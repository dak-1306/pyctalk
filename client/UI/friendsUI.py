import sys
sys.path.append('.')
sys.path.append('..')

try:
    from Chat1_1.chat_client import ChatWindow, ChatClient
except ImportError:
    # Fallback for demo mode
    ChatWindow = None
    ChatClient = None
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QLineEdit, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class FriendItem(QWidget):
    """Widget representing a friend in the friends list"""
    def __init__(self, username, is_online=True, last_message="", unread_count=0, parent_window=None):
        super().__init__()
        self.username = username
        self.is_online = is_online
        self.parent_window = parent_window
        self.setupUI(last_message, unread_count)
    
    def setupUI(self, last_message, unread_count):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Profile picture placeholder
        profile_pic = QLabel("👤")
        profile_pic.setFixedSize(50, 50)
        profile_pic.setStyleSheet("""
            background-color: #e4e6ea;
            border-radius: 25px;
            font-size: 20px;
            text-align: center;
        """)
        profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Friend info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Name and online status
        name_layout = QHBoxLayout()
        name_label = QLabel(self.username)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1c1e21;")
        
        if self.is_online:
            online_indicator = QLabel("●")
            online_indicator.setStyleSheet("color: #42b883; font-size: 12px;")
            name_layout.addWidget(online_indicator)
        
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        
        # Last message
        if last_message:
            message_label = QLabel(last_message)
            message_label.setStyleSheet("font-size: 13px; color: #65676b;")
            message_label.setWordWrap(True)
        else:
            message_label = QLabel("Click to start chatting")
            message_label.setStyleSheet("font-size: 13px; color: #bcc0c4;")
        
        info_layout.addLayout(name_layout)
        info_layout.addWidget(message_label)
        
        layout.addWidget(profile_pic)
        layout.addLayout(info_layout)
        
        # Unread count
        if unread_count > 0:
            unread_label = QLabel(str(unread_count))
            unread_label.setFixedSize(25, 25)
            unread_label.setStyleSheet("""
                background-color: #e41e3f;
                color: white;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            """)
            unread_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(unread_label)
        else:
            layout.addStretch()
        
        self.setLayout(layout)
        
        # Make clickable
        self.setStyleSheet("""
            FriendItem:hover {
                background-color: #f2f3f5;
            }
        """)
        
    def mousePressEvent(self, event):
        """Handle click to open chat"""
        if self.parent_window and hasattr(self.parent_window, 'openChat'):
            self.parent_window.openChat(self.username)

class Ui_FriendsWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("FriendsWindow")
        MainWindow.setMinimumSize(400, 600)
        MainWindow.resize(400, 600)
        MainWindow.setWindowTitle("PycTalk - Friends")
        
        # Central widget
        self.centralwidget = QWidget(parent=MainWindow)
        
        # Main layout
        main_layout = QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            background-color: #4267B2;
            border-bottom: 1px solid #ddd;
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Chats")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        
        # New chat button
        self.btnNewChat = QPushButton("+ New")
        self.btnNewChat.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btnNewChat)
        
        # Search bar
        search_widget = QWidget()
        search_widget.setFixedHeight(50)
        search_widget.setStyleSheet("background-color: white; border-bottom: 1px solid #ddd;")
        
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(15, 10, 15, 10)
        
        self.txtSearch = QLineEdit()
        self.txtSearch.setPlaceholderText("🔍 Search friends...")
        self.txtSearch.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: none;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #e4e6ea;
            }
        """)
        
        search_layout.addWidget(self.txtSearch)
        
        # Friends list
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        self.friendsWidget = QWidget()
        self.friendsLayout = QVBoxLayout(self.friendsWidget)
        self.friendsLayout.setContentsMargins(0, 0, 0, 0)
        self.friendsLayout.setSpacing(0)
        
        self.scrollArea.setWidget(self.friendsWidget)
        
        # Add components to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(search_widget)
        main_layout.addWidget(self.scrollArea)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Add sample friends - pass MainWindow as parent_window will be set later
        # We'll call this from FriendsWindow after it's fully initialized
    
    def addSampleFriends(self, parent_window=None):
        """Add sample friends for demo"""
        sample_friends = [
            ("Alice", True, "Hey! How are you doing?", 2),
            ("Bob", True, "See you tomorrow! 👋", 0),
            ("Charlie", False, "Thanks for the help", 1),
            ("David", True, "👍", 0),
            ("Emma", True, "Can we meet up later?", 3),
            ("Frank", False, "Good night! 😴", 0),
        ]
        
        for username, is_online, last_msg, unread in sample_friends:
            self.addFriend(username, is_online, last_msg, unread, parent_window)
    
    def addFriend(self, username, is_online=True, last_message="", unread_count=0, parent_window=None):
        """Add a friend to the list"""
        friend_item = FriendItem(username, is_online, last_message, unread_count, parent_window)
        self.friendsLayout.addWidget(friend_item)

class FriendsWindow(QMainWindow):
    """Main friends window that can open chat windows"""
    def __init__(self, username, client=None):
        super().__init__()
        self.username = username
        self.client = client
        self.ui = Ui_FriendsWindow()
        self.ui.setupUi(self)
        
        # Connect events
        self.ui.btnNewChat.clicked.connect(self.newChat)
        
        # Add sample friends after initialization
        self.ui.addSampleFriends(self)
        
    def openChat(self, friend_username):
        """Open chat window with a friend"""
        if ChatWindow is None:
            # Demo mode - show message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Demo Mode", f"Would open chat with {friend_username}")
            return
            
        if self.client and hasattr(self.client, 'socket'):
            # Open with real connection
            chat_window = ChatWindow(self.username, friend_username, self.client.socket)
        else:
            # Open for demo/testing
            chat_window = ChatWindow(self.username, friend_username, None)
        
        chat_window.show()
        # Store reference to prevent garbage collection
        if not hasattr(self, 'chat_windows'):
            self.chat_windows = []
        self.chat_windows.append(chat_window)
    
    def newChat(self):
        """Start a new chat (placeholder)"""
        from PyQt6.QtWidgets import QInputDialog
        username, ok = QInputDialog.getText(self, 'New Chat', 'Enter friend username:')
        if ok and username:
            self.openChat(username)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = FriendsWindow("current_user")
    window.show()
    sys.exit(app.exec())
