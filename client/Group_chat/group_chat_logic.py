from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem
from PyQt6 import QtCore
import re
import asyncio
import os


class GroupChatLogic:
    """Async logic cho GroupChatWindow với lazy loading"""

    def __init__(self, ui, api_client, user_id, username):
        self.ui = ui
        self.api_client = api_client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.message_offset = 0
        self.loading_lock = asyncio.Lock()  # Prevent concurrent loading
        self._realtime_connected = False
        
        # Lazy loading settings
        self.messages_per_load = 20  # Tải 20 tin nhắn mỗi lần thay vì 50
        self.total_messages_loaded = 0
        self.has_more_messages = True
        self.is_loading_more = False

        # Debug log để kiểm tra thông tin user
        print(f"[DEBUG] GroupChatLogic init: user_id={user_id}, username='{username}'")

        # Kết nối tín hiệu từ UI với wrapper sync function
        self.ui.group_selected.connect(self._handle_group_selected_sync)
        self.ui.message_send_requested.connect(self.send_message)
        
        # Connect file send signal if available
        if hasattr(self.ui, 'file_send_requested'):
            self.ui.file_send_requested.connect(
                lambda file_data: asyncio.create_task(self.send_file_message(file_data))
            )
        
        # Connect real-time group message signals
        self._connect_realtime_signals()
        
    def _connect_realtime_signals(self):
        """Connect real-time group message signals from server"""
        if not self._realtime_connected and hasattr(self.api_client, 'connection'):
            try:
                # Connect to new group message signal
                self.api_client.connection.new_group_message_received.connect(self._on_realtime_group_message)
                self._realtime_connected = True
                print(f"[DEBUG][GroupChatLogic] Real-time signals connected for user_id={self.user_id}")
            except Exception as e:
                print(f"[ERROR][GroupChatLogic] Failed to connect real-time signals: {e}")
    
    def _on_realtime_group_message(self, message_data):
        """Handle real-time group message from server"""
        try:
            print(f"[DEBUG][GroupChatLogic] Real-time group message received: {message_data}")
            
            # Check if message is for current group
            group_id = str(message_data.get('group_id', ''))
            current_group_id = str(self.current_group.get('group_id', '')) if self.current_group else ''
            
            if group_id == current_group_id:
                # Check if message is from another user (not current user)
                sender_id = str(message_data.get('user_id', ''))
                current_user_id = str(self.user_id)
                
                if sender_id != current_user_id:
                    # Add message to UI immediately
                    content = message_data.get('message', '')
                    timestamp = message_data.get('timestamp', '')
                    sender_name = message_data.get('username', 'Unknown')
                    
                    print(f"[DEBUG][GroupChatLogic] Adding real-time group message to UI: {content}")
                    
                    # Add to UI as message from another user (show sender name in group)
                    self.ui.add_message(content, False, timestamp, sender_name, show_sender_name=True)
                else:
                    print(f"[DEBUG][GroupChatLogic] Ignoring own message from real-time: {content}")
            else:
                print(f"[DEBUG][GroupChatLogic] Message not for current group: group_id={group_id}, current={current_group_id}")
                
        except Exception as e:
            print(f"[ERROR][GroupChatLogic] Failed to handle real-time group message: {e}")
            import traceback
            traceback.print_exc()

    # ---------------------------
    # Load danh sách nhóm
    # ---------------------------
    async def load_user_groups(self):
        print("[GroupChatLogic] Đang tải danh sách nhóm...")
        response = await self.api_client.get_user_groups(self.user_id)
        if not response:
            QMessageBox.critical(self.ui, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            self.ui.groups_list.clear()
            for idx, group in enumerate(response.get("groups", [])):
                try:
                    item_text = f"{group['group_name']} (ID: {group['group_id']})"
                    item = QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, group)
                    self.ui.groups_list.addItem(item)
                except Exception as e:
                    print(f"[GroupChatLogic][ERROR] Lỗi khi tạo item cho group #{idx}: {e}")
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải danh sách nhóm"))

    # ---------------------------
    # Chọn nhóm
    # ---------------------------
    def _handle_group_selected_sync(self, item):
        """Sync wrapper for async handle_group_selected"""
        import asyncio
        asyncio.create_task(self.handle_group_selected(item))
    
    async def handle_group_selected(self, item):
        """Xử lý khi UI chọn 1 nhóm"""
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        print(f"[GroupChatLogic] Chuyển sang nhóm: {group_data.get('group_name')} (ID: {group_data.get('group_id')})")
        await self.select_group(group_data)

    async def select_group(self, group_data):
        """Select group và reset trạng thái lazy loading"""
        self.current_group = group_data
        self.message_offset = 0
        self.total_messages_loaded = 0
        self.has_more_messages = True
        self.is_loading_more = False
        
        self.ui.update_group_info(group_data)
        
        # Clear messages trước và load initial batch
        self.ui.clear_messages()
        await self.load_initial_messages()

    # ---------------------------
    # Lazy Loading tin nhắn nhóm
    # ---------------------------
    async def load_initial_messages(self):
        """Load tin nhắn ban đầu (ít nhất để không trống màn hình)"""
        if not self.current_group:
            print("[GroupChatLogic] current_group is None, abort load_initial_messages")
            return
            
        print(f"[DEBUG] Loading initial {self.messages_per_load} messages...")
        await self.load_group_messages(offset=0, limit=self.messages_per_load, is_initial=True)

    async def load_more_messages(self):
        """Load thêm tin nhắn cũ hơn khi user cuộn lên"""
        if not self.has_more_messages or self.is_loading_more:
            return
            
        print(f"[DEBUG] Loading more messages, offset={self.total_messages_loaded}")
        await self.load_group_messages(
            offset=self.total_messages_loaded, 
            limit=self.messages_per_load, 
            is_initial=False
        )

    # ---------------------------
    # Tải tin nhắn nhóm
    # ---------------------------
    async def load_group_messages(self, offset=0, limit=20, is_initial=True):
        """Load tin nhắn với lazy loading support"""
        async with self.loading_lock:  # Prevent concurrent loading
            if not self.current_group:
                print("[GroupChatLogic] current_group is None, abort load_group_messages")
                return
                
            if not is_initial:
                self.is_loading_more = True
                
            response = await self.api_client.get_group_messages(
                self.current_group["group_id"], self.user_id, limit, offset
            )
            
            if not is_initial:
                self.is_loading_more = False
                
            if not response:
                print("[GroupChatLogic] No response from server!")
                return
                
            if response.get("success"):
                messages = response.get("messages", [])
                print(f"[DEBUG] load_group_messages: Loaded {len(messages)} messages for group_id={self.current_group['group_id']}, offset={offset}")
                
                # Cập nhật trạng thái
                if len(messages) < limit:
                    self.has_more_messages = False
                    print("[DEBUG] No more messages to load")
                
                if len(messages) > 0:
                    self.total_messages_loaded += len(messages)
                    self.display_messages(messages, offset, self.username, is_initial)
                else:
                    print("[DEBUG] No messages returned")
            else:
                print(f"[GroupChatLogic][ERROR] Không thể tải tin nhắn: {response.get('message')}")
                error_msg = response.get('message', '')
                if 'không phải thành viên' in error_msg:
                    print(f"[GroupChatLogic][INFO] User no longer in group, stopping message loading")
                    return    # ---------------------------
    # Hiển thị tin nhắn
    # ---------------------------
    def display_messages(self, messages, offset, username, is_initial=True):
        """Hiển thị tin nhắn với hỗ trợ lazy loading và smooth animation"""
        try:
            # Không clear messages nếu đang load more (prepend vào đầu)
            if not is_initial and offset > 0:
                # Prepend messages vào đầu danh sách với animation
                print(f"[DEBUG] Prepending {len(messages)} older messages with animation")
                asyncio.create_task(self._animate_prepend_messages(messages, username))
            else:
                # Load initial hoặc refresh - clear và load từ đầu
                if is_initial:
                    self.ui.clear_messages()
                
                # Animate initial messages loading
                asyncio.create_task(self._animate_initial_messages(messages, username))
                
        except (RuntimeError, AttributeError) as e:
            # Handle UI widget deletion or attribute errors
            print(f"Warning: UI display error in display_messages: {e}")
            # Try alternative display method
            if hasattr(self.ui, 'messages'):
                self.ui.messages.extend([
                    {
                        'content': msg.get('content', ''),
                        'is_sent': msg.get('sender_name', '').lower() == username.lower(),
                        'timestamp': msg.get("time_send", "Unknown"),
                        'sender': msg.get('sender_name', 'Unknown')
                    } for msg in messages
                ])
    
    async def _animate_initial_messages(self, messages, username):
        """Animate initial messages loading với batch và delay"""
        previous_sender = None
        batch_size = 5  # Load 5 messages at a time
        delay_between_batches = 50  # 50ms delay between batches
        
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            
            for msg in batch:
                sender = msg.get('sender_name', 'Unknown')
                time_str = msg.get("time_send", "Unknown")
                content = msg.get('content', '')
                is_sent = sender.lower() == username.lower()
                
                # Logic hiển thị tên người gửi
                show_sender_name = False
                if not is_sent:
                    if previous_sender is None or previous_sender.lower() != sender.lower():
                        show_sender_name = True
                
                # Add message to UI
                self.ui.add_message(content, is_sent, time_str, sender, show_sender_name)
                previous_sender = sender
            
            # Small delay between batches for smooth effect
            if i + batch_size < len(messages):
                await asyncio.sleep(delay_between_batches / 1000.0)
    
    async def _animate_prepend_messages(self, messages, username):
        """Animate prepending older messages"""
        self.ui.prepend_messages(messages, username)

    # ---------------------------
    # Gửi tin nhắn
    # ---------------------------
    async def send_message(self, content: str):
        """Gửi tin nhắn và refresh danh sách"""
        if not self.current_group:
            QMessageBox.warning(self.ui, "Lỗi", "Vui lòng chọn nhóm trước")
            return
        if not content.strip():
            return

        response = await self.api_client.send_group_message(
            self.user_id, self.current_group["group_id"], content.strip()
        )
        if response and response.get("success"):
            # Reset lazy loading state và reload từ đầu
            self.total_messages_loaded = 0
            self.has_more_messages = True
            self.is_loading_more = False
            await self.load_initial_messages()
        else:
            QMessageBox.warning(self.ui, "Lỗi", "Không thể gửi tin nhắn")

    async def send_file_message(self, file_data):
        """Send file message with optional caption"""
        try:
            print(f"[DEBUG][GroupChatLogic] send_file_message called: file_data={file_data}")

            if not self.current_group:
                QMessageBox.warning(self.ui, "Lỗi", "Vui lòng chọn nhóm trước")
                return

            file_path = file_data.get('file_path')
            file_type = file_data.get('file_type')
            caption = file_data.get('caption', '')

            if not file_path or not os.path.exists(file_path):
                print(f"[ERROR][GroupChatLogic] File not found: {file_path}")
                QMessageBox.warning(self.ui, "Lỗi", "File không tồn tại")
                return

            # Upload file and get metadata
            try:
                # For now, use fallback: send as text with file info
                file_name = os.path.basename(file_path)
                file_info = f"📎 Sent file: {file_name}"
                if caption:
                    file_info += f"\n{caption}"

                resp = await asyncio.wait_for(
                    self.api_client.send_group_message(
                        self.user_id,
                        self.current_group["group_id"],
                        file_info
                    ),
                    timeout=10.0
                )

                if resp and resp.get("success"):
                    # Reset lazy loading state và reload từ đầu
                    self.total_messages_loaded = 0
                    self.has_more_messages = True
                    self.is_loading_more = False
                    await self.load_initial_messages()
                    print(f"[DEBUG][GroupChatLogic] File message sent successfully")
                else:
                    error_msg = resp.get("message", "Không thể gửi file") if resp else "Không có phản hồi từ server"
                    print(f"[DEBUG][GroupChatLogic] Failed to send file message: {error_msg}")
                    QMessageBox.warning(self.ui, "Lỗi", error_msg)

            except Exception as e:
                print(f"[ERROR][GroupChatLogic] Failed to upload/send file: {e}")
                QMessageBox.warning(self.ui, "Lỗi", f"Không thể gửi file: {str(e)}")

        except Exception as e:
            print(f"[ERROR][GroupChatLogic] send_file_message error: {e}")
            QMessageBox.warning(self.ui, "Lỗi", f"Lỗi khi gửi file: {str(e)}")

    # ---------------------------
    # Quản lý nhóm
    # ---------------------------
    async def create_new_group(self):
        group_name, ok = QInputDialog.getText(self.ui, "Tạo nhóm mới", "Tên nhóm:")
        if not ok or not group_name.strip():
            return
        response = await self.api_client.create_group(group_name.strip(), self.user_id)
        if response and response.get("success"):
            QMessageBox.information(self.ui, "Thành công", f"Đã tạo nhóm '{group_name}' thành công!")
            await self.load_user_groups()
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tạo nhóm"))

    async def add_member(self):
        if not self.current_group:
            return
        response = await self.api_client.get_friends(self.user_id)
        friends = response.get("friends", []) if response and response.get("success") else []
        if not friends:
            QMessageBox.warning(self.ui, "Lỗi", "Không có bạn bè để thêm")
            return

        friend_names = [f"{f['username']} (ID: {f['user_id']})" for f in friends]
        selected, ok = QInputDialog.getItem(self.ui, "Thêm thành viên", "Chọn bạn để thêm:", friend_names, 0, False)
        if not ok or not selected:
            return

        match = re.search(r'ID: (\d+)', selected)
        if not match:
            return
        add_user_id = int(match.group(1))

        response = await self.api_client.add_member_to_group(
            self.current_group["group_id"], add_user_id, self.user_id
        )
        if response and response.get("success"):
            QMessageBox.information(self.ui, "Thành công", "Đã thêm thành viên thành công!")
            await self.view_members()
        else:
            QMessageBox.critical(self.ui, "Lỗi", response.get("message", "Không thể thêm thành viên"))

    async def view_members(self):
        if not self.current_group:
            return
        response = await self.api_client.get_group_members(self.current_group["group_id"], self.user_id)
        if response and response.get("success"):
            members_text = "Thành viên nhóm:\n\n"
            for m in response.get("members", []):
                members_text += f"• {m['username']} (ID: {m['user_id']})\n"
            QMessageBox.information(self.ui, f"Thành viên nhóm {self.current_group['group_name']}", members_text)
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải danh sách thành viên"))
