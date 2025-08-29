import logging
import asyncio
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QTimer

# Giữ nguyên import API + Logic như bản cũ
from client.Group_chat.group_api_client import GroupAPIClient
from client.Group_chat.group_chat_logic import GroupChatLogic

# Import MessageBubble và TimeFormatter
from client.UI.messenger_ui.message_bubble_widget import MessageBubble
from client.UI.messenger_ui.time_formatter import TimeFormatter

logger = logging.getLogger(__name__)

class EmbeddedGroupChatWidget(QtWidgets.QWidget):
    # Signals should be declared at class level
    message_send_requested = QtCore.pyqtSignal(str)
    group_selected = QtCore.pyqtSignal(dict)

    def __init__(self, client, user_id, username, group_data):
        super().__init__()
        # --- giữ logic cũ ---
        self.api_client = GroupAPIClient(client)
        self.logic = GroupChatLogic(self, self.api_client, user_id, username)
        self.user_id = user_id
        self.username = username
        self.group_data = group_data

        # Track previous message for timestamp logic (group chat)
        self.last_message_time = None
        self.last_message_sender = None
        self.message_count = 0
        self.time_formatter = TimeFormatter()

        self._setupUI()
        
        # Set overall widget styling
        self.setStyleSheet("""
            EmbeddedGroupChatWidget {
                background-color: #ffffff;
                border: none;
            }
        """)

        # Thiết lập nhóm hiện tại và load tin nhắn với lazy loading
        self.logic.current_group = group_data
        asyncio.create_task(self.logic.load_initial_messages())
        
        # Load thông tin thành viên nhóm
        asyncio.create_task(self.load_group_members())
        
        # Setup scroll loading detection
        self._setup_scroll_loading()

    def showEvent(self, event):
        """Reload tin nhắn khi widget được hiển thị lại (quay lại nhóm)"""
        super().showEvent(event)
        logger.info("[EmbeddedGroupChatWidget] showEvent triggered - reload group messages")
        try:
            if getattr(self.logic, "current_group", None):
                import asyncio
                # Check if user is still a member before loading messages
                asyncio.create_task(self._check_membership_and_load())
        except Exception as e:
            logger.error(f"[EmbeddedGroupChatWidget] Lỗi reload tin nhắn: {e}")

    async def _check_membership_and_load(self):
        """Check if user is still a group member before loading data"""
        try:
            # First check group members
            response = await self.api_client.get_group_members(
                str(self.group_data.get('group_id')),
                str(self.user_id)
            )
            
            if response and response.get("status") == "ok":
                members = response.get("members", [])
                # Check if current user is in the members list
                user_in_group = any(int(member["user_id"]) == int(self.user_id) for member in members)
                
                if user_in_group:
                    # User is still in group, load with lazy loading
                    await self.logic.load_initial_messages()
                    await self.load_group_members()
                else:
                    print(f"[DEBUG] User {self.user_id} no longer in group {self.group_data.get('group_id')}")
                    # Clear messages and show info
                    self.clear_messages()
            else:
                print(f"[DEBUG] Failed to check group membership: {response}")
        except Exception as e:
            print(f"[ERROR] _check_membership_and_load: {e}")

    def add_message(self, message, is_sent, timestamp=None, sender_name=None, show_sender_name=False):
        """Thêm một message bubble vào UI với timestamp logic giống Messenger"""
        
        # Increment message counter
        self.message_count += 1
        is_first_message = self.message_count == 1
        
        # Determine sender for comparison
        current_sender = sender_name if sender_name else ("You" if is_sent else "Unknown")
        
        # Check if we should show timestamp using TimeFormatter
        show_timestamp = False
        if timestamp:
            show_timestamp = self.time_formatter.should_show_timestamp(
                timestamp, 
                self.last_message_time, 
                current_sender, 
                self.last_message_sender,
                is_first_message
            )
        
        # Format timestamp for display
        formatted_timestamp = None
        if timestamp and show_timestamp:
            formatted_timestamp = self.time_formatter.format_message_time(timestamp)
        
        print(f"[DEBUG][GroupChat] add_message: message={message}, sender={current_sender}, show_timestamp={show_timestamp}, formatted_time={formatted_timestamp}")
        
        # Create message bubble with timestamp logic
        bubble = MessageBubble(
            message, 
            is_sent, 
            formatted_timestamp if show_timestamp else None, 
            sender_name, 
            show_sender_name,
            show_timestamp
        )
        
        # Update tracking variables
        if timestamp:
            self.last_message_time = timestamp
        self.last_message_sender = current_sender
        
        # Connect signals
        bubble.sender_clicked.connect(self._handle_sender_clicked)
        bubble.timestamp_clicked.connect(self._handle_timestamp_clicked)
        
        # Remove the stretch item temporarily
        layout_count = self.messages_layout.count()
        stretch_item = None
        if layout_count > 0:
            last_item = self.messages_layout.itemAt(layout_count - 1)
            if last_item and last_item.spacerItem():
                stretch_item = self.messages_layout.takeAt(layout_count - 1)
        
        # Add the message bubble với fade-in animation
        self.messages_layout.addWidget(bubble)
        
        # Add fade-in animation
        self._animate_message_bubble(bubble)
        
        # Re-add the stretch item
        if stretch_item:
            self.messages_layout.addItem(stretch_item)
        else:
            self.messages_layout.addStretch()
        
        # Update layout
        self.messages_widget.updateGeometry()
        self.messages_layout.update()
        
        self._scroll_to_bottom()

    def clear_messages(self):
        """Xóa toàn bộ message bubbles khỏi UI và reset timestamp tracking"""
        self._clear_message_bubbles()
        
        # Reset timestamp tracking variables
        self.last_message_time = None
        self.last_message_sender = None
        self.message_count = 0

    def _setupUI(self):
        """Tạo UI layout với styling hiện đại như Zalo"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Hiển thị tên nhóm với button quản lý - Header Bar
        group_header_layout = QtWidgets.QHBoxLayout()
        group_header_layout.setContentsMargins(16, 12, 16, 12)
        
        self.group_info_label = QtWidgets.QLabel()
        self.group_info_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 16px;
                color: #1a1a1a;
                padding: 0px;
            }
        """)
        self.update_group_info()
        group_header_layout.addWidget(self.group_info_label)
        
        # Button quản lý nhóm
        self.manage_group_btn = QtWidgets.QPushButton("⚙️ Quản lý")
        self.manage_group_btn.setMaximumWidth(100)
        self.manage_group_btn.setStyleSheet("""
            QPushButton {
                background-color: #0084FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0073E6;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #005CBF;
                transform: translateY(0px);
            }
        """)
        self.manage_group_btn.clicked.connect(self.open_group_management)
        group_header_layout.addWidget(self.manage_group_btn)
        
        group_header_widget = QtWidgets.QWidget()
        group_header_widget.setLayout(group_header_layout)
        group_header_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-bottom: 1px solid #e4e6ea;
            }
        """)
        layout.addWidget(group_header_widget)

        # Hiển thị thông tin thành viên
        self.members_info_label = QtWidgets.QLabel()
        self.members_info_label.setStyleSheet("""
            QLabel {
                color: #65676b; 
                padding: 8px 16px; 
                font-size: 12px; 
                background-color: #f7f8fa;
                border-bottom: 1px solid #e4e6ea;
                margin: 0px;
            }
        """)
        self.members_info_label.setText("Đang tải thông tin thành viên...")
        self.members_info_label.setWordWrap(True)
        layout.addWidget(self.members_info_label)

        # Khu vực tin nhắn: ScrollArea với styling đẹp
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #f7f8fa;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c4c4c4;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.messages_widget = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(16, 12, 16, 12)
        self.messages_layout.setSpacing(4)  # Spacing nhỏ hơn cho bubble gần nhau
        # Stretch để các bubble dồn lên trên, chừa chỗ cuối
        self.messages_layout.addStretch()
        
        # Subtle loading bar thay vì popup
        self.loading_bar = QtWidgets.QProgressBar()
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
                text-align: center;
                height: 2px;
                border-radius: 1px;
                margin: 0px;
            }
            QProgressBar::chunk {
                background-color: #0084ff;
                border-radius: 1px;
            }
        """)
        self.loading_bar.setRange(0, 0)  # Indeterminate progress
        self.loading_bar.hide()
        
        # Container cho loading bar ở top
        loading_container = QtWidgets.QWidget()
        loading_container.setFixedHeight(4)
        loading_layout = QtWidgets.QVBoxLayout(loading_container)
        loading_layout.setContentsMargins(0, 0, 0, 0)
        loading_layout.addWidget(self.loading_bar)
        
        # Thêm loading bar vào đầu layout
        self.messages_layout.insertWidget(0, loading_container)

        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area, stretch=1)

        # Input gửi tin - Modern design
        input_container = QtWidgets.QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-top: 1px solid #e4e6ea;
                padding: 0px;
            }
        """)
        
        input_layout = QtWidgets.QHBoxLayout(input_container)
        input_layout.setContentsMargins(16, 12, 16, 12)
        input_layout.setSpacing(12)

        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Nhập tin nhắn...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #f7f8fa;
                border: 1px solid #e4e6ea;
                border-radius: 20px;
                padding: 10px 16px;
                font-size: 14px;
                color: #1a1a1a;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #0084FF;
                background-color: #ffffff;
            }
            QLineEdit::placeholder {
                color: #8a8d91;
            }
        """)
        self.message_input.returnPressed.connect(self._on_send_message)
        
        # Connect text changed để hiển thị typing indicator
        self.message_input.textChanged.connect(self._on_text_changed)

        self.send_button = QtWidgets.QPushButton("➤")
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0084FF;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0073E6;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #005CBF;
                transform: scale(0.95);
            }
            QPushButton:disabled {
                background-color: #bcc0c4;
            }
        """)
        self.send_button.clicked.connect(self._on_send_message)

        input_layout.addWidget(self.message_input, stretch=1)
        input_layout.addWidget(self.send_button)
        layout.addWidget(input_container)
    
    def _setup_scroll_loading(self):
        """Setup scroll detection để load thêm tin nhắn cũ"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.valueChanged.connect(self._on_scroll_changed)
        
    def _on_scroll_changed(self, value):
        """Detect scroll lên đầu để load thêm tin nhắn cũ"""
        scrollbar = self.scroll_area.verticalScrollBar()
        
        # Nếu scroll gần đầu (trong 50 pixels) và còn tin nhắn để load
        if value <= 50 and hasattr(self.logic, 'has_more_messages') and self.logic.has_more_messages:
            if not hasattr(self.logic, 'is_loading_more') or not self.logic.is_loading_more:
                print("[DEBUG] Near top of scroll, loading more messages...")
                self.show_loading_indicator()
                asyncio.create_task(self._load_more_with_indicator())
    
    async def _load_more_with_indicator(self):
        """Load more messages với loading bar"""
        try:
            await self.logic.load_more_messages()
        finally:
            self.hide_loading_indicator()
    
    def show_loading_indicator(self):
        """Hiển thị loading bar"""
        if hasattr(self, 'loading_bar'):
            self.loading_bar.show()
    
    def _animate_message_bubble(self, bubble):
        """Add smooth fade-in animation to message bubble"""
        try:
            # Ensure bubble is visible first
            bubble.setVisible(True)
            bubble.show()
            
            # Skip animation for now to fix visibility issues
            print(f"[DEBUG] Message bubble animated and visible: {bubble.isVisible()}")
            
        except Exception as e:
            print(f"[DEBUG] Animation error (fallback to instant): {e}")
            # Fallback - just show bubble instantly
            bubble.setVisible(True)
            bubble.show()

    def hide_loading_indicator(self):
        """Ẩn loading bar"""
        if hasattr(self, 'loading_bar'):
            self.loading_bar.hide()

    def prepend_messages(self, messages, username):
        """Thêm tin nhắn cũ vào đầu danh sách (cho lazy loading)"""
        if not messages:
            return
            
        # Lưu scroll position hiện tại
        scrollbar = self.scroll_area.verticalScrollBar()
        old_value = scrollbar.value()
        old_max = scrollbar.maximum()
        
        # Thêm tin nhắn vào đầu (reverse order vì server trả về DESC)
        for msg in reversed(messages):
            sender = msg.get('sender_name', 'Unknown')
            time_str = msg.get("time_send", "Unknown")
            content = msg.get('content', '')
            is_sent = sender.lower() == username.lower()
            
            # Tạo bubble và thêm vào đầu layout (sau header nhưng trước tin nhắn hiện tại)
            bubble = MessageBubble(
                content, 
                is_sent=is_sent, 
                timestamp=time_str, 
                sender_name=sender, 
                show_sender_name=(not is_sent), 
                show_timestamp=False
            )
            
            # Insert vào vị trí 0 (ngay sau stretch đầu tiên)
            self.messages_layout.insertWidget(1, bubble)
            
        # Điều chỉnh scroll để giữ vị trí tương đối
        QTimer.singleShot(100, lambda: self._adjust_scroll_after_prepend(old_value, old_max))
        
    def _adjust_scroll_after_prepend(self, old_value, old_max):
        """Điều chỉnh scroll position sau khi prepend tin nhắn"""
        scrollbar = self.scroll_area.verticalScrollBar()
        new_max = scrollbar.maximum()
        
        # Tính toán vị trí mới để giữ tin nhắn hiện tại ở cùng vị trí
        if old_max > 0:
            ratio = old_value / old_max
            new_value = int(ratio * new_max)
            scrollbar.setValue(new_value)
        else:
            # Nếu không có scroll trước đó, scroll xuống một chút để không ở đầu
            scrollbar.setValue(100)

    def _on_text_changed(self):
        """Handle typing indicator"""
        text = self.message_input.text()
        # Enable/disable send button based on text content
        self.send_button.setEnabled(bool(text.strip()))
        
        # Update send button style
        if text.strip():
            self.send_button.setStyleSheet("""
                QPushButton {
                    background-color: #0084FF;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0073E6;
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background-color: #005CBF;
                    transform: scale(0.95);
                }
            """)
        else:
            self.send_button.setStyleSheet("""
                QPushButton {
                    background-color: #bcc0c4;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)

    def update_group_info(self):
        """Cập nhật thông tin nhóm hiển thị"""
        if self.group_data:
            group_name = self.group_data.get("group_name", "Unknown Group")
            group_id = self.group_data.get("group_id", "?")
            self.group_info_label.setText(f"Nhóm: {group_name} (ID: {group_id})")

    def _on_send_message(self):
        """Xử lý gửi tin nhắn"""
        content = self.message_input.text().strip()
        if content:
            asyncio.create_task(self._send_message_async(content))

    async def _send_message_async(self, content):
        """Gửi tin nhắn async (giữ nguyên logic cũ)"""
        print(f"[DEBUG] Sending group message: user_id={self.user_id}, group_id={self.group_data['group_id']}, content='{content}'")
        
        # Giữ nguyên việc dùng self.group_data["group_id"] như bản cũ
        response = await self.api_client.send_group_message(
            self.user_id, self.group_data["group_id"], content
        )
        
        print(f"[DEBUG] Send group message response: {response}")

        if response and response.get("success"):
            # Clear input với animation
            self.message_input.clear()
            
            # Hiệu ứng feedback khi gửi thành công
            self.send_button.setText("✓")
            QTimer.singleShot(500, lambda: self.send_button.setText("➤"))
            
            print(f"[DEBUG] Message sent successfully, reloading with lazy loading")
            # Reset lazy loading và load lại từ đầu
            self.logic.total_messages_loaded = 0
            self.logic.has_more_messages = True
            self.logic.is_loading_more = False
            await self.logic.load_initial_messages()
        else:
            error_msg = response.get("message", "Không thể gửi tin nhắn") if response else "Không có phản hồi từ server"
            print(f"[DEBUG] Failed to send message: {error_msg}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", error_msg)

    def _add_message_bubble(self, message, is_sent, timestamp=None):
        """Helper method for adding message bubbles"""
        bubble = MessageBubble(message, is_sent=is_sent, timestamp=timestamp)
        # Chèn trước stretch ở cuối
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

    def _clear_message_bubbles(self):
        """Clear all message bubbles from layout"""
        try:
            if self.messages_layout and not self.messages_layout.isEmpty():
                while self.messages_layout.count() > 1:
                    item = self.messages_layout.takeAt(0)
                    if item:
                        w = item.widget()
                        if w:
                            w.deleteLater()
        except RuntimeError as e:
            # Layout đã bị delete, ignore error
            pass

    def _scroll_to_bottom(self):
        """Cuộn xuống cuối với hiệu ứng mượt mà"""
        if self.scroll_area:
            # Scroll animation cho mượt mà
            scrollbar = self.scroll_area.verticalScrollBar()
            
            # Tạo animation cho scroll
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
            
            if hasattr(self, '_scroll_animation'):
                self._scroll_animation.stop()
            
            self._scroll_animation = QPropertyAnimation(scrollbar, b"value")
            self._scroll_animation.setDuration(150)  # 150ms animation
            self._scroll_animation.setEasingCurve(QEasingCurve.Type.OutQuart)
            self._scroll_animation.setStartValue(scrollbar.value())
            self._scroll_animation.setEndValue(scrollbar.maximum())
            self._scroll_animation.start()
            
            # Fallback nếu animation không hoạt động
            QTimer.singleShot(200, lambda: scrollbar.setValue(scrollbar.maximum()))

    async def load_group_members(self):
        """Load và hiển thị thông tin thành viên nhóm"""
        try:
            group_id = self.group_data.get("group_id")
            if not group_id:
                self.members_info_label.setText("Không thể lấy thông tin nhóm")
                return
                
            print(f"[DEBUG] Loading members for group_id={group_id}")
            
            # Gọi API để lấy thành viên
            response = await self.api_client.get_group_members(str(group_id), str(self.user_id))
            
            print(f"[DEBUG] Load members response: {response}")
            
            if response and response.get("status") == "ok":  # Sửa từ "success" thành "status" == "ok"
                members = response.get("members", [])
                member_count = len(members)
                
                print(f"[DEBUG] Found {member_count} members: {members}")
                
                # Store members data for later use
                self.logic.group_members = members
                
                # Tạo danh sách tên thành viên
                member_names = [member.get("username", "Unknown") for member in members]
                
                # Tạo tooltip với danh sách đầy đủ
                tooltip_text = "Danh sách thành viên:\n" + "\n".join([f"• {name}" for name in member_names])
                self.members_info_label.setToolTip(tooltip_text)
                
                # Hiển thị thông tin
                if member_count > 0:
                    if member_count <= 5:
                        # Hiển thị tất cả tên nếu ít người
                        names_text = ", ".join(member_names)
                        self.members_info_label.setText(f"👥 {member_count} thành viên: {names_text}")
                    else:
                        # Hiển thị một số tên đầu + "và X người khác"
                        first_names = ", ".join(member_names[:3])
                        remaining = member_count - 3
                        self.members_info_label.setText(f"👥 {member_count} thành viên: {first_names} và {remaining} người khác")
                else:
                    self.members_info_label.setText("👥 Không có thành viên")
                    self.members_info_label.setToolTip("Không có thành viên nào trong nhóm này")
            else:
                error_msg = response.get("message", "Lỗi không xác định") if response else "Không có phản hồi từ server"
                print(f"[DEBUG] Load members failed: {error_msg}")
                self.members_info_label.setText(f"❌ Lỗi: {error_msg}")
                
        except Exception as e:
            logger.error(f"[EmbeddedGroupChatWidget] Lỗi load thành viên: {e}")
            self.members_info_label.setText("❌ Lỗi tải thông tin thành viên")

    def _handle_sender_clicked(self, sender_name):
        """Handle when user clicks on sender name"""
        print(f"[DEBUG] Sender clicked: {sender_name}")
        
        # Find user_id for the sender_name
        user_data = {
            'username': sender_name,
            'friend_name': sender_name
        }
        
        # Try to get user_id from group members
        try:
            # Search in loaded group members if available
            if hasattr(self.logic, 'group_members') and self.logic.group_members:
                print(f"[DEBUG] Found {len(self.logic.group_members)} group members")
                for member in self.logic.group_members:
                    print(f"[DEBUG] Member: {member}")
                    if member.get('username') == sender_name:
                        user_data['user_id'] = member.get('user_id')
                        user_data['friend_id'] = member.get('user_id')
                        print(f"[DEBUG] Found user_id: {user_data['user_id']} for {sender_name}")
                        break
            else:
                print(f"[DEBUG] No group members found or logic doesn't have group_members")
        except Exception as e:
            print(f"[DEBUG] Error finding user_id: {e}")
        
        print(f"[DEBUG] Final user_data: {user_data}")
        self._show_user_profile(user_data)

    def open_group_management(self):
        """Mở dialog quản lý nhóm"""
        from client.UI.messenger_ui.group_management_dialog import GroupManagementDialog
        
        dialog = GroupManagementDialog(
            group_data=self.group_data,
            current_user_id=self.user_id,
            username=self.username,
            client=self.api_client,  # Truyền api_client thay vì connection
            parent=self
        )
        
        # Refresh group members when dialog closes
        result = dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            # User left the group, emit signal to refresh group list
            self.group_selected.emit({"action": "user_left_group", "group_id": self.group_data.get('group_id')})
        else:
            # Just refresh members info
            asyncio.create_task(self.load_group_members())
        
    def _show_user_profile(self, user_data):
        """Show user profile window"""
        try:
            from client.UI.messenger_ui.user_profile_window import UserProfileWindow
            
            profile_window = UserProfileWindow(
                user_data=user_data,
                current_user_id=self.user_id,
                client=self.api_client.connection,  # Fix: dùng connection từ api_client
                parent=self
            )
            profile_window.show()
            
        except Exception as e:
            print(f"[ERROR] Failed to show user profile: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị thông tin người dùng: {str(e)}")

    def _handle_timestamp_clicked(self, timestamp):
        """Handle when user clicks on timestamp"""
        print(f"[DEBUG] Timestamp clicked: {timestamp}")
        # Could show detailed timestamp or message info
        # For now, just log it
