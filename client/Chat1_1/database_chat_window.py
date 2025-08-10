# Chat 1-1 Window với Database Integration
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                            QScrollArea, QLineEdit, QPushButton, QLabel, 
                            QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QCursor

# Import database và UI
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from UI.chatUI import MessageBubble
    from database.messenger_db import MessengerDatabase
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    MessengerDatabase = None

class DatabaseChatWindow(QMainWindow):
    """Chat window sử dụng database thật với giao diện Messenger"""
    
    def __init__(self, current_user_id, friend_id, friend_name="Friend", current_username="You"):
        super().__init__()
        self.current_user_id = current_user_id
        self.friend_id = friend_id
        self.friend_name = friend_name
        self.current_username = current_username
        
        # Khởi tạo database
        if MessengerDatabase:
            self.messenger_db = MessengerDatabase()
        else:
            self.messenger_db = None
            print("Warning: Database not available")
        
        # Lưu timestamp tin nhắn cuối để check tin nhắn mới
        self.last_message_time = None
        
        self.setup_ui()
        self.load_chat_history()
        
        # Auto refresh timer để check tin nhắn mới
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_new_messages)
        self.refresh_timer.start(3000)  # 3 giây check 1 lần
    
    def setup_ui(self):
        """Thiết lập giao diện chat"""
        self.setWindowTitle(f"Chat với {self.friend_name}")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Messages area
        self.create_messages_area(main_layout)
        
        # Input area
        self.create_input_area(main_layout)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
        """)
    
    def create_header(self, main_layout):
        """Tạo header với thông tin friend"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background-color: #4267B2;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Back button
        self.btn_back = QPushButton("← Quay lại")
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_back.clicked.connect(self.go_back)
        
        # Friend avatar (placeholder)
        avatar = QLabel(self.friend_name[0].upper())
        avatar.setFixedSize(60, 60)
        avatar.setStyleSheet("""
            QLabel {
                background-color: #FF6B6B;
                color: white;
                border-radius: 30px;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Friend info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        friend_name_label = QLabel(self.friend_name)
        friend_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        status_label = QLabel("● Online")
        status_label.setStyleSheet("""
            QLabel {
                color: #42b883;
                font-size: 14px;
            }
        """)
        
        info_layout.addWidget(friend_name_label)
        info_layout.addWidget(status_label)
        
        # Settings button
        btn_settings = QPushButton("⚙")
        btn_settings.setFixedSize(45, 45)
        btn_settings.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        header_layout.addWidget(self.btn_back)
        header_layout.addWidget(avatar)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        header_layout.addWidget(btn_settings)
        
        main_layout.addWidget(header)
    
    def create_messages_area(self, main_layout):
        """Tạo khu vực hiển thị tin nhắn"""
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
                background-color: #f0f2f5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #c4c4c4;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Messages widget
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(15, 15, 15, 15)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()  # Push messages to bottom
        
        self.scroll_area.setWidget(self.messages_widget)
        main_layout.addWidget(self.scroll_area)
    
    def create_input_area(self, main_layout):
        """Tạo khu vực nhập tin nhắn"""
        input_area = QWidget()
        input_area.setFixedHeight(80)
        input_area.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #e4e6ea;
            }
        """)
        
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        # Attach button
        btn_attach = QPushButton("📎")
        btn_attach.setFixedSize(50, 50)
        btn_attach.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #e4e6ea;
            }
        """)
        btn_attach.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Message input
        self.txt_message = QLineEdit()
        self.txt_message.setPlaceholderText("Nhập tin nhắn...")
        self.txt_message.setFixedHeight(50)
        self.txt_message.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: none;
                border-radius: 25px;
                padding: 0 20px;
                font-size: 16px;
            }
            QLineEdit:focus {
                background-color: #e4e6ea;
                outline: none;
            }
        """)
        self.txt_message.returnPressed.connect(self.send_message)
        
        # Send button
        self.btn_send = QPushButton("➤")
        self.btn_send.setFixedSize(50, 50)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #0084FF;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #006bd6;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_send.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_send.clicked.connect(self.send_message)
        
        input_layout.addWidget(btn_attach)
        input_layout.addWidget(self.txt_message)
        input_layout.addWidget(self.btn_send)
        
        main_layout.addWidget(input_area)
    
    def add_message_to_ui(self, message_text, is_sent, timestamp=None):
        """Thêm tin nhắn vào giao diện"""
        # Remove stretch trước khi thêm message
        item_count = self.messages_layout.count()
        if item_count > 0:
            last_item = self.messages_layout.takeAt(item_count - 1)
            if last_item.spacerItem():
                del last_item
        
        # Tạo message bubble
        message_bubble = MessageBubble(message_text, is_sent, timestamp)
        self.messages_layout.addWidget(message_bubble)
        
        # Add stretch lại để push messages xuống dưới
        self.messages_layout.addStretch()
        
        # Auto scroll xuống dưới
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Scroll xuống tin nhắn mới nhất"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def load_chat_history(self):
        """Load lịch sử chat từ database"""
        if not self.messenger_db:
            # Nếu không có database, thêm tin nhắn mẫu
            self.add_sample_messages()
            return
        
        try:
            messages = self.messenger_db.get_chat_history(
                self.current_user_id, 
                self.friend_id, 
                limit=50
            )
            
            for msg in messages:
                self.add_message_to_ui(
                    msg['content'], 
                    msg['is_sent'], 
                    msg['timestamp']
                )
                
                # Cập nhật last message time
                if messages and len(messages) > 0:
                    self.last_message_time = messages[-1]['timestamp']
                else:
                    self.last_message_time = None
            
            print(f"✅ Loaded {len(messages)} messages from database")
            
        except Exception as e:
            print(f"Error loading chat history: {e}")
            self.add_sample_messages()
    
    def add_sample_messages(self):
        """Thêm tin nhắn mẫu nếu không có database"""
        sample_messages = [
            ("Chào bạn! Bạn có khỏe không?", False),
            ("Chào! Mình khỏe, cảm ơn bạn. Còn bạn thì sao?", True),
            ("Mình cũng ổn. Project PycTalk này tiến triển như thế nào rồi?", False),
            ("Đang làm giao diện chat giống Messenger đây! 😊", True),
            ("Wow nghe hay đấy! Khi nào demo được?", False),
        ]
        
        for message, is_sent in sample_messages:
            self.add_message_to_ui(message, is_sent)
    
    def send_message(self):
        """Gửi tin nhắn mới"""
        message_text = self.txt_message.text().strip()
        if not message_text:
            return
        
        try:
            if self.messenger_db:
                # Gửi qua database
                result = self.messenger_db.send_message(
                    self.current_user_id,
                    self.friend_id,
                    message_text
                )
                
                if result['success']:
                    # Thêm vào UI
                    self.add_message_to_ui(message_text, True, result['timestamp'])
                    self.txt_message.clear()
                    self.last_message_time = result['timestamp']
                    print(f"✅ Message sent: {message_text}")
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không thể gửi tin nhắn: {result.get('error', 'Unknown error')}")
            else:
                # Chỉ hiển thị trong UI (demo mode)
                self.add_message_to_ui(message_text, True)
                self.txt_message.clear()
                print(f"Message sent (demo): {message_text}")
                
                # Simulate reply sau 2 giây
                QTimer.singleShot(2000, lambda: self.simulate_reply(message_text))
                
        except Exception as e:
            print(f"Error sending message: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể gửi tin nhắn: {str(e)}")
    
    def simulate_reply(self, original_message):
        """Simulate phản hồi tự động (demo mode)"""
        replies = [
            "OK, mình hiểu rồi! 👍",
            "Cảm ơn bạn!",
            "Haha được đó 😄",
            "Nghe hay quá!",
            f"Bạn vừa nói: '{original_message[:20]}...' đúng không?"
        ]
        import random
        reply = random.choice(replies)
        self.add_message_to_ui(reply, False)
    
    def check_new_messages(self):
        """Kiểm tra tin nhắn mới từ database"""
        if not self.messenger_db or not self.last_message_time:
            return
        
        try:
            # Lấy tin nhắn mới hơn last_message_time
            messages = self.messenger_db.get_chat_history(
                self.current_user_id,
                self.friend_id,
                limit=10
            )
            
            # Filter tin nhắn mới từ friend
            new_messages = [
                msg for msg in messages 
                if msg['timestamp'] > self.last_message_time and not msg['is_sent']
            ]
            
            # Thêm tin nhắn mới vào UI
            for msg in new_messages:
                self.add_message_to_ui(msg['content'], msg['is_sent'], msg['timestamp'])
                self.last_message_time = msg['timestamp']
            
            if new_messages:
                print(f"✅ Received {len(new_messages)} new messages")
                
        except Exception as e:
            print(f"Error checking new messages: {e}")
    
    def go_back(self):
        """Quay lại danh sách chat"""
        self.refresh_timer.stop()
        self.close()
    
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        if self.messenger_db and hasattr(self.messenger_db, 'close'):
            self.messenger_db.close()
        
        event.accept()

# Test function
def main():
    """Test chat window"""
    app = QApplication(sys.argv)
    
    # Test với user_id=1 chat với user_id=2
    window = DatabaseChatWindow(
        current_user_id=1,
        friend_id=2,
        friend_name="Trần Thị B",
        current_username="Bạn"
    )
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
