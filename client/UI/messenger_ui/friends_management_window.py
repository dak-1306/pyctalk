from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
import asyncio

class FriendItem(QtWidgets.QWidget):
    """Widget for individual friend item with actions"""
    chat_requested = pyqtSignal(dict)  # friend_data
    remove_requested = pyqtSignal(dict)  # friend_data
    
    def __init__(self, friend_data, parent=None):
        super().__init__(parent)
        self.friend_data = friend_data
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Avatar placeholder
        avatar_label = QtWidgets.QLabel("👤")
        avatar_label.setFixedSize(50, 50)
        avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #3498db;
                border-radius: 25px;
                background-color: #ecf0f1;
                font-size: 24px;
            }
        """)
        layout.addWidget(avatar_label)
        
        # Friend info
        info_layout = QtWidgets.QVBoxLayout()
        name_label = QtWidgets.QLabel(f"<b>{self.friend_data.get('friend_name', 'Unknown')}</b>")
        name_label.setStyleSheet("font-size: 16px; color: #2c3e50;")
        
        status_label = QtWidgets.QLabel("Đang hoạt động")
        status_label.setStyleSheet("color: #27ae60; font-size: 12px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(status_label)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Chat button
        chat_btn = QtWidgets.QPushButton("💬 Nhắn tin")
        chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        chat_btn.clicked.connect(lambda: self.chat_requested.emit(self.friend_data))
        
        # Remove button
        remove_btn = QtWidgets.QPushButton("🗑️ Xóa")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.friend_data))
        
        button_layout.addWidget(chat_btn)
        button_layout.addWidget(remove_btn)
        layout.addLayout(button_layout)
        
        # Add border to the item
        self.setStyleSheet("""
            FriendItem {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                margin: 2px;
            }
            FriendItem:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
        """)

class FriendsManagementWindow(QtWidgets.QDialog):
    """Window to manage friends list"""
    chat_friend_requested = pyqtSignal(dict)  # Emit when user wants to chat with a friend
    
    def __init__(self, client, username, user_id, parent=None):
        super().__init__(parent)
        self.client = client
        self.username = username
        self.user_id = user_id
        self.friends_list = []
        
        self.setWindowTitle("Danh sách bạn bè")
        self.setFixedSize(600, 700)
        self.setModal(True)
        
        # Set window flags to ensure it appears on top
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.WindowTitleHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        
        self._setup_ui()
        
        # Load friends on startup
        asyncio.create_task(self._load_friends())
        
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("👥 Danh sách bạn bè")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        
        refresh_btn = QtWidgets.QPushButton("🔄 Làm mới")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(lambda: asyncio.create_task(self._load_friends()))
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("🔍")
        search_label.setStyleSheet("font-size: 16px;")
        
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm bạn bè...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self._filter_friends)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Đang tải danh sách bạn bè...")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Friends list area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #95a5a6;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.friends_container = QtWidgets.QWidget()
        self.friends_layout = QtWidgets.QVBoxLayout(self.friends_container)
        self.friends_layout.setContentsMargins(10, 10, 10, 10)
        self.friends_layout.setSpacing(8)
        self.friends_layout.addStretch()
        
        scroll_area.setWidget(self.friends_container)
        layout.addWidget(scroll_area)
        
    async def _load_friends(self):
        """Load friends from server"""
        try:
            self.status_label.setText("Đang tải...")
            
            response = await self.client.send_request("get_friends", {
                "username": self.username
            })
            
            print(f"[DEBUG] Friends response: {response}")
            
            if response and response.get("status") == "ok":
                self.friends_list = response.get("data", [])
                self._display_friends(self.friends_list)
                
                if not self.friends_list:
                    self.status_label.setText("Bạn chưa có bạn bè nào")
                else:
                    self.status_label.setText(f"Có {len(self.friends_list)} bạn bè")
            else:
                self.status_label.setText("Lỗi tải dữ liệu")
                print(f"[ERROR] Failed to load friends: {response}")
                
        except Exception as e:
            self.status_label.setText("Lỗi kết nối")
            print(f"[ERROR] Exception loading friends: {e}")
            
    def _display_friends(self, friends):
        """Display friends in the UI"""
        # Clear existing items (except stretch)
        while self.friends_layout.count() > 1:
            item = self.friends_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add friend items
        for friend in friends:
            # Ensure friend has required data
            friend_data = {
                'friend_id': friend.get('friend_id'),
                'friend_name': friend.get('friend_name'),
                'current_user_id': self.user_id,
                'last_message': '',
                'last_message_time': '',
                'unread_count': 0
            }
            
            friend_item = FriendItem(friend_data)
            friend_item.chat_requested.connect(self._handle_chat_request)
            friend_item.remove_requested.connect(self._handle_remove_request)
            self.friends_layout.insertWidget(self.friends_layout.count() - 1, friend_item)
            
    def _filter_friends(self, search_text):
        """Filter friends based on search text"""
        search_text = search_text.lower()
        
        # Find all FriendItem widgets
        for i in range(self.friends_layout.count()):
            item = self.friends_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), FriendItem):
                friend_item = item.widget()
                friend_name = friend_item.friend_data.get('friend_name', '').lower()
                
                # Show/hide based on search match
                is_visible = search_text in friend_name
                friend_item.setVisible(is_visible)
    
    def _handle_chat_request(self, friend_data):
        """Handle request to chat with a friend"""
        print(f"[DEBUG] Chat requested with: {friend_data}")
        # Emit signal to parent to open chat window
        self.chat_friend_requested.emit(friend_data)
        # Close this window
        self.close()
        
    def _handle_remove_request(self, friend_data):
        """Handle request to remove a friend"""
        friend_name = friend_data.get('friend_name')
        
        # Confirm removal
        reply = QtWidgets.QMessageBox.question(
            self, "Xác nhận", 
            f"Bạn có chắc chắn muốn xóa {friend_name} khỏi danh sách bạn bè?",
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            asyncio.create_task(self._remove_friend(friend_name))
            
    async def _remove_friend(self, friend_name):
        """Remove a friend"""
        try:
            print(f"[DEBUG] Removing friend: {friend_name}")
            response = await self.client.send_request("remove_friend", {
                "username": self.username,
                "friend_name": friend_name
            })
            
            print(f"[DEBUG] Remove friend response: {response}")
            
            if response and response.get("status") == "ok":
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    f"Đã xóa {friend_name} khỏi danh sách bạn bè"
                )
                
                # Reload friends list
                await self._load_friends()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Lỗi", 
                    f"Không thể xóa bạn bè: {response.get('message', 'Unknown error')}"
                )
                
        except Exception as e:
            print(f"[ERROR] Exception removing friend: {e}")
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {str(e)}")
