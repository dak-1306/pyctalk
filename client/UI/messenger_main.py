# PycTalk Messenger - Main Chat List với navigation đến chat chi tiết
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QLineEdit, QScrollArea, 
                            QListWidget, QListWidgetItem, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

# Add paths để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from UI.messenger_test import MessengerTestWindow
    from database.messenger_db import MessengerDatabase
except ImportError as e:
    print(f"Import warning: {e}")
    MessengerTestWindow = None
    MessengerDatabase = None

class ChatListItem(QFrame):
    """Widget cho mỗi item trong danh sách chat"""
    
    clicked = pyqtSignal(dict)  # Signal khi được click
    
    def __init__(self, chat_data, parent=None):
        super().__init__(parent)
        self.chat_data = chat_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI cho chat item"""
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
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Avatar
        avatar = QLabel()
        avatar.setFixedSize(55, 55)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_avatar_color()};
                color: white;
                border-radius: 27px;
                font-size: 22px;
                font-weight: bold;
                border: 3px solid #e4e6ea;
            }}
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setText(self.chat_data.get('friend_name', 'U')[0].upper())
        
        # Chat info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Name
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
        if len(last_msg) > 50:
            last_msg = last_msg[:50] + "..."
            
        msg_label = QLabel(last_msg)
        msg_label.setStyleSheet("""
            QLabel {
                color: #8a8d91;
                font-size: 14px;
                font-weight: 400;
            }
        """)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(msg_label)
        
        # Time và status
        time_layout = QVBoxLayout()
        time_layout.setSpacing(5)
        
        time_label = QLabel(self.format_time(self.chat_data.get('last_message_time', '')))
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
            badge = QLabel(str(self.chat_data.get('unread_count')))
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
            time_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignRight)
        
        time_layout.addWidget(time_label)
        time_layout.addStretch()
        
        # Layout chính
        layout.addWidget(avatar)
        layout.addLayout(info_layout, 1)
        layout.addLayout(time_layout)
        
    def get_avatar_color(self):
        """Lấy màu avatar theo tên"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
        name = self.chat_data.get('friend_name', 'User')
        return colors[hash(name) % len(colors)]
    
    def format_time(self, timestamp):
        """Format thời gian hiển thị"""
        if not timestamp:
            return ""
        
        # Simplified time formatting
        if hasattr(timestamp, 'strftime'):
            return timestamp.strftime("%H:%M")
        else:
            return str(timestamp)[:5]  # Truncate for display
            
    def mousePressEvent(self, event):
        """Handle click event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.chat_data)
        super().mousePressEvent(event)

class MessengerChatList(QMainWindow):
    """Main window - danh sách chat giống Messenger"""
    
    def __init__(self):
        super().__init__()
        self.current_user_id = 1  # Giả sử user hiện tại
        self.current_username = "Nguyễn Văn A"
        
        # Test database connection
        if MessengerDatabase:
            try:
                self.messenger_db = MessengerDatabase()
                self.db_connected = True
            except Exception as e:
                self.messenger_db = None
                self.db_connected = False
                print(f"Database connection failed: {e}")
        else:
            self.messenger_db = None
            self.db_connected = False
        
        self.chat_windows = {}  # Lưu trữ các chat window đang mở
        self.setup_ui()
        self.load_conversations()
        
    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("PycTalk - Messenger")
        self.setMinimumSize(400, 600)
        self.resize(450, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        self.create_header(layout)
        
        # Search bar
        self.create_search_bar(layout)
        
        # Chat list
        self.create_chat_list(layout)
        
        # Apply main styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)
    
    def create_header(self, main_layout):
        """Tạo header với profile và settings"""
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
        
        # Profile avatar
        profile_avatar = QLabel()
        profile_avatar.setFixedSize(45, 45)
        profile_avatar.setStyleSheet("""
            QLabel {
                background-color: #FF6B6B;
                color: white;
                border-radius: 22px;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid rgba(255,255,255,0.3);
            }
        """)
        profile_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_avatar.setText(self.current_username[0])
        
        # Title
        title_label = QLabel("PycTalk")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        header_layout.addWidget(profile_avatar)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(settings_btn)
        
        main_layout.addWidget(header)
    
    def create_search_bar(self, main_layout):
        """Tạo thanh search"""
        search_container = QWidget()
        search_container.setFixedHeight(60)
        search_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #f0f2f5;
            }
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 10, 20, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search conversations...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 15px;
                color: #1c1e21;
            }
            QLineEdit:focus {
                background-color: #e4e6ea;
                border: 2px solid #0084FF;
            }
            QLineEdit::placeholder {
                color: #8a8d91;
            }
        """)
        self.search_input.textChanged.connect(self.filter_conversations)
        
        search_layout.addWidget(self.search_input)
        main_layout.addWidget(search_container)
    
    def create_chat_list(self, main_layout):
        """Tạo danh sách chat"""
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
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
                background-color: #c8c8c8;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Container for chat items
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(5)
        self.chat_layout.addStretch()  # Push items to top
        
        scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(scroll_area)
    
    def load_conversations(self):
        """Load danh sách conversations"""
        if self.messenger_db and self.db_connected:
            try:
                conversations = self.messenger_db.get_user_conversations(self.current_user_id)
                self.display_conversations(conversations)
            except Exception as e:
                print(f"Error loading conversations: {e}")
                self.load_sample_conversations()
        else:
            self.load_sample_conversations()
    
    def load_sample_conversations(self):
        """Load sample conversations for demo"""
        sample_conversations = [
            {
                'friend_id': 2,
                'friend_name': 'Trần Thị B',
                'last_message': 'Chào bạn! Bạn có khỏe không? 👋',
                'last_message_time': '10:30',
                'unread_count': 2
            },
            {
                'friend_id': 3,
                'friend_name': 'Lê Văn C',
                'last_message': 'Project PycTalk tiến triển thế nào rồi?',
                'last_message_time': '09:15',
                'unread_count': 0
            },
            {
                'friend_id': 4,
                'friend_name': 'Phạm Thị D',
                'last_message': 'Cảm ơn bạn về thông tin hữu ích! 🙏',
                'last_message_time': 'Yesterday',
                'unread_count': 0
            },
            {
                'friend_id': 5,
                'friend_name': 'Hoàng Văn E',
                'last_message': 'Hẹn gặp lại bạn sau nhé! 👋',
                'last_message_time': '2 days ago',
                'unread_count': 1
            },
            {
                'friend_id': 6,
                'friend_name': 'Ngô Thị F',
                'last_message': 'UI Messenger này đẹp quá! 😍',
                'last_message_time': '3 days ago',
                'unread_count': 0
            }
        ]
        self.display_conversations(sample_conversations)
    
    def display_conversations(self, conversations):
        """Hiển thị conversations trong UI"""
        # Clear existing items
        while self.chat_layout.count() > 1:  # Keep the stretch
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add conversation items
        for conv in conversations:
            chat_item = ChatListItem(conv)
            chat_item.clicked.connect(self.open_chat_window)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, chat_item)
    
    def filter_conversations(self, search_text):
        """Filter conversations based on search"""
        search_text = search_text.lower()
        
        # Simple filter implementation
        for i in range(self.chat_layout.count() - 1):  # -1 for stretch
            item = self.chat_layout.itemAt(i)
            if item.widget():
                chat_item = item.widget()
                friend_name = chat_item.chat_data.get('friend_name', '').lower()
                last_message = chat_item.chat_data.get('last_message', '').lower()
                
                should_show = (search_text in friend_name or 
                             search_text in last_message or 
                             search_text == '')
                
                chat_item.setVisible(should_show)
    
    def open_chat_window(self, chat_data):
        """Mở chat window khi click vào conversation"""
        friend_id = chat_data.get('friend_id')
        friend_name = chat_data.get('friend_name', 'Unknown')
        
        # Kiểm tra nếu chat window đã mở
        if friend_id in self.chat_windows:
            existing_window = self.chat_windows[friend_id]
            if existing_window.isVisible():
                existing_window.raise_()
                existing_window.activateWindow()
                return
        
        # Tạo chat window mới
        if MessengerTestWindow:
            try:
                chat_window = MessengerTestWindow()
                
                # Customize cho friend này
                chat_window.ui.lblFriendName.setText(friend_name)
                chat_window.ui.friendAvatar.setText(friend_name[0].upper())
                chat_window.ui.lblStatus.setText("● Active now")
                
                # Connect close event để cleanup
                original_close_event = chat_window.closeEvent
                def on_chat_closed(event):
                    if friend_id in self.chat_windows:
                        del self.chat_windows[friend_id]
                    if original_close_event:
                        original_close_event(event)
                    else:
                        event.accept()
                
                chat_window.closeEvent = on_chat_closed
                
                # Show window
                chat_window.show()
                self.chat_windows[friend_id] = chat_window
                
                print(f"✅ Opened chat with {friend_name} (ID: {friend_id})")
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể mở chat window: {str(e)}")
                print(f"Error opening chat window: {e}")
        else:
            QMessageBox.warning(self, "Lỗi", "MessengerTestWindow không khả dụng!")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Create main window
    main_window = MessengerChatList()
    main_window.show()
    
    print("🚀 PycTalk Messenger - Chat List")
    print("Features:")
    print("  ✅ Beautiful chat list interface")
    print("  ✅ Search conversations")
    print("  ✅ Click to open detailed chat")
    print("  ✅ Database integration")
    print("  ✅ Real-time conversation management")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
