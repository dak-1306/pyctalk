import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QThread

# Import database and UI
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from UI.chatUI import Ui_ChatWindow, MessageBubble
    from database.messenger_db import MessengerDatabase
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    MessengerDatabase = None

class DatabaseChatWindow(QMainWindow):
    """Chat window sử dụng database thật"""
    
    def __init__(self, current_user_id, friend_id, friend_name="Friend"):
        super().__init__()
        self.current_user_id = current_user_id
        self.friend_id = friend_id
        self.friend_name = friend_name
        
        # Khởi tạo database
        if MessengerDatabase:
            self.messenger_db = MessengerDatabase()
        else:
            self.messenger_db = None
            print("Warning: Database not available")
        
        # Setup UI
        self.ui = Ui_ChatWindow()
        self.ui.setupUi(self)
        
        # Cập nhật thông tin friend
        self.setup_friend_info()
        
        # Connect events
        self.connect_events()
        
        # Load chat history
        self.load_chat_history()
        
        # Setup auto refresh (kiểm tra tin nhắn mới mỗi 2 giây)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_new_messages)
        self.refresh_timer.start(2000)  # 2 seconds
        
        # Lưu timestamp của tin nhắn cuối cùng để check tin nhắn mới
        self.last_message_time = None
    
    def setup_friend_info(self):
        """Cập nhật thông tin friend trong UI"""
        if hasattr(self.ui, 'lblFriendName'):
            self.ui.lblFriendName.setText(self.friend_name)
        
        self.setWindowTitle(f"Chat với {self.friend_name}")
        
        # Cập nhật avatar với chữ cái đầu
        if self.friend_name:
            first_letter = self.friend_name[0].upper()
            # TODO: Set avatar letter in UI if available
    
    def connect_events(self):
        """Connect các events"""
        # Send button
        if hasattr(self.ui, 'btnSend'):
            self.ui.btnSend.clicked.connect(self.send_message)
        
        # Enter key in text input
        if hasattr(self.ui, 'txtMessage'):
            self.ui.txtMessage.returnPressed.connect(self.send_message)
        
        # Back button  
        if hasattr(self.ui, 'btnBack'):
            self.ui.btnBack.clicked.connect(self.go_back)
    
    def load_chat_history(self):
        """Load lịch sử chat từ database"""
        if not self.messenger_db:
            return
        
        try:
            messages = self.messenger_db.get_chat_history(
                self.current_user_id, 
                self.friend_id, 
                limit=50
            )
            
            # Clear existing messages
            if hasattr(self.ui, 'messagesLayout'):
                for i in reversed(range(self.ui.messagesLayout.count())):
                    child = self.ui.messagesLayout.itemAt(i)
                    if child and child.widget():
                        child.widget().setParent(None)
            
            # Add messages to UI
            for msg in messages:
                self.add_message_to_ui(msg['content'], msg['is_sent'])
                
                # Update last message time
                if not self.last_message_time or msg['timestamp'] > self.last_message_time:
                    self.last_message_time = msg['timestamp']
            
            print(f"✅ Loaded {len(messages)} messages from database")
            
        except Exception as e:
            print(f"Error loading chat history: {e}")
    
    def add_message_to_ui(self, message, is_sent):
        """Thêm tin nhắn vào UI"""
        try:
            # Create message bubble
            message_bubble = MessageBubble(message, is_sent)
            
            # Add to messages layout
            if hasattr(self.ui, 'messagesLayout'):
                self.ui.messagesLayout.addWidget(message_bubble)
            elif hasattr(self.ui, 'messages_layout'):
                self.ui.messages_layout.addWidget(message_bubble)
            else:
                # Fallback: tìm layout chứa messages
                scroll_widget = None
                if hasattr(self.ui, 'scrollArea'):
                    scroll_widget = self.ui.scrollArea.widget()
                elif hasattr(self.ui, 'scroll_area'):
                    scroll_widget = self.ui.scroll_area.widget()
                
                if scroll_widget and scroll_widget.layout():
                    scroll_widget.layout().addWidget(message_bubble)
            
            # Scroll to bottom
            self.scroll_to_bottom()
            
        except Exception as e:
            print(f"Error adding message to UI: {e}")
    
    def scroll_to_bottom(self):
        """Scroll xuống tin nhắn mới nhất"""
        try:
            if hasattr(self.ui, 'scrollArea'):
                scrollbar = self.ui.scrollArea.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            elif hasattr(self.ui, 'scroll_area'):
                scrollbar = self.ui.scroll_area.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
        except:
            pass
    
    def send_message(self):
        """Gửi tin nhắn mới"""
        if not hasattr(self.ui, 'txtMessage'):
            return
        
        message_text = self.ui.txtMessage.text().strip()
        if not message_text:
            return
        
        try:
            # Gửi tin nhắn qua database
            if self.messenger_db:
                result = self.messenger_db.send_message(
                    self.current_user_id,
                    self.friend_id,
                    message_text
                )
                
                if result['success']:
                    # Thêm tin nhắn vào UI
                    self.add_message_to_ui(message_text, True)
                    
                    # Clear input
                    self.ui.txtMessage.clear()
                    
                    # Update last message time
                    self.last_message_time = result['timestamp']
                    
                    print(f"✅ Message sent: {message_text}")
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không thể gửi tin nhắn: {result.get('error', 'Unknown error')}")
            else:
                # Fallback: chỉ hiển thị tin nhắn trong UI
                self.add_message_to_ui(message_text, True)
                self.ui.txtMessage.clear()
                print(f"Message sent (no database): {message_text}")
                
        except Exception as e:
            print(f"Error sending message: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể gửi tin nhắn: {str(e)}")
    
    def check_new_messages(self):
        """Kiểm tra tin nhắn mới"""
        if not self.messenger_db or not self.last_message_time:
            return
        
        try:
            # Lấy tin nhắn mới hơn last_message_time
            messages = self.messenger_db.get_chat_history(
                self.current_user_id,
                self.friend_id,
                limit=10
            )
            
            # Filter tin nhắn mới
            new_messages = [
                msg for msg in messages 
                if msg['timestamp'] > self.last_message_time and not msg['is_sent']
            ]
            
            # Thêm tin nhắn mới vào UI
            for msg in new_messages:
                self.add_message_to_ui(msg['content'], msg['is_sent'])
                self.last_message_time = msg['timestamp']
            
            if new_messages:
                print(f"✅ Received {len(new_messages)} new messages")
                
        except Exception as e:
            print(f"Error checking new messages: {e}")
    
    def go_back(self):
        """Quay lại danh sách tin nhắn"""
        # Stop refresh timer
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        # Close this window
        self.close()
        
        # TODO: Hiển thị lại chat list window
        print("Going back to chat list...")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop refresh timer
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        # Close database connection
        if self.messenger_db:
            self.messenger_db.close()
        
        event.accept()

def main():
    """Test function"""
    app = QApplication(sys.argv)
    
    # Test với user_id=1 chat với user_id=2
    window = DatabaseChatWindow(
        current_user_id=1,
        friend_id=2,
        friend_name="Trần Thị B"
    )
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
