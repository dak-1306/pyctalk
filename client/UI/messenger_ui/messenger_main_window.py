from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from .chat_window_widget import ChatWindow
from .friend_list_window import FriendListWindow

try:
    from database.messenger_db import MessengerDatabase
except ImportError:
    MessengerDatabase = None


class MessengerMainWindow(QtWidgets.QMainWindow):
    """Main messenger application window"""
    
    def __init__(self, username="Guest", user_id=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.current_user_id = user_id if user_id is not None else 1
        
        # Database connection
        self.messenger_db = None
        self.db_connected = False
        self._init_database()
        
        self._setup_ui()
        
    def _init_database(self):
        """Initialize database connection"""
        if MessengerDatabase:
            try:
                self.messenger_db = MessengerDatabase()
                self.db_connected = True
            except Exception as e:
                print(f"Database connection failed: {e}")
    
    def _setup_ui(self):
        """Setup main messenger UI"""
        self.setWindowTitle("PycTalk - Messenger")
        self.setMinimumSize(400, 600)
        self.resize(450, 700)
        
        # Central widget with stacked layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Stacked widget for switching between views
        self.stacked_widget = QtWidgets.QStackedWidget()
        
        # Friend list view
        self.friend_list_widget = FriendListWindow(self.username, user_id=self.current_user_id)
        self.friend_list_widget.friend_selected.connect(self._open_chat_window)
        self.stacked_widget.addWidget(self.friend_list_widget)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        
        # Apply main styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)
    
    def _open_chat_window(self, chat_data):
        """Open chat window for selected friend"""
        # Add current user info to chat data
        chat_data['current_user_id'] = self.current_user_id
        chat_data['current_username'] = self.username
        
        # Create chat window
        chat_window = ChatWindow(chat_data)
        chat_window.back_clicked.connect(self._show_friend_list)
        chat_window.message_sent.connect(self._handle_message_sent)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(chat_window)
        self.stacked_widget.setCurrentWidget(chat_window)
        
        # Load message history if database is available
        if self.messenger_db and self.db_connected:
            self._load_message_history(chat_window, chat_data)
        
        print(f"Opened chat with {chat_data.get('friend_name', 'Unknown')} (ID: {chat_data.get('friend_id')})")
    
    def _load_message_history(self, chat_window, chat_data):
        """Load message history from database"""
        try:
            messages = self.messenger_db.get_chat_history(
                self.current_user_id, 
                chat_data.get('friend_id'),
                limit=50
            )
            if messages:
                chat_window.load_message_history(messages)
        except Exception as e:
            print(f"Error loading message history: {e}")
    
    def _handle_message_sent(self, message_text):
        """Handle when a message is sent"""
        # Get current chat window
        current_widget = self.stacked_widget.currentWidget()
        if isinstance(current_widget, ChatWindow) and self.messenger_db and self.db_connected:
            try:
                # Save message to database
                friend_id = current_widget.chat_data.get('friend_id')
                if friend_id:
                    self.messenger_db.send_message(
                        self.current_user_id,
                        friend_id,
                        message_text
                    )
                    print(f"Message saved to database: {message_text}")
            except Exception as e:
                print(f"Error saving message: {e}")
    
    def _show_friend_list(self):
        """Return to friend list view"""
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != self.friend_list_widget:
            self.stacked_widget.removeWidget(current_widget)
            current_widget.deleteLater()
        
        self.stacked_widget.setCurrentWidget(self.friend_list_widget)
        
        # Refresh conversations list
        self.friend_list_widget.refresh_conversations()
    
    def get_current_chat_data(self):
        """Get current chat data if in chat view"""
        current_widget = self.stacked_widget.currentWidget()
        if isinstance(current_widget, ChatWindow):
            return current_widget.chat_data
        return None
    
    def send_message_to_current_chat(self, message):
        """Send message to current chat (programmatically)"""
        current_widget = self.stacked_widget.currentWidget()
        if isinstance(current_widget, ChatWindow):
            current_widget.add_message(message, True)
            self._handle_message_sent(message)
    
    def receive_message_in_current_chat(self, message):
        """Receive message in current chat (for real-time updates)"""
        current_widget = self.stacked_widget.currentWidget()
        if isinstance(current_widget, ChatWindow):
            current_widget.add_message(message, False)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup database connection
        if self.messenger_db:
            try:
                # Close database connection if needed
                pass
            except:
                pass
        event.accept()


def main():
    """Main function to run messenger application"""
    import sys
    from client.Request.handle_request_client import PycTalkClient

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    # Đăng nhập lấy thông tin user
    client = PycTalkClient()
    print("Vui lòng đăng nhập để sử dụng Messenger:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    login_response = client.login(username, password)
    if not login_response or not login_response.get("success"):
        print("❌ Đăng nhập thất bại. Không thể khởi động Messenger.")
        sys.exit(1)

    user_id = client.get_user_id()
    username = client.get_username()

    main_window = MessengerMainWindow(username, user_id=user_id)
    main_window.show()

    print("🚀 PycTalk Messenger - Modular Application")
    print("Features:")
    print("  ✅ Modular architecture with separate widgets")
    print("  ✅ Beautiful Messenger-style interface")
    print("  ✅ Smooth navigation between friend list and chat")
    print("  ✅ Database integration support")
    print("  ✅ Real-time messaging capability")
    print("  ✅ Professional UI design")
    print("  ✅ Easy integration with main UI")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
