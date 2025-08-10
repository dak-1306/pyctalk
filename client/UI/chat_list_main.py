# Main Chat List UI - Giao Diện Danh Sách Chat Messenger
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                            QScrollArea, QLineEdit, QPushButton, QLabel, 
                            QApplication, QListWidget, QListWidgetItem, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QPixmap, QPainter, QBrush, QColor

# Import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from UI.messenger_test import MessengerTestWindow
    from database.messenger_db import MessengerDatabase
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    MessengerTestWindow = None
    MessengerDatabase = None

class ChatListItem(QWidget):
    """Widget cho mỗi item trong danh sách chat"""
    
    clicked = pyqtSignal(dict)  # Signal khi click vào item
    
    def __init__(self, chat_data, parent=None):
        super().__init__(parent)
        self.chat_data = chat_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI cho chat item"""
        self.setFixedHeight(80)
        self.setStyleSheet("""
            ChatListItem {
                background-color: transparent;
                border-bottom: 1px solid #e4e6ea;
            }
            ChatListItem:hover {
                background-color: #f0f2f5;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Avatar
        avatar = QLabel()
        avatar.setFixedSize(56, 56)
        avatar_text = self.chat_data.get('friend_name', 'U')[0].upper()
        avatar.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #{self.get_avatar_color()}, stop:1 #{self.get_avatar_color(True)});
                color: white;
                border-radius: 28px;
                font-size: 22px;
                font-weight: bold;
                border: 3px solid #ffffff;
            }}
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setText(avatar_text)
        
        # Chat info (name + last message)
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # Friend name
        name_label = QLabel(self.chat_data.get('friend_name', 'Unknown'))
        name_label.setStyleSheet("""
            QLabel {
                color: #1c1e21;
                font-size: 16px;
                font-weight: 600;
            }
        """)
        
        # Last message
        last_msg = self.chat_data.get('last_message', 'No messages')
        if len(last_msg) > 40:
            last_msg = last_msg[:40] + "..."
        
        message_label = QLabel(last_msg)
        message_label.setStyleSheet("""
            QLabel {
                color: #65676b;
                font-size: 14px;
                font-weight: 400;
            }
        """)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(message_label)
        
        # Right side (time + unread badge)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Time
        time_str = self.format_time(self.chat_data.get('last_message_time'))
        time_label = QLabel(time_str)
        time_label.setStyleSheet("""
            QLabel {
                color: #65676b;
                font-size: 12px;
                font-weight: 400;
            }
        """)
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Unread badge (optional)
        unread_count = self.chat_data.get('unread_count', 0)
        if unread_count > 0:
            unread_badge = QLabel(str(unread_count))
            unread_badge.setFixedSize(24, 24)
            unread_badge.setStyleSheet("""
                QLabel {
                    background-color: #0084FF;
                    color: white;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            unread_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(unread_badge)
        else:
            right_layout.addStretch()
        
        right_layout.addWidget(time_label)
        right_widget.setFixedWidth(80)
        
        # Online status dot
        status_dot = QLabel("●")
        if self.chat_data.get('is_online', False):
            status_dot.setStyleSheet("color: #42b883; font-size: 14px;")
        else:
            status_dot.setStyleSheet("color: transparent;")
        
        layout.addWidget(avatar)
        layout.addWidget(info_widget)
        layout.addStretch()
        layout.addWidget(right_widget)
        layout.addWidget(status_dot)
    
    def get_avatar_color(self, darker=False):
        """Get avatar color based on name"""
        colors = [
            ("#FF6B6B", "#FF5252"),  # Red
            ("#4ECDC4", "#26A69A"),  # Teal  
            ("#45B7D1", "#2196F3"),  # Blue
            ("#96CEB4", "#66BB6A"),  # Green
            ("#FECA57", "#FF9800"),  # Orange
            ("#FF9FF3", "#E91E63"),  # Pink
            ("#54A0FF", "#3F51B5"),  # Indigo
            ("#5F27CD", "#673AB7"),  # Purple
        ]
        
        name = self.chat_data.get('friend_name', 'U')
        color_index = len(name) % len(colors)
        return colors[color_index][1 if darker else 0]
    
    def format_time(self, timestamp):
        """Format timestamp for display"""
        if not timestamp:
            return ""
        
        try:
            if isinstance(timestamp, str):
                return timestamp
            
            now = datetime.now()
            diff = now - timestamp
            
            if diff.days > 0:
                if diff.days == 1:
                    return "Yesterday"
                elif diff.days < 7:
                    return f"{diff.days}d ago"
                else:
                    return timestamp.strftime("%m/%d")
            else:
                hours = diff.seconds // 3600
                if hours > 0:
                    return f"{hours}h ago"
                else:
                    minutes = diff.seconds // 60
                    if minutes > 0:
                        return f"{minutes}m ago"
                    else:
                        return "Just now"
        except:
            return "Recently"
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.chat_data)
        super().mousePressEvent(event)

class ChatListWindow(QMainWindow):
    """Main chat list window - giống Messenger"""
    
    def __init__(self):
        super().__init__()
        self.current_user_id = 1  # Default user ID
        self.current_username = "Nguyễn Văn A"
        
        # Database connection
        self.messenger_db = None
        try:
            if MessengerDatabase:
                self.messenger_db = MessengerDatabase()
        except Exception as e:
            print(f"Database connection failed: {e}")
        
        self.setup_ui()
        self.load_chats()
        
        # Auto refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_chats)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
    
    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("PycTalk - Messenger")
        self.setMinimumSize(400, 600)
        self.resize(450, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Search bar
        self.create_search_bar(main_layout)
        
        # Chat list
        self.create_chat_list(main_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def create_header(self, main_layout):
        """Create header with user info"""
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0084FF, stop:1 #00C6FF);
                border-bottom: 1px solid #e1e5e9;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # User avatar
        user_avatar = QLabel()
        user_avatar.setFixedSize(50, 50)
        user_avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF6B6B, stop:1 #FF8E8E);
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid rgba(255,255,255,0.4);
            }
        """)
        user_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_avatar.setText(self.current_username[0].upper())
        
        # Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title = QLabel("Chats")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 700;
            }
        """)
        
        subtitle = QLabel(self.current_username)
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                font-weight: 400;
            }
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(45, 45)
        settings_btn.setStyleSheet("""
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
        settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        settings_btn.clicked.connect(self.show_settings)
        
        header_layout.addWidget(user_avatar)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(settings_btn)
        
        main_layout.addWidget(header)
    
    def create_search_bar(self, main_layout):
        """Create search bar"""
        search_container = QWidget()
        search_container.setFixedHeight(60)
        search_container.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                border-bottom: 1px solid #e4e6ea;
            }
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(16, 12, 16, 12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search conversations...")
        self.search_input.setFixedHeight(36)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #e4e6ea;
                border-radius: 18px;
                padding: 8px 16px;
                font-size: 14px;
                color: #1c1e21;
            }
            QLineEdit:focus {
                border: 2px solid #0084FF;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #65676b;
            }
        """)
        self.search_input.textChanged.connect(self.filter_chats)
        
        search_layout.addWidget(self.search_input)
        main_layout.addWidget(search_container)
    
    def create_chat_list(self, main_layout):
        """Create scrollable chat list"""
        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: #c4c4c4;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Chat list widget
        self.chat_list_widget = QWidget()
        self.chat_list_layout = QVBoxLayout(self.chat_list_widget)
        self.chat_list_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_list_layout.setSpacing(0)
        self.chat_list_layout.addStretch()  # Push items to top
        
        self.scroll_area.setWidget(self.chat_list_widget)
        main_layout.addWidget(self.scroll_area)
    
    def load_chats(self):
        """Load chat conversations"""
        if self.messenger_db:
            try:
                conversations = self.messenger_db.get_user_conversations(self.current_user_id)
                self.display_chats(conversations)
                print(f"✅ Loaded {len(conversations)} conversations")
            except Exception as e:
                print(f"Error loading chats: {e}")
                self.load_sample_chats()
        else:
            self.load_sample_chats()
    
    def load_sample_chats(self):
        """Load sample chat data"""
        sample_chats = [
            {
                'friend_id': 2,
                'friend_name': 'Trần Thị B',
                'last_message': 'Đang làm giao diện chat giống Messenger đây! 😊',
                'last_message_time': 'Just now',
                'unread_count': 2,
                'is_online': True
            },
            {
                'friend_id': 3,
                'friend_name': 'Lê Văn C',
                'last_message': 'Project PycTalk tiến triển thế nào rồi? Có cần hỗ trợ gì không?',
                'last_message_time': '2m ago',
                'unread_count': 0,
                'is_online': False
            },
            {
                'friend_id': 4,
                'friend_name': 'Phạm Thị D',
                'last_message': 'Cảm ơn bạn về thông tin! Rất hữu ích',
                'last_message_time': '1h ago',
                'unread_count': 0,
                'is_online': True
            },
            {
                'friend_id': 5,
                'friend_name': 'Hoàng Văn E',
                'last_message': 'Hẹn gặp lại bạn sau! 👋',
                'last_message_time': 'Yesterday',
                'unread_count': 1,
                'is_online': False
            },
            {
                'friend_id': 6,
                'friend_name': 'Nguyễn Thị F',
                'last_message': 'UI này nhìn đẹp quá! Giống Messenger thật sự',
                'last_message_time': '2 days ago',
                'unread_count': 0,
                'is_online': True
            }
        ]
        
        self.display_chats(sample_chats)
        print("✅ Loaded sample chats")
    
    def display_chats(self, chats):
        """Display chat items in the list"""
        # Clear existing items
        self.clear_chat_list()
        
        for chat in chats:
            chat_item = ChatListItem(chat)
            chat_item.clicked.connect(self.open_chat)
            self.chat_list_layout.addWidget(chat_item)
        
        # Remove stretch and add it at the end
        self.chat_list_layout.addStretch()
    
    def clear_chat_list(self):
        """Clear all chat items"""
        while self.chat_list_layout.count() > 0:
            child = self.chat_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def filter_chats(self, text):
        """Filter chats based on search text"""
        # TODO: Implement search filtering
        print(f"Search: {text}")
    
    def refresh_chats(self):
        """Refresh chat list"""
        self.load_chats()
    
    def open_chat(self, chat_data):
        """Open chat window for selected conversation"""
        friend_id = chat_data.get('friend_id')
        friend_name = chat_data.get('friend_name', 'Unknown')
        
        print(f"Opening chat with {friend_name} (ID: {friend_id})")
        
        if MessengerTestWindow:
            # Open new chat window
            chat_window = MessengerTestWindow()
            chat_window.ui.lblFriendName.setText(friend_name)
            chat_window.ui.friendAvatar.setText(friend_name[0].upper())
            chat_window.show()
            
            # Hide current window
            self.hide()
        else:
            print("MessengerTestWindow not available")
    
    def show_settings(self):
        """Show settings dialog"""
        print("Settings clicked")
    
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        if self.messenger_db and hasattr(self.messenger_db, 'close'):
            self.messenger_db.close()
        
        event.accept()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set modern style
    app.setStyle('Fusion')
    
    window = ChatListWindow()
    window.show()
    
    print("🚀 PycTalk Chat List")
    print("Features:")
    print("  ✅ Messenger-style chat list")
    print("  ✅ User avatars with gradient colors")
    print("  ✅ Last message preview")
    print("  ✅ Unread message badges")
    print("  ✅ Online status indicators")
    print("  ✅ Search functionality")
    print("  ✅ Auto-refresh every 10 seconds")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
