from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from .chat_window_widget import ChatWindow
from .friend_list_window import FriendListWindow

class MessengerMainWindow(QtWidgets.QMainWindow):
    """Main messenger application window"""
    
    def __init__(self, username="Guest", user_id=None, parent=None):
        print("[DEBUG] MessengerMainWindow.__init__ called")
        super().__init__(parent)
        self.username = username
        self.current_user_id = user_id if user_id is not None else 1
        

        
        self._setup_ui()
        
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
        print("[DEBUG] MessengerMainWindow._open_chat_window called")
        """Open chat window for selected friend"""
        # Add current user info to chat data
        chat_data['current_user_id'] = self.current_user_id
        chat_data['current_username'] = self.username
        # Truyền pyctalk_client vào ChatWindow
        pyctalk_client = getattr(self, 'pyctalk_client', None)
        chat_window = ChatWindow(chat_data, pyctalk_client=pyctalk_client)
        chat_window.back_clicked.connect(self._show_friend_list)
        chat_window.message_sent.connect(self._handle_message_sent)
        self.stacked_widget.addWidget(chat_window)
        self.stacked_widget.setCurrentWidget(chat_window)
        

        
        print(f"Opened chat with {chat_data.get('friend_name', 'Unknown')} (ID: {chat_data.get('friend_id')})")
    

    

    
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
    



def main():
    """Main function to run messenger application"""
    import sys
    from client.Request.handle_request_client import AsyncPycTalkClient

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    # Đăng nhập lấy thông tin user
    client = AsyncPycTalkClient()
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
    # Truyền client vào main_window để dùng cho ChatWindow
    main_window.pyctalk_client = client
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
