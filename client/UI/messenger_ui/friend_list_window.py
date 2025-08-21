from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from .chat_list_item_widget import ChatListItem

try:
    from database.messenger_db import MessengerDatabase
except ImportError:
    MessengerDatabase = None


class FriendListWindow(QtWidgets.QWidget):
    """Friend list window for messenger"""
    
    friend_selected = pyqtSignal(dict)  # Signal when friend is selected to chat
    
    def __init__(self, username="Guest", user_id=None, client=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.current_user_id = user_id
        # Nếu client chưa truyền vào, thử lấy từ parent (nếu có)
        if client is not None:
            self.client = client
        elif parent and hasattr(parent, 'client'):
            self.client = parent.client
        else:
            self.client = None
        self._setup_ui()
        self._load_conversations()
        
    # Đã bỏ kết nối database, chỉ lấy từ server
    
    def _setup_ui(self):
        """Setup friend list UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search bar
        self._create_search_bar(layout)
        
        # Friends list
        self._create_friends_list(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
    
    def _create_search_bar(self, main_layout):
        """Create search bar for filtering friends"""
        search_container = QtWidgets.QWidget()
        search_container.setFixedHeight(60)
        search_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #f0f2f5;
            }
        """)
        
        search_layout = QtWidgets.QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 10, 20, 10)
        
        self.search_input = QtWidgets.QLineEdit()
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
        self.search_input.textChanged.connect(self._filter_conversations)
        
        search_layout.addWidget(self.search_input)
        main_layout.addWidget(search_container)
    
    def _create_friends_list(self, main_layout):
        """Create scrollable friends list"""
        # Scroll area
        scroll_area = QtWidgets.QScrollArea()
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
        """)
        
        # Container for chat items
        self.friends_container = QtWidgets.QWidget()
        self.friends_layout = QtWidgets.QVBoxLayout(self.friends_container)
        self.friends_layout.setContentsMargins(10, 10, 10, 10)
        self.friends_layout.setSpacing(5)
        self.friends_layout.addStretch()
        
        scroll_area.setWidget(self.friends_container)
        main_layout.addWidget(scroll_area)
    
    def _load_conversations(self):
        """Lấy danh sách bạn bè từ server qua FriendClient"""
        if self.client is None:
            print("Không tìm thấy client để lấy danh sách bạn bè. Hãy truyền client khi khởi tạo FriendListWindow.")
            self._display_conversations([])
            return
        try:
            from Add_friend.friend import FriendClient
            friend_client = FriendClient(self.client)
            response = friend_client.get_friends()
            friends = response.get("data", []) if response and response.get("success") else []
            conversations = []
            for friend_name in friends:
                conversations.append({
                    'friend_id': None,  # Nếu server trả về cả id thì dùng id
                    'friend_name': friend_name,
                    'last_message': '',
                    'last_message_time': '',
                    'unread_count': 0
                })
            self._display_conversations(conversations)
        except Exception as e:
            print(f"Error loading friends: {e}")
            self._display_conversations([])
    
    # Đã bỏ dữ liệu mẫu, chỉ dùng dữ liệu thật từ database
    
    def _display_conversations(self, conversations):
        """Display conversations in the list"""
        # Clear existing items
        while self.friends_layout.count() > 1:  # Keep the stretch
            child = self.friends_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add conversation items
        for conv in conversations:
            chat_item = ChatListItem(conv)
            chat_item.clicked.connect(self._on_friend_selected)
            self.friends_layout.insertWidget(self.friends_layout.count() - 1, chat_item)
    
    def _on_friend_selected(self, chat_data):
        """Handle friend selection"""
        self.friend_selected.emit(chat_data)
    
    def _filter_conversations(self, search_text):
        """Filter conversations based on search text"""
        search_text = search_text.lower()
        
        # Find all ChatListItem widgets
        for i in range(self.friends_layout.count()):
            item = self.friends_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatListItem):
                chat_item = item.widget()
                friend_name = chat_item.chat_data.get('friend_name', '').lower()
                last_message = chat_item.chat_data.get('last_message', '').lower()
                
                # Show/hide based on search match
                is_visible = (search_text in friend_name or search_text in last_message)
                chat_item.setVisible(is_visible)
    
    def refresh_conversations(self):
        """Refresh conversation list"""
        self._load_conversations()
    
    def add_conversation(self, conversation_data):
        """Add a new conversation to the list"""
        chat_item = ChatListItem(conversation_data)
        chat_item.clicked.connect(self._on_friend_selected)
        self.friends_layout.insertWidget(self.friends_layout.count() - 1, chat_item)
    
    def update_conversation(self, friend_id, last_message, timestamp):
        """Update a conversation's last message"""
        # Find the conversation item and update it
        for i in range(self.friends_layout.count()):
            item = self.friends_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatListItem):
                chat_item = item.widget()
                if chat_item.chat_data.get('friend_id') == friend_id:
                    chat_item.chat_data['last_message'] = last_message
                    chat_item.chat_data['last_message_time'] = timestamp
                    chat_item.update_chat_data(chat_item.chat_data)
                    break
