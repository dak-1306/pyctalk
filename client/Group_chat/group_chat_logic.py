from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem
from PyQt6 import QtCore
import re
import asyncio


class GroupChatLogic:
    """Async logic cho GroupChatWindow (toàn bộ xử lý đã gom về đây)"""

    def __init__(self, ui, api_client, user_id, username):
        self.ui = ui
        self.api_client = api_client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.message_offset = 0
        self.loading_lock = asyncio.Lock()  # Prevent concurrent loading
        self._realtime_connected = False

        # Debug log để kiểm tra thông tin user
        print(f"[DEBUG] GroupChatLogic init: user_id={user_id}, username='{username}'")

        # Kết nối tín hiệu từ UI
        self.ui.group_selected.connect(self.handle_group_selected)
        self.ui.message_send_requested.connect(self.send_message)
        
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
    async def handle_group_selected(self, item):
        """Xử lý khi UI chọn 1 nhóm"""
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        print(f"[GroupChatLogic] Chuyển sang nhóm: {group_data.get('group_name')} (ID: {group_data.get('group_id')})")
        await self.select_group(group_data)

    async def select_group(self, group_data):
        self.current_group = group_data
        self.message_offset = 0
        self.ui.update_group_info(group_data)
        await self.load_group_messages()

    # ---------------------------
    # Tải tin nhắn nhóm
    # ---------------------------
    async def load_group_messages(self, offset=0, limit=50):
        async with self.loading_lock:  # Prevent concurrent loading
            if not self.current_group:
                print("[GroupChatLogic] current_group is None, abort load_group_messages")
                return
            response = await self.api_client.get_group_messages(
                self.current_group["group_id"], self.user_id, limit, offset
            )
            if not response:
                QMessageBox.critical(self.ui, "Lỗi", "Không nhận được phản hồi từ server!")
                return
            if response.get("success"):
                messages = response.get("messages", [])
                print(f"[DEBUG] load_group_messages: Loaded {len(messages)} messages for group_id={self.current_group['group_id']}")
                print(f"[DEBUG] load_group_messages: First few messages: {messages[:3] if messages else 'None'}")
                self.display_messages(messages, offset, self.username)
            else:
                print(f"[GroupChatLogic][ERROR] Không thể tải tin nhắn: {response.get('message')}")
                QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải tin nhắn"))    # ---------------------------
    # Hiển thị tin nhắn
    # ---------------------------
    def display_messages(self, messages, offset, username):
        try:
            if offset == 0:
                self.ui.clear_messages()
            
            # Theo dõi người gửi tin nhắn trước đó để quyết định có hiển thị tên không
            previous_sender = None
            
            for i, msg in enumerate(messages):
                sender = msg.get('sender_name', 'Unknown')
                time_str = msg.get("time_send", "Unknown")
                content = msg.get('content', '')
                # Fix case-insensitive comparison
                is_sent = sender.lower() == username.lower()
                
                # Quyết định có hiển thị tên người gửi không
                show_sender_name = False
                if not is_sent:  # Chỉ hiển thị tên cho tin nhắn của người khác
                    # Hiển thị tên nếu:
                    # 1. Là tin nhắn đầu tiên, hoặc
                    # 2. Người gửi khác với tin nhắn trước đó
                    if previous_sender is None or previous_sender.lower() != sender.lower():
                        show_sender_name = True
                
                # Debug log để kiểm tra logic
                print(f"[DEBUG] display_messages: sender='{sender}', username='{username}', is_sent={is_sent}, show_sender_name={show_sender_name}, content='{content[:30]}...'")
                
                self.ui.add_message(content, is_sent, time_str, sender, show_sender_name)
                
                # Cập nhật người gửi trước đó
                previous_sender = sender
                
        except (RuntimeError, AttributeError) as e:
            # Handle UI widget deletion or attribute errors
            print(f"Warning: UI display error in display_messages: {e}")
            # Try alternative display method
            if hasattr(self.ui, 'messages'):
                self.ui.messages.extend([
                    {
                        'content': msg.get('content', ''),
                        'is_sent': msg.get('sender_name', '').lower() == username.lower(),
                        'timestamp': msg.get('time_send', '')
                    } for msg in messages
                ])

    # ---------------------------
    # Gửi tin nhắn
    # ---------------------------
    async def send_message(self, content: str):
        if not self.current_group:
            QMessageBox.warning(self.ui, "Lỗi", "Vui lòng chọn nhóm trước")
            return
        if not content.strip():
            return

        response = await self.api_client.send_group_message(
            self.user_id, self.current_group["group_id"], content.strip()
        )
        if response and response.get("success"):
            await self.load_group_messages(offset=0)
        else:
            QMessageBox.warning(self.ui, "Lỗi", "Không thể gửi tin nhắn")

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
