import sys
import os
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget

# Import database and chat UI
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from UI.chatUI import Ui_ChatWindow
    from Chat1_1.chat_client import ChatWindow
    from Chat1_1.database_chat import DatabaseChatWindow
    from database.messenger_db import MessengerDatabase
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    MessengerDatabase = None
    DatabaseChatWindow = None

class ChatListItem(QWidget):
    # Signal khi click vào item
    clicked = pyqtSignal(dict)
    
    def __init__(self, chat_data):
        super().__init__()
        self.chat_data = chat_data
        self.setupUI()
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        
        # Hover effect
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover, True)
        
    def setupUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Avatar
        avatar = QtWidgets.QLabel()
        avatar.setFixedSize(60, 60)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {self.chat_data.get('avatar_color', '#0084FF')};
                border-radius: 30px;
                color: white;
                font-weight: bold;
                font-size: 24px;
            }}
        """)
        avatar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar.setText(self.chat_data['name'][0].upper())
        
        # Thông tin chat
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Tên và thời gian
        name_time_layout = QHBoxLayout()
        name_time_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QtWidgets.QLabel(self.chat_data['name'])
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1C1E21;
            }
        """)
        
        time_label = QtWidgets.QLabel(self.chat_data.get('time', '2 phút'))
        time_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #65676B;
            }
        """)
        
        name_time_layout.addWidget(name_label)
        name_time_layout.addStretch()
        name_time_layout.addWidget(time_label)
        
        # Tin nhắn cuối và unread badge
        message_layout = QHBoxLayout()
        message_layout.setContentsMargins(0, 0, 0, 0)
        
        last_message = QtWidgets.QLabel(self.chat_data.get('last_message', 'Tin nhắn mới...'))
        last_message.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {'#1C1E21' if self.chat_data.get('unread', 0) > 0 else '#65676B'};
                font-weight: {'bold' if self.chat_data.get('unread', 0) > 0 else 'normal'};
            }}
        """)
        last_message.setWordWrap(True)
        
        # Unread badge
        if self.chat_data.get('unread', 0) > 0:
            unread_badge = QtWidgets.QLabel(str(self.chat_data['unread']))
            unread_badge.setFixedSize(20, 20)
            unread_badge.setStyleSheet("""
                QLabel {
                    background-color: #FF3040;
                    color: white;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            unread_badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            message_layout.addWidget(last_message)
            message_layout.addStretch()
            message_layout.addWidget(unread_badge)
        else:
            message_layout.addWidget(last_message)
            message_layout.addStretch()
        
        info_layout.addLayout(name_time_layout)
        info_layout.addLayout(message_layout)
        
        layout.addWidget(avatar)
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
        
        # Style cho item
        self.setStyleSheet("""
            ChatListItem {
                background-color: white;
                border-bottom: 1px solid #E4E6EA;
            }
            ChatListItem:hover {
                background-color: #F2F3F5;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit(self.chat_data)
        super().mousePressEvent(event)

class Ui_ChatListWindow(object):
    def setupUi(self, ChatListWindow):
        self.main_window = ChatListWindow  # Lưu reference đến main window
        self.current_user_id = 1  # TODO: Lấy từ login session
        
        # Khởi tạo database connection
        if MessengerDatabase:
            self.messenger_db = MessengerDatabase()
        else:
            self.messenger_db = None
            print("Warning: Database not available, using sample data")
        
        ChatListWindow.setObjectName("ChatListWindow")
        ChatListWindow.resize(400, 700)
        ChatListWindow.setWindowTitle("PycTalk - Tin nhắn")
        ChatListWindow.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)
        
        # Central widget
        self.centralwidget = QtWidgets.QWidget(ChatListWindow)
        ChatListWindow.setCentralWidget(self.centralwidget)
        
        # Main layout
        main_layout = QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Search bar
        search_bar = self.create_search_bar()
        main_layout.addWidget(search_bar)
        
        # Chat list
        self.chat_scroll = self.create_chat_list()
        main_layout.addWidget(self.chat_scroll)
        
        # Load conversations from database
        self.load_conversations()
    
    def create_header(self):
        header = QtWidgets.QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QWidget {
                background-color: #4267B2;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # App title
        title = QtWidgets.QLabel("Tin nhắn")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        # Settings button
        self.btnSettings = QtWidgets.QPushButton("⚙")
        self.btnSettings.setFixedSize(45, 45)
        self.btnSettings.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 20px;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.btnSettings.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.btnSettings)
        
        return header
    
    def create_search_bar(self):
        search_widget = QtWidgets.QWidget()
        search_widget.setFixedHeight(70)
        search_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #E4E6EA;
            }
        """)
        
        layout = QHBoxLayout(search_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.txtSearch = QtWidgets.QLineEdit()
        self.txtSearch.setPlaceholderText("🔍 Tìm kiếm tin nhắn...")
        self.txtSearch.setFixedHeight(40)
        self.txtSearch.setStyleSheet("""
            QLineEdit {
                background-color: #F0F2F5;
                border: none;
                border-radius: 20px;
                padding: 0 15px;
                font-size: 15px;
            }
            QLineEdit:focus {
                background-color: #E4E6EA;
            }
        """)
        
        layout.addWidget(self.txtSearch)
        
        return search_widget
    
    def create_chat_list(self):
        # Scroll area cho danh sách chat
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #F0F2F5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #C4C4C4;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #A0A0A0;
            }
        """)
        
        # Widget chứa danh sách
        self.chat_list_widget = QWidget()
        self.chat_list_layout = QVBoxLayout(self.chat_list_widget)
        self.chat_list_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_list_layout.setSpacing(0)
        
        scroll.setWidget(self.chat_list_widget)
        
        return scroll
    
    def load_conversations(self):
        """Load cuộc trò chuyện từ database"""
        if not self.messenger_db:
            # Fallback to sample data if no database
            self.load_sample_chats()
            return
        
        try:
            # Lấy conversations từ database
            conversations = self.messenger_db.get_user_conversations(self.current_user_id)
            
            # Nếu không có conversation nào, tạo sample data và tải lại
            if not conversations:
                print("No conversations found, creating sample data...")
                self.messenger_db.create_sample_messages(self.current_user_id)
                conversations = self.messenger_db.get_user_conversations(self.current_user_id)
            
            # Clear existing items
            for i in reversed(range(self.chat_list_layout.count())):
                child = self.chat_list_layout.itemAt(i)
                if child.widget():
                    child.widget().setParent(None)
            
            # Add conversation items
            for conv_data in conversations:
                chat_item = ChatListItem(conv_data)
                chat_item.clicked.connect(self.on_chat_selected)
                self.chat_list_layout.addWidget(chat_item)
            
            # Add stretch để đẩy items lên top
            self.chat_list_layout.addStretch()
            
            print(f"✅ Loaded {len(conversations)} conversations from database")
            
        except Exception as e:
            print(f"Error loading conversations from database: {e}")
            # Fallback to sample data
            self.load_sample_chats()
    
    def refresh_conversations(self):
        """Refresh danh sách cuộc trò chuyện"""
        self.load_conversations()
    
    def load_sample_chats(self):
        """Load dữ liệu mẫu (fallback)"""
        # Dữ liệu mẫu cho danh sách chat
        sample_chats = [
            {
                'name': 'Nguyễn Văn A',
                'last_message': 'Chào bạn! Hôm nay thế nào?',
                'time': '2 phút',
                'unread': 3,
                'avatar_color': '#FF6B6B',
                'user_id': 1
            },
            {
                'name': 'Trần Thị B',
                'last_message': 'Ok, mai mình gặp nhau nhé',
                'time': '15 phút',
                'unread': 0,
                'avatar_color': '#4ECDC4',
                'user_id': 2
            },
            {
                'name': 'Lê Minh C',
                'last_message': 'Cảm ơn bạn nhiều! 👍',
                'time': '1 giờ',
                'unread': 1,
                'avatar_color': '#45B7D1',
                'user_id': 3
            },
            {
                'name': 'Phạm Thu D',
                'last_message': 'Bạn đã xem tin nhắn chưa?',
                'time': '3 giờ',
                'unread': 0,
                'avatar_color': '#96CEB4',
                'user_id': 4
            },
            {
                'name': 'Hoàng Văn E',
                'last_message': 'Meeting lúc 3h chiều nhé',
                'time': 'Hôm qua',
                'unread': 2,
                'avatar_color': '#FECA57',
                'user_id': 5
            },
            {
                'name': 'Đặng Thị F',
                'last_message': 'Chúc bạn ngủ ngon! 😴',
                'time': 'Hôm qua',
                'unread': 0,
                'avatar_color': '#FF9FF3',
                'user_id': 6
            },
            {
                'name': 'Vũ Minh G',
                'last_message': 'Dự án này khó quá...',
                'time': '2 ngày',
                'unread': 0,
                'avatar_color': '#54A0FF',
                'user_id': 7
            }
        ]
        
        for chat_data in sample_chats:
            chat_item = ChatListItem(chat_data)
            chat_item.clicked.connect(self.on_chat_selected)
            self.chat_list_layout.addWidget(chat_item)
        
        # Add stretch để đẩy items lên top
        self.chat_list_layout.addStretch()
    
    def on_chat_selected(self, chat_data):
        print(f"Opening chat with: {chat_data['name']} (ID: {chat_data['user_id']})")
        
        try:
            # Sử dụng DatabaseChatWindow nếu có
            if DatabaseChatWindow and self.messenger_db:
                self.chat_window = DatabaseChatWindow(
                    current_user_id=self.current_user_id,
                    friend_id=chat_data['user_id'],
                    friend_name=chat_data['name']
                )
                self.chat_window.show()
                
                # Ẩn cửa sổ danh sách tin nhắn
                self.main_window.hide()
                
                print(f"✅ Opened database chat with {chat_data['name']}")
            else:
                # Fallback to simple chat UI
                self.open_simple_chat(chat_data)
            
        except Exception as e:
            print(f"Error opening chat: {e}")
            # Fallback: chỉ hiển thị thông báo
            QtWidgets.QMessageBox.information(
                self.main_window,
                "Mở chat",
                f"Sẽ mở chat với {chat_data['name']}\n(ID: {chat_data['user_id']})"
            )
    
    def open_simple_chat(self, chat_data):
        """Mở giao diện chat đơn giản"""
        from PyQt6.QtWidgets import QMainWindow
        
        # Tạo cửa sổ chat mới
        self.chat_window = QMainWindow()
        self.chat_ui = Ui_ChatWindow()
        self.chat_ui.setupUi(self.chat_window)
        
        # Cập nhật thông tin friend
        if hasattr(self.chat_ui, 'lblFriendName'):
            self.chat_ui.lblFriendName.setText(chat_data['name'])
        
        self.chat_window.setWindowTitle(f"Chat với {chat_data['name']}")
        self.chat_window.show()
        
        # Ẩn cửa sổ danh sách tin nhắn  
        self.main_window.hide()

class ChatListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ChatListWindow()
        self.ui.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = ChatListWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
