from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
class ChatListItem(QtWidgets.QFrame):
    """Individual chat list item with modern design"""
    
    clicked = pyqtSignal(dict)  # Signal when clicked
    
    def __init__(self, chat_data, parent=None):
        super().__init__(parent)
        self.chat_data = chat_data
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup chat list item UI"""
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-radius: 8px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #f0f2f5;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Avatar
        avatar = self._create_avatar()
        layout.addWidget(avatar)
        
        # Chat info
        info_layout = self._create_chat_info()
        layout.addLayout(info_layout, 1)
        
        # Time and status
        time_layout = self._create_time_status()
        layout.addLayout(time_layout)
    
    def _create_avatar(self):
        """Create user avatar"""
        avatar = QtWidgets.QLabel()
        avatar.setFixedSize(55, 55)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {self._get_avatar_color()};
                color: white;
                border-radius: 27px;
                font-size: 22px;
                font-weight: bold;
                border: 3px solid #e4e6ea;
            }}
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setText(self.chat_data.get('friend_name', 'U')[0].upper())
        return avatar
    
    def _create_chat_info(self):
        """Create chat info layout (name and last message)"""
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Name
        name_label = QtWidgets.QLabel(self.chat_data.get('friend_name', 'Unknown'))
        name_label.setStyleSheet("""
            QLabel {
                color: #1c1e21;
                font-size: 16px;
                font-weight: 600;
            }
        """)
        
        # Last message
        last_msg = self.chat_data.get('last_message', 'No messages')
        if len(last_msg) > 50:
            last_msg = last_msg[:50] + "..."
            
        msg_label = QtWidgets.QLabel(last_msg)
        msg_label.setStyleSheet("""
            QLabel {
                color: #8a8d91;
                font-size: 14px;
                font-weight: 400;
            }
        """)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(msg_label)
        
        return info_layout
    
    def _create_time_status(self):
        """Create time and status layout"""
        time_layout = QtWidgets.QVBoxLayout()
        time_layout.setSpacing(5)
        
        time_label = QtWidgets.QLabel(self._format_time(self.chat_data.get('last_message_time', '')))
        time_label.setStyleSheet("""
            QLabel {
                color: #8a8d91;
                font-size: 12px;
                font-weight: 400;
            }
        """)
        time_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        # Unread badge (optional)
        if self.chat_data.get('unread_count', 0) > 0:
            badge = self._create_unread_badge()
            time_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignRight)
        
        time_layout.addWidget(time_label)
        time_layout.addStretch()
        
        return time_layout
    
    def _create_unread_badge(self):
        """Create unread message badge"""
        badge = QtWidgets.QLabel(str(self.chat_data.get('unread_count')))
        badge.setFixedSize(20, 20)
        badge.setStyleSheet("""
            QLabel {
                background-color: #0084FF;
                color: white;
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return badge
    
    def _get_avatar_color(self):
        """Get avatar color based on friend name"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                 '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
        name = self.chat_data.get('friend_name', 'User')
        return colors[hash(name) % len(colors)]
    
    def _format_time(self, timestamp):
        """Format timestamp for display"""
        if not timestamp:
            return ""
        if hasattr(timestamp, 'strftime'):
            return timestamp.strftime("%H:%M")
        else:
            return str(timestamp)[:5]
    
    def mousePressEvent(self, event):
        """Handle mouse click event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.chat_data)
        super().mousePressEvent(event)
    
    def update_chat_data(self, new_chat_data):
        """Update chat data and refresh UI"""
        self.chat_data = new_chat_data
        # Refresh the UI components
        self._setup_ui()
    
    def set_online_status(self, is_online):
        """Set friend online status"""
        self.chat_data['is_online'] = is_online
        # You could add visual indicators here
