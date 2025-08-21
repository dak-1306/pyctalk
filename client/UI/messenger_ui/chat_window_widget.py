from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from .message_bubble_widget import MessageBubble


class ChatWindow(QtWidgets.QWidget):
    """Individual chat window with modern messenger design"""    
    back_clicked = pyqtSignal()  # Signal to go back to chat list
    message_sent = pyqtSignal(str)  # Signal when message is sent
    
    def __init__(self, chat_data=None, parent=None, **kwargs):
        super().__init__(parent)
        
        # Handle both new chat_data format and old parameter format for backward compatibility
        if chat_data is not None:
            self.chat_data = chat_data
        else:
            # Legacy support for old parameter names
            self.chat_data = {
                'friend_name': kwargs.get('friend_username', 'Friend'),
                'friend_id': kwargs.get('friend_id', 1),
                'current_username': kwargs.get('current_username', 'You'),
                'friend_avatar': kwargs.get('friend_avatar', ''),
                'last_message': kwargs.get('last_message', ''),
                'unread_count': kwargs.get('unread_count', 0)
            }
        
        self._setup_ui()
        self._load_sample_messages()
        
    def _setup_ui(self):
        """Setup chat window UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        self._create_header(layout)
        
        # Chat area
        self._create_chat_area(layout)
        
        # Input area
        self._create_input_area(layout)
    
    def _create_header(self, main_layout):
        """Create chat header with friend info and action buttons"""
        header = QtWidgets.QWidget()
        header.setFixedHeight(75)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-bottom: 1px solid #e1e5e9;
            }
        """)
        
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Back button
        self.btn_back = QtWidgets.QPushButton("←")
        self.btn_back.setFixedSize(45, 45)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                font-size: 24px;
                font-weight: bold;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_back.clicked.connect(self.back_clicked.emit)
        
        # Friend avatar
        friend_avatar = self._create_friend_avatar()
        
        # Friend info
        user_info = self._create_friend_info()
        
        # Action buttons
        buttons_widget = self._create_action_buttons()
        
        # Add to header layout
        header_layout.addWidget(self.btn_back)
        header_layout.addWidget(friend_avatar)
        header_layout.addLayout(user_info)
        header_layout.addStretch()
        header_layout.addWidget(buttons_widget)
        
        main_layout.addWidget(header)
    
    def _create_friend_avatar(self):
        """Create friend avatar in header"""
        friend_avatar = QtWidgets.QLabel()
        friend_avatar.setFixedSize(50, 50)
        friend_avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff7eb3, stop:1 #ff758c);
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                border: 3px solid rgba(255,255,255,0.3);
            }
        """)
        friend_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        friend_avatar.setText(self.chat_data.get('friend_name', 'F')[0].upper())
        return friend_avatar
    
    def _create_friend_info(self):
        """Create friend info layout in header"""
        user_info = QtWidgets.QVBoxLayout()
        user_info.setSpacing(2)
        
        friend_name = QtWidgets.QLabel(self.chat_data.get('friend_name', 'Friend'))
        friend_name.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: 600;
            }
        """)
        
        status = QtWidgets.QLabel("● Active now")
        status.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        user_info.addWidget(friend_name)
        user_info.addWidget(status)
        
        return user_info
    
    def _create_action_buttons(self):
        """Create action buttons (call, video, info)"""
        buttons_widget = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Call, Video, Info buttons
        for icon in ["📞", "📹", "ⓘ"]:
            btn = QtWidgets.QPushButton(icon)
            btn.setFixedSize(45, 45)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: white;
                    border: none;
                    border-radius: 22px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.25);
                }
            """)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            buttons_layout.addWidget(btn)
        
        return buttons_widget
    
    def _create_chat_area(self, main_layout):
        """Create scrollable chat messages area"""
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c8c8c8, stop:1 #b8b8b8);
                border-radius: 3px;
                min-height: 20px;
            }
        """)
        
        # Messages container
        self.messages_widget = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(self.messages_widget)
        main_layout.addWidget(self.scroll_area)
    
    def _create_input_area(self, main_layout):
        """Create message input area with send button"""
        input_area = QtWidgets.QWidget()
        input_area.setFixedHeight(85)
        input_area.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-top: 1px solid #e4e6ea;
            }
        """)
        
        input_layout = QtWidgets.QHBoxLayout(input_area)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(15)
        
        # Attach button
        btn_attach = self._create_attach_button()
        
        # Message input
        self.txt_message = self._create_message_input()
        
        # Emoji button
        btn_emoji = self._create_emoji_button()
        
        # Send button
        self.btn_send = self._create_send_button()
        
        # Add to layout
        input_layout.addWidget(btn_attach)
        input_layout.addWidget(self.txt_message)
        input_layout.addWidget(btn_emoji)
        input_layout.addWidget(self.btn_send)
        
        main_layout.addWidget(input_area)
    
    def _create_attach_button(self):
        """Create file attach button"""
        btn_attach = QtWidgets.QPushButton("📎")
        btn_attach.setFixedSize(50, 50)
        btn_attach.setStyleSheet("""
            QPushButton {
                background-color: #e4e6ea;
                color: #0084FF;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d3d6;
            }
        """)
        btn_attach.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return btn_attach
    
    def _create_message_input(self):
        """Create message input field"""
        txt_message = QtWidgets.QLineEdit()
        txt_message.setPlaceholderText("Type a message...")
        txt_message.setFixedHeight(50)
        txt_message.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: none;
                border-radius: 25px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: 400;
                color: #1c1e21;
            }
            QLineEdit:focus {
                background-color: #e4e6ea;
                outline: none;
                border: 2px solid #0084FF;
            }
        """)
        txt_message.returnPressed.connect(self.send_message)
        return txt_message
    
    def _create_emoji_button(self):
        """Create emoji picker button"""
        btn_emoji = QtWidgets.QPushButton("😊")
        btn_emoji.setFixedSize(50, 50)
        btn_emoji.setStyleSheet("""
            QPushButton {
                background-color: #e4e6ea;
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #d0d3d6;
            }
        """)
        btn_emoji.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return btn_emoji
    
    def _create_send_button(self):
        """Create send message button"""
        btn_send = QtWidgets.QPushButton("➤")
        btn_send.setFixedSize(50, 50)
        btn_send.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0084FF, stop:1 #0066CC);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0066CC, stop:1 #004499);
            }
        """)
        btn_send.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_send.clicked.connect(self.send_message)
        return btn_send
    
    def _load_sample_messages(self):
        """Load sample messages for demo"""
        sample_messages = [
            ("Chào bạn! Bạn có khỏe không?", False),
            ("Chào! Mình khỏe, cảm ơn bạn. Còn bạn thì sao?", True),
            ("Mình cũng ổn. Project PycTalk này tiến triển như thế nào rồi?", False),
            ("Đang làm giao diện chat giống Messenger đây! Nhìn đẹp không?", True),
            ("Wow nhìn rất đẹp và professional! Khi nào có thể demo được?", False),
        ]
        
        for message, is_sent in sample_messages:
            self.add_message(message, is_sent)
        
        QTimer.singleShot(100, self._scroll_to_bottom)
    
    def add_message(self, message, is_sent):
        """Add a new message to the chat"""
        # Remove stretch if present
        layout = self.messages_layout
        if layout.count() > 0:
            last_item = layout.takeAt(layout.count() - 1)
            if last_item.spacerItem():
                del last_item
        
        # Add message bubble
        bubble = MessageBubble(message, is_sent)
        layout.addWidget(bubble)
        
        # Add stretch back
        layout.addStretch()
        
        # Auto scroll
        QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        """Scroll to bottom of chat"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send a new message"""
        text = self.txt_message.text().strip()
        if not text:
            return
        
        # Add sent message
        self.add_message(text, True)
        
        # Emit signal
        self.message_sent.emit(text)
        
        # Clear input
        self.txt_message.clear()
        
        # Simulate reply after 2 seconds
        QTimer.singleShot(2000, lambda: self._simulate_reply(text))
    
    def _simulate_reply(self, original_message):
        """Simulate friend reply (for demo)"""
        replies = [
            "Tôi hiểu rồi!",
            "Cảm ơn bạn!",
            "Nghe hay quá!",
            "OK được đó!",
            "Haha thú vị nhỉ!",
            "Sounds good!",
        ]
        
        import random
        reply = random.choice(replies)
        self.add_message(reply, False)
    
    def clear_messages(self):
        """Clear all messages"""
        while self.messages_layout.count() > 1:  # Keep the stretch
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def load_message_history(self, messages):
        """Load message history from database"""
        self.clear_messages()
        for msg in messages:
            is_sent = msg.get('sender_id') == self.chat_data.get('current_user_id')
            self.add_message(msg.get('content', ''), is_sent)
