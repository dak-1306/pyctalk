# Test Database Chat Integration
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QListWidget, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from Chat1_1.database_chat_window import DatabaseChatWindow
    from database.messenger_db import MessengerDatabase
except ImportError as e:
    print(f"Import error: {e}")
    DatabaseChatWindow = None
    MessengerDatabase = None

class ChatLauncher(QMainWindow):
    """Launcher để test các cuộc trò chuyện"""
    
    def __init__(self):
        super().__init__()
        self.current_user_id = 1  # Giả sử user hiện tại có ID = 1
        self.current_username = "Nguyễn Văn A"
        
        # Test database connection
        if MessengerDatabase:
            try:
                self.messenger_db = MessengerDatabase()
                self.db_status = "✅ Connected"
            except Exception as e:
                self.messenger_db = None
                self.db_status = f"❌ Error: {str(e)}"
        else:
            self.messenger_db = None
            self.db_status = "❌ Module not found"
        
        self.setup_ui()
        self.load_conversations()
    
    def setup_ui(self):
        """Thiết lập giao diện chính"""
        self.setWindowTitle("PycTalk - Database Chat Test")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🚀 PycTalk Database Chat Test")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Database status
        db_status_label = QLabel(f"Database Status: {self.db_status}")
        db_status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(db_status_label)
        
        # Current user info
        user_info = QLabel(f"Current User: {self.current_username} (ID: {self.current_user_id})")
        user_info.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #495057;
                padding: 10px;
                background-color: #e9ecef;
                border-radius: 8px;
            }
        """)
        layout.addWidget(user_info)
        
        # Conversations list
        layout.addWidget(QLabel("💬 Select a conversation to test:"))
        
        self.conversations_list = QListWidget()
        self.conversations_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #f1f3f4;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        self.conversations_list.itemDoubleClicked.connect(self.open_chat)
        layout.addWidget(self.conversations_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        btn_open_chat = QPushButton("💬 Open Chat")
        btn_open_chat.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        btn_open_chat.clicked.connect(self.open_chat)
        
        btn_test_db = QPushButton("🔧 Test Database")
        btn_test_db.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        btn_test_db.clicked.connect(self.test_database)
        
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        btn_refresh.clicked.connect(self.load_conversations)
        
        buttons_layout.addWidget(btn_open_chat)
        buttons_layout.addWidget(btn_test_db)
        buttons_layout.addWidget(btn_refresh)
        
        layout.addLayout(buttons_layout)
    
    def load_conversations(self):
        """Load danh sách cuộc trò chuyện"""
        self.conversations_list.clear()
        
        if self.messenger_db:
            try:
                conversations = self.messenger_db.get_user_conversations(self.current_user_id)
                
                for conv in conversations:
                    friend_name = conv.get('friend_name', f"User {conv.get('friend_id', 'Unknown')}")
                    last_message = conv.get('last_message', 'No messages')
                    last_time = conv.get('last_message_time', 'Never')
                    
                    item_text = f"👤 {friend_name}\n💭 {last_message}\n🕒 {last_time}"
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, conv)
                    self.conversations_list.addItem(item)
                
                if conversations:
                    print(f"✅ Loaded {len(conversations)} conversations")
                else:
                    # Thêm test conversations
                    self.add_test_conversations()
                    
            except Exception as e:
                print(f"Error loading conversations: {e}")
                self.add_test_conversations()
        else:
            self.add_test_conversations()
    
    def add_test_conversations(self):
        """Thêm các cuộc trò chuyện test"""
        test_conversations = [
            {
                'friend_id': 2,
                'friend_name': 'Trần Thị B',
                'last_message': 'Chào bạn! Bạn có khỏe không?',
                'last_message_time': '10:30 AM'
            },
            {
                'friend_id': 3,
                'friend_name': 'Lê Văn C',
                'last_message': 'Project PycTalk tiến triển thế nào rồi?',
                'last_message_time': '9:15 AM'
            },
            {
                'friend_id': 4,
                'friend_name': 'Phạm Thị D',
                'last_message': 'Cảm ơn bạn về thông tin!',
                'last_message_time': 'Yesterday'
            },
            {
                'friend_id': 5,
                'friend_name': 'Hoàng Văn E',
                'last_message': 'Hẹn gặp lại bạn sau!',
                'last_message_time': '2 days ago'
            }
        ]
        
        for conv in test_conversations:
            item_text = f"👤 {conv['friend_name']}\n💭 {conv['last_message']}\n🕒 {conv['last_message_time']}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, conv)
            self.conversations_list.addItem(item)
        
        print("✅ Added test conversations")
    
    def open_chat(self):
        """Mở cửa sổ chat"""
        current_item = self.conversations_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một cuộc trò chuyện!")
            return
        
        if not DatabaseChatWindow:
            QMessageBox.critical(self, "Lỗi", "DatabaseChatWindow module not available!")
            return
        
        conv_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            chat_window = DatabaseChatWindow(
                current_user_id=self.current_user_id,
                friend_id=conv_data['friend_id'],
                friend_name=conv_data['friend_name'],
                current_username=self.current_username
            )
            chat_window.show()
            
            print(f"✅ Opened chat with {conv_data['friend_name']} (ID: {conv_data['friend_id']})")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Cannot open chat window: {str(e)}")
            print(f"Error opening chat: {e}")
    
    def test_database(self):
        """Test database connection và operations"""
        if not self.messenger_db:
            QMessageBox.warning(self, "Database Test", 
                              "Database not available!\n\n" + 
                              "Please check:\n" +
                              "1. XAMPP is running\n" + 
                              "2. MySQL is started\n" + 
                              "3. Database schema is created")
            return
        
        try:
            # Test basic operations
            result_text = "📊 Database Test Results:\n\n"
            
            # Test get conversations
            conversations = self.messenger_db.get_user_conversations(self.current_user_id)
            result_text += f"✅ Found {len(conversations)} conversations\n"
            
            # Test send a test message
            test_result = self.messenger_db.send_message(
                self.current_user_id, 
                2, 
                "Test message from launcher"
            )
            if test_result['success']:
                result_text += "✅ Test message sent successfully\n"
            else:
                result_text += f"❌ Failed to send test message: {test_result.get('error', 'Unknown')}\n"
            
            # Test get chat history
            history = self.messenger_db.get_chat_history(self.current_user_id, 2, limit=5)
            result_text += f"✅ Retrieved {len(history)} messages from history\n"
            
            result_text += "\n🎉 Database is working correctly!"
            
            QMessageBox.information(self, "Database Test", result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Database Test Failed", 
                               f"Database test failed:\n\n{str(e)}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set app style
    app.setStyle('Fusion')
    
    launcher = ChatLauncher()
    launcher.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
