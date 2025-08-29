import logging
import asyncio
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, QTimer

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
    file_send_requested = QtCore.pyqtSignal(dict)  # Thêm signal cho file sending
    group_selected = QtCore.pyqtSignal(dict)
    back_clicked = QtCore.pyqtSignal()  # Thêm signal cho back button

    def __init__(self, client, user_id, username, group_data):
        super().__init__()
        # Set object name for CSS specificity
        self.setObjectName("EmbeddedGroupChatWidget")
        
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

        # File selection tracking
        self.selected_file_path = None
        self.selected_file_type = None
        self.current_file_preview = None

        # Track theme mode
        self.is_dark_mode = False
        
        self._setupUI()
        
        # Set overall widget styling với theme support
        self._apply_theme()
        
        # Thiết lập nhóm hiện tại và load tin nhắn với lazy loading
        self.logic.current_group = group_data
        # Delay async operations until widget is shown
        self._pending_async_tasks = [
            self.logic.load_initial_messages(),
            self.load_group_members()
        ]
        
        # Setup scroll loading detection
        self._setup_scroll_loading()

    def showEvent(self, event):
        """Reload tin nhắn khi widget được hiển thị lại (quay lại nhóm)"""
        super().showEvent(event)
        logger.info("[EmbeddedGroupChatWidget] showEvent triggered - reload group messages")
        try:
            if getattr(self.logic, "current_group", None):
                import asyncio
                # Execute pending async tasks
                if hasattr(self, '_pending_async_tasks'):
                    for task in self._pending_async_tasks:
                        asyncio.create_task(task)
                    self._pending_async_tasks = []  # Clear after execution
                
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

        # Setup responsive design
        self._setup_responsive_design()

        # Hiển thị tên nhóm với button quản lý - Header Bar (đồng bộ với chat 1-1)
        group_header_layout = QtWidgets.QHBoxLayout()
        group_header_layout.setContentsMargins(20, 0, 20, 0)
        group_header_layout.setSpacing(15)

        # Back button (cho consistency với chat 1-1)
        self.back_btn = QtWidgets.QPushButton("←")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.back_btn.clicked.connect(self._on_back_clicked)
        group_header_layout.addWidget(self.back_btn)

        # Group avatar (circle với initial)
        group_initial = self.group_data.get('name', 'Group')[0].upper()
        group_avatar = QtWidgets.QLabel(group_initial)
        group_avatar.setFixedSize(50, 50)
        group_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_avatar.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        group_header_layout.addWidget(group_avatar)

        self.group_info_label = QtWidgets.QLabel(self.group_data.get('name', 'Group'))
        self.group_info_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
            }
        """)
        group_header_layout.addWidget(self.group_info_label)

        group_header_layout.addStretch()

        # Theme toggle button (giữ lại tính năng nâng cao)
        self.theme_toggle_btn = QtWidgets.QPushButton("🌙")
        self.theme_toggle_btn.setFixedSize(40, 40)
        self.theme_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        self.theme_toggle_btn.setToolTip("Chuyển đổi chế độ sáng/tối")
        group_header_layout.addWidget(self.theme_toggle_btn)

        # Group management button
        self.manage_group_btn = QtWidgets.QPushButton("⚙️")
        self.manage_group_btn.setFixedSize(40, 40)
        self.manage_group_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.manage_group_btn.clicked.connect(self.open_group_management)
        self.manage_group_btn.setToolTip("Quản lý nhóm")
        group_header_layout.addWidget(self.manage_group_btn)

        group_header_widget = QtWidgets.QWidget()
        group_header_widget.setFixedHeight(75)  # Đồng bộ height với chat 1-1
        group_header_widget.setLayout(group_header_layout)
        group_header_widget.setStyleSheet("""
            QWidget {
                background-color: #667eea;  /* Đồng bộ màu với chat 1-1 */
                border-bottom: 1px solid #e1e5e9;
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
        self.messages_layout.setContentsMargins(10, 10, 10, 10)  # Đồng bộ với chat 1-1
        self.messages_layout.setSpacing(8)  # Đồng bộ spacing với chat 1-1
        # Stretch để các bubble dồn lên trên, chừa chỗ cuối
        self.messages_layout.addStretch()
        
        # Subtle loading bar thay vì popup
        self.loading_bar = QtWidgets.QProgressBar()
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
                text-align: center;
                height: 3px;  /* Đồng bộ height với chat 1-1 */
                border-radius: 1px;
                margin: 0px;
            }
            QProgressBar::chunk {
                background-color: #667eea;  /* Đồng bộ màu với chat 1-1 */
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

        # Input gửi tin - Modern design với emoji picker
        input_container = QtWidgets.QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-top: 1px solid #e4e6ea;
                padding: 0px;
            }
        """)

        # File preview area
        self.file_preview_area = QtWidgets.QWidget()
        self.file_preview_layout = QtWidgets.QVBoxLayout(self.file_preview_area)
        self.file_preview_area.hide()

        input_layout = QtWidgets.QHBoxLayout(input_container)
        input_layout.setContentsMargins(5, 5, 5, 5)  # Đồng bộ với chat 1-1
        input_layout.setSpacing(5)  # Đồng bộ spacing với chat 1-1

        # Emoji button
        self.emoji_button = QtWidgets.QPushButton("😊")
        self.emoji_button.setFixedSize(36, 36)
        self.emoji_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 18px;
                font-size: 18px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #f7f8fa;
            }
            QPushButton:pressed {
                background-color: #e4e6ea;
            }
        """)
        self.emoji_button.clicked.connect(self._show_emoji_picker)
        input_layout.addWidget(self.emoji_button)

        # File upload widget (đồng bộ với chat 1-1)
        try:
            from client.UI.messenger_ui.file_upload_widget import FileUploadWidget
            self.file_upload = FileUploadWidget()
            self.file_upload.file_selected.connect(self._on_file_selected)
            input_layout.addWidget(self.file_upload)
        except ImportError as e:
            print(f"[WARNING][GroupChat] Could not import FileUploadWidget: {e}")
            self.file_upload = None

        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")  # Đồng bộ với chat 1-1
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

        # Typing indicator label
        self.typing_indicator = QtWidgets.QLabel("")
        self.typing_indicator.setStyleSheet("""
            QLabel {
                color: #8a8d91;
                font-size: 12px;
                font-style: italic;
                padding: 0px 8px;
            }
        """)
        self.typing_indicator.hide()

        self.send_button = QtWidgets.QPushButton("➤")
        self.send_button.setFixedSize(40, 35)  # Đồng bộ size với chat 1-1
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0084ff;  /* Đồng bộ màu với chat 1-1 */
                color: white;
                border: none;
                border-radius: 17px;  /* Đồng bộ border-radius */
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0066cc;  /* Đồng bộ hover color */
            }
            QPushButton:pressed {
                background-color: #004499;  /* Đồng bộ pressed color */
            }
            QPushButton:disabled {
                background-color: #cccccc;  /* Màu xám nhạt hơn khi disabled */
            }
        """)
        self.send_button.clicked.connect(self._on_send_message)
        self.send_button.setEnabled(False)

        input_layout.addWidget(self.message_input, stretch=1)
        input_layout.addWidget(self.typing_indicator)
        input_layout.addWidget(self.send_button)
        layout.addWidget(self.file_preview_area)
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
    
    def _apply_theme(self):
        """Áp dụng theme (light/dark) cho toàn bộ widget"""
        if self.is_dark_mode:
            self.setStyleSheet("""
                EmbeddedGroupChatWidget {
                    background-color: #1a1a1a;
                    border: none;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                EmbeddedGroupChatWidget {
                    background-color: #ffffff;
                    border: none;
                    color: #1a1a1a;
                }
            """)
        
        # Update các component khác
        self._update_component_themes()

    def _update_component_themes(self):
        """Cập nhật theme cho các component con"""
        if self.is_dark_mode:
            # Update theme toggle button
            self.theme_toggle_btn.setText("☀️")
            self.theme_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    border-radius: 18px;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
            """)
            
            # Header
            self.group_info_label.setStyleSheet("""
                QLabel {
                    font-weight: bold; 
                    font-size: 16px;
                    color: #ffffff;
                    padding: 0px;
                }
            """)
            
            # Members info
            self.members_info_label.setStyleSheet("""
                QLabel {
                    color: #b0b0b0; 
                    padding: 8px 16px; 
                    font-size: 12px; 
                    background-color: #2a2a2a;
                    border-bottom: 1px solid #404040;
                    margin: 0px;
                }
            """)
            
            # Scroll area
            self.scroll_area.setStyleSheet("""
                QScrollArea {
                    background-color: #1a1a1a;
                    border: none;
                }
                QScrollBar:vertical {
                    background-color: #2a2a2a;
                    width: 8px;
                    border-radius: 4px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #555555;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #777777;
                }
            """)
            
            # Emoji button
            self.emoji_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 18px;
                    font-size: 18px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
            """)
            
            # Typing indicator
            self.typing_indicator.setStyleSheet("""
                QLabel {
                    color: #b0b0b0;
                    font-size: 12px;
                    font-style: italic;
                    padding: 0px 8px;
                }
            """)
            
        else:
            # Update theme toggle button
            self.theme_toggle_btn.setText("🌙")
            self.theme_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #666666;
                    border: none;
                    border-radius: 18px;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #f7f8fa;
                }
                QPushButton:pressed {
                    background-color: #e4e6ea;
                }
            """)
            
            # Light mode styles (giữ nguyên)
            self.group_info_label.setStyleSheet("""
                QLabel {
                    font-weight: bold; 
                    font-size: 16px;
                    color: #1a1a1a;
                    padding: 0px;
                }
            """)
            
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
            """)
            
            # Emoji button
            self.emoji_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 18px;
                    font-size: 18px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #f7f8fa;
                }
                QPushButton:pressed {
                    background-color: #e4e6ea;
                }
            """)
            
            # Typing indicator
            self.typing_indicator.setStyleSheet("""
                QLabel {
                    color: #8a8d91;
                    font-size: 12px;
                    font-style: italic;
                    padding: 0px 8px;
                }
            """)

    def toggle_theme(self):
        """Chuyển đổi giữa light/dark mode"""
        self.is_dark_mode = not self.is_dark_mode
        self._apply_theme()
        
        # Animate theme transition
        self._animate_theme_transition()

    def _animate_theme_transition(self):
        """Animation cho việc chuyển theme"""
        try:
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
            
            # Fade animation cho toàn bộ widget
            animation = QPropertyAnimation(self, b"windowOpacity")
            animation.setDuration(300)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            animation.setStartValue(0.8)
            animation.setEndValue(1.0)
            animation.start()
            
        except Exception as e:
            print(f"[DEBUG] Theme transition animation failed: {e}")

    def _animate_message_bubble(self, bubble):
        """Add smooth fade-in animation to message bubble với theme support"""
        try:
            # Ensure bubble is visible first
            bubble.setVisible(True)
            bubble.show()
            
            # Apply theme to bubble
            self._apply_theme_to_bubble(bubble)
            
            # Skip animation for now to fix visibility issues
            print(f"[DEBUG] Message bubble animated and visible: {bubble.isVisible()}")
            
        except Exception as e:
            print(f"[DEBUG] Animation error (fallback to instant): {e}")
            # Fallback - just show bubble instantly
            bubble.setVisible(True)
            bubble.show()

    def _apply_theme_to_bubble(self, bubble):
        """Áp dụng theme cho message bubble"""
        try:
            # Update bubble styling based on theme
            if hasattr(bubble, 'is_sent') and hasattr(bubble, 'setStyleSheet'):
                if bubble.is_sent:
                    if self.is_dark_mode:
                        bubble.setStyleSheet("""
                            QLabel {
                                background-color: #0084FF;
                                color: white;
                                border-radius: 18px;
                                padding: 10px 14px;
                                font-size: 14px;
                                line-height: 1.4;
                            }
                        """)
                    else:
                        bubble.setStyleSheet("""
                            QLabel {
                                background-color: #0084FF;
                                color: white;
                                border-radius: 18px;
                                padding: 10px 14px;
                                font-size: 14px;
                                line-height: 1.4;
                            }
                        """)
                else:
                    if self.is_dark_mode:
                        bubble.setStyleSheet("""
                            QLabel {
                                background-color: #333333;
                                color: #ffffff;
                                border-radius: 18px;
                                padding: 10px 14px;
                                font-size: 14px;
                                line-height: 1.4;
                                border: 1px solid #555555;
                            }
                        """)
                    else:
                        bubble.setStyleSheet("""
                            QLabel {
                                background-color: #f1f3f4;
                                color: #1a1a1a;
                                border-radius: 18px;
                                padding: 10px 14px;
                                font-size: 14px;
                                line-height: 1.4;
                                border: 1px solid #e4e6ea;
                            }
                        """)
        except Exception as e:
            print(f"[DEBUG] Failed to apply theme to bubble: {e}")

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

    def _show_emoji_picker(self):
        """Hiển thị emoji picker đơn giản"""
        self._show_simple_emoji_picker()

    def _show_simple_emoji_picker(self):
        """Emoji picker đơn giản nếu không có dialog riêng"""
        emojis = ["😀", "😂", "😊", "😍", "🥰", "😘", "😉", "😎", "🤔", "😮", "😢", "😭", 
                 "😤", "😡", "🥺", "😴", "🤗", "🤭", "🤫", "🤥", "😈", "👻", "💀", "👽",
                 "👍", "👎", "👌", "✌️", "🤞", "👏", "🙌", "🤝", "🙏", "💪", "🤳", "💅",
                 "❤️", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❣️", "💕", "💞",
                 "💓", "💗", "💖", "💘", "💝", "💟", "☮️", "✝️", "☪️", "🕉️", "☸️", "✡️",
                 "🔥", "💫", "⭐", "🌟", "✨", "💥", "💢", "💦", "💨", "💬", "👁️‍🗨️", "🗨️", "🗯️", "💭"]
        
        # Tạo menu popup với emojis
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e4e6ea;
                border-radius: 8px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px;
                border-radius: 4px;
                font-size: 16px;
            }
            QMenu::item:selected {
                background-color: #f7f8fa;
            }
        """)
        
        # Chia emojis thành các hàng
        emojis_per_row = 8
        current_row = []
        
        for i, emoji in enumerate(emojis):
            action = menu.addAction(emoji)
            action.triggered.connect(lambda checked, e=emoji: self._insert_emoji(e))
            
            current_row.append(action)
            if (i + 1) % emojis_per_row == 0:
                menu.addSeparator()
                current_row = []
        
        # Hiển thị menu tại vị trí emoji button
        button_pos = self.emoji_button.mapToGlobal(QtCore.QPoint(0, self.emoji_button.height()))
        menu.exec(button_pos)

    def _insert_emoji(self, emoji):
        """Chèn emoji vào input field"""
        current_text = self.message_input.text()
        self.message_input.setText(current_text + emoji)
        self.message_input.setFocus()

    def _on_text_changed(self):
        """Handle typing indicator và send button state"""
        text = self.message_input.text()
        
        # Enable/disable send button based on text content
        has_text = bool(text.strip())
        self.send_button.setEnabled(has_text)
        
        # Update send button style
        if has_text:
            self.send_button.setStyleSheet("""
                QPushButton {
                    background-color: #0084FF;
                    color: white;
                    border: none;
                    border-radius: 18px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0073E6;
                }
                QPushButton:pressed {
                    background-color: #005CBF;
                }
            """)
        else:
            self.send_button.setStyleSheet("""
                QPushButton {
                    background-color: #bcc0c4;
                    color: white;
                    border: none;
                    border-radius: 18px;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
        
        # Send typing indicator to server (nếu cần)
        self._handle_typing_indicator(text)

    def _handle_typing_indicator(self, text):
        """Xử lý typing indicator"""
        # Chỉ gửi typing indicator nếu có text và chưa gửi trong 2 giây
        if text.strip():
            current_time = QtCore.QDateTime.currentDateTime().toMSecsSinceEpoch()
            if not hasattr(self, '_last_typing_time') or current_time - self._last_typing_time > 2000:
                self._last_typing_time = current_time
                # Gửi typing indicator đến server (nếu API hỗ trợ)
                asyncio.create_task(self._send_typing_indicator())
        else:
            # Clear typing indicator khi xóa text
            if hasattr(self, '_last_typing_time'):
                delattr(self, '_last_typing_time')
                asyncio.create_task(self._clear_typing_indicator())

    async def _send_typing_indicator(self):
        """Gửi typing indicator đến server"""
        try:
            # TODO: Implement API call to send typing indicator
            print(f"[DEBUG] Sending typing indicator for group {self.group_data.get('group_id')}")
        except Exception as e:
            print(f"[DEBUG] Failed to send typing indicator: {e}")

    async def _clear_typing_indicator(self):
        """Xóa typing indicator"""
        try:
            # TODO: Implement API call to clear typing indicator
            print(f"[DEBUG] Clearing typing indicator for group {self.group_data.get('group_id')}")
        except Exception as e:
            print(f"[DEBUG] Failed to clear typing indicator: {e}")

    def show_typing_indicator(self, username):
        """Hiển thị typing indicator từ user khác"""
        if username != self.username:
            self.typing_indicator.setText(f"{username} đang gõ...")
            self.typing_indicator.show()
            
            # Auto hide after 3 seconds
            if hasattr(self, '_typing_timer'):
                self._typing_timer.stop()
            
            self._typing_timer = QTimer()
            self._typing_timer.setSingleShot(True)
            self._typing_timer.timeout.connect(self.hide_typing_indicator)
            self._typing_timer.start(3000)

    def hide_typing_indicator(self):
        """Ẩn typing indicator"""
        self.typing_indicator.hide()
        if hasattr(self, '_typing_timer'):
            self._typing_timer.stop()

    def update_group_info(self):
        """Cập nhật thông tin nhóm hiển thị - Đã được cập nhật để đồng bộ với chat 1-1"""
        if self.group_data:
            group_name = self.group_data.get("name", "Unknown Group")
            self.group_info_label.setText(group_name)  # Chỉ hiển thị tên nhóm, không có ID

    def _on_back_clicked(self):
        """Handle back button click - đồng bộ với chat 1-1"""
        # Emit signal để parent widget xử lý việc quay lại
        self.back_clicked.emit()
        print("[DEBUG][GroupChat] Back button clicked")

    def _on_send_message(self):
        """Xử lý gửi tin nhắn hoặc file"""
        content = self.message_input.text().strip()

        # If file is selected, send file message
        if hasattr(self, 'selected_file_path') and self.selected_file_path:
            self._send_file_message()
        elif content:
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

    def _on_file_selected(self, file_path, file_type):
        """Handle file selection from upload widget"""
        print(f"[DEBUG][EmbeddedGroupChat] File selected: {file_path}, type: {file_type}")
        self.selected_file_path = file_path
        self.selected_file_type = file_type
        self._show_file_preview(file_path, file_type)

    def _show_file_preview(self, file_path, file_type):
        """Show preview of selected file"""
        try:
            from UI.messenger_ui.file_upload_widget import FilePreviewWidget

            # Remove existing preview
            if self.current_file_preview:
                self.file_preview_layout.removeWidget(self.current_file_preview)
                self.current_file_preview.deleteLater()

            # Create new preview
            self.current_file_preview = FilePreviewWidget(file_path, file_type)
            self.current_file_preview.remove_file.connect(self._remove_file_preview)
            self.file_preview_layout.addWidget(self.current_file_preview)

            # Show preview area
            self.file_preview_area.show()

        except ImportError as e:
            print(f"[WARNING][EmbeddedGroupChat] Could not import FilePreviewWidget: {e}")

    def _remove_file_preview(self):
        """Remove file preview and reset selection"""
        if self.current_file_preview:
            self.file_preview_layout.removeWidget(self.current_file_preview)
            self.current_file_preview.deleteLater()
            self.current_file_preview = None

        # Hide preview area
        self.file_preview_area.hide()

        # Reset file selection
        self.selected_file_path = None
        self.selected_file_type = None
        if hasattr(self, 'file_upload') and self.file_upload:
            self.file_upload.reset()

    def _send_file_message(self):
        """Send file message with optional text caption"""
        if not self.selected_file_path:
            return

        text_caption = self.message_input.text().strip()
        print(f"[DEBUG][EmbeddedGroupChat] Sending file: {self.selected_file_path} with caption: '{text_caption}'")

        # Create message data for file
        message_data = {
            'file_path': self.selected_file_path,
            'file_type': self.selected_file_type,
            'caption': text_caption
        }

        # Emit file send signal
        self.file_send_requested.emit(message_data)

        # Clear input and preview
        self.message_input.clear()
        self._remove_file_preview()

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

    def add_message_reaction(self, message_id, emoji):
        """Thêm reaction cho tin nhắn"""
        print(f"[DEBUG] Adding reaction {emoji} to message {message_id}")
        # TODO: Implement API call to add reaction
        # For now, just show visual feedback
        self._show_reaction_feedback(emoji)

    def _show_reaction_feedback(self, emoji):
        """Hiển thị feedback khi thêm reaction"""
        # Create a temporary floating emoji animation
        try:
            floating_emoji = QtWidgets.QLabel(emoji)
            floating_emoji.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    background-color: transparent;
                    border: none;
                }
            """)
            floating_emoji.setParent(self)
            floating_emoji.move(self.width() // 2 - 12, self.height() // 2 - 12)
            floating_emoji.show()
            
            # Animate upward and fade out
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
            
            # Move animation
            move_anim = QPropertyAnimation(floating_emoji, b"pos")
            move_anim.setDuration(1000)
            move_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            move_anim.setStartValue(floating_emoji.pos())
            move_anim.setEndValue(floating_emoji.pos() + QtCore.QPoint(0, -50))
            
            # Opacity animation
            opacity_anim = QPropertyAnimation(floating_emoji, b"windowOpacity")
            opacity_anim.setDuration(1000)
            opacity_anim.setStartValue(1.0)
            opacity_anim.setEndValue(0.0)
            
            # Start animations
            move_anim.start()
            opacity_anim.start()
            
            # Clean up after animation
            QTimer.singleShot(1000, floating_emoji.deleteLater)
            
        except Exception as e:
            print(f"[DEBUG] Reaction feedback animation failed: {e}")

    def _setup_responsive_design(self):
        """Thiết lập responsive design cho các màn hình khác nhau"""
        # Adjust sizes based on screen size
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_size = screen.size()
            screen_width = screen_size.width()
            
            # Adjust message bubble max width based on screen size
            if screen_width < 1200:  # Small screens
                self.max_bubble_width = 250
            elif screen_width < 1600:  # Medium screens
                self.max_bubble_width = 320
            else:  # Large screens
                self.max_bubble_width = 400
            
            # Adjust font sizes
            if screen_width < 1200:
                self.base_font_size = 12
                self.header_font_size = 14
            else:
                self.base_font_size = 14
                self.header_font_size = 16

    def resizeEvent(self, event):
        """Handle resize events for responsive design"""
        super().resizeEvent(event)
        # Update responsive settings when window is resized
        self._setup_responsive_design()
        self._update_component_sizes()

    def _update_component_sizes(self):
        """Cập nhật kích thước components theo responsive design"""
        try:
            # Update message input size
            if hasattr(self, 'max_bubble_width'):
                # Update existing bubbles if needed
                for i in range(self.messages_layout.count()):
                    item = self.messages_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if hasattr(widget, 'setMaximumWidth'):
                            widget.setMaximumWidth(self.max_bubble_width)
            
            # Update font sizes
            if hasattr(self, 'base_font_size'):
                # Update input field font
                font = self.message_input.font()
                font.setPointSize(self.base_font_size)
                self.message_input.setFont(font)
                
                # Update header font
                header_font = self.group_info_label.font()
                header_font.setPointSize(self.header_font_size)
                self.group_info_label.setFont(header_font)
                
        except Exception as e:
            print(f"[DEBUG] Failed to update component sizes: {e}")
