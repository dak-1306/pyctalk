from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
import asyncio

class FriendRequestItem(QtWidgets.QWidget):
    """Widget for individual friend request item"""
    request_accepted = pyqtSignal(str)  # username
    request_rejected = pyqtSignal(str)  # username
    
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Avatar placeholder
        avatar_label = QtWidgets.QLabel("👤")
        avatar_label.setFixedSize(40, 40)
        avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                border-radius: 20px;
                background-color: #f0f0f0;
                font-size: 20px;
            }
        """)
        layout.addWidget(avatar_label)
        
        # Username and request info
        info_layout = QtWidgets.QVBoxLayout()
        username_label = QtWidgets.QLabel(f"<b>{self.username}</b>")
        username_label.setStyleSheet("font-size: 14px;")
        request_label = QtWidgets.QLabel("muốn kết bạn với bạn")
        request_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(username_label)
        info_layout.addWidget(request_label)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        accept_btn = QtWidgets.QPushButton("Chấp nhận")
        accept_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        accept_btn.clicked.connect(lambda: self.request_accepted.emit(self.username))
        
        reject_btn = QtWidgets.QPushButton("Từ chối")
        reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        reject_btn.clicked.connect(lambda: self.request_rejected.emit(self.username))
        
        button_layout.addWidget(accept_btn)
        button_layout.addWidget(reject_btn)
        layout.addLayout(button_layout)
        
        # Add border to the item
        self.setStyleSheet("""
            FriendRequestItem {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                margin: 2px;
            }
            FriendRequestItem:hover {
                background-color: #f9f9f9;
            }
        """)

class FriendRequestsWindow(QtWidgets.QDialog):
    """Window to display and manage friend requests"""
    friend_added = pyqtSignal(dict)  # Emit when friend is accepted
    
    def __init__(self, client, username, parent=None):
        super().__init__(parent)
        self.client = client
        self.username = username
        self.setWindowTitle("Lời mời kết bạn")
        self.setFixedSize(500, 600)
        self.setModal(True)  # Make it modal
        
        # Set window flags to ensure it appears on top
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.WindowTitleHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        
        self._setup_ui()
        
        # Load friend requests on startup
        asyncio.create_task(self._load_friend_requests())
        
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("Lời mời kết bạn")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        refresh_btn = QtWidgets.QPushButton("🔄 Làm mới")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_btn.clicked.connect(lambda: asyncio.create_task(self._load_friend_requests()))
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4757;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff3838;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(close_btn)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)
        
        # Scroll area for friend requests
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #fafafa;
            }
        """)
        
        self.requests_widget = QtWidgets.QWidget()
        self.requests_layout = QtWidgets.QVBoxLayout(self.requests_widget)
        self.requests_layout.setContentsMargins(10, 10, 10, 10)
        self.requests_layout.setSpacing(10)
        self.requests_layout.addStretch()
        
        self.scroll_area.setWidget(self.requests_widget)
        layout.addWidget(self.scroll_area)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Đang tải...")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
    async def _load_friend_requests(self):
        """Load friend requests from server"""
        try:
            self.status_label.setText("Đang tải...")
            
            response = await self.client.send_request("get_friend_requests", {
                "username": self.username
            })
            
            if response and response.get("status") == "ok":
                requests = response.get("data", [])
                self._display_requests(requests)
                
                if not requests:
                    self.status_label.setText("Không có lời mời kết bạn nào")
                else:
                    self.status_label.setText(f"Có {len(requests)} lời mời kết bạn")
            else:
                self.status_label.setText("Lỗi tải dữ liệu")
                print(f"[ERROR] Failed to load friend requests: {response}")
                
        except Exception as e:
            self.status_label.setText("Lỗi kết nối")
            print(f"[ERROR] Exception loading friend requests: {e}")
            
    def _display_requests(self, requests):
        """Display friend requests in the UI"""
        # Clear existing items (except stretch)
        while self.requests_layout.count() > 1:
            item = self.requests_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add request items
        for username in requests:
            request_item = FriendRequestItem(username)
            request_item.request_accepted.connect(self._handle_accept_request)
            request_item.request_rejected.connect(self._handle_reject_request)
            self.requests_layout.insertWidget(self.requests_layout.count() - 1, request_item)
            
    def _handle_accept_request(self, username):
        """Handle accepting a friend request"""
        asyncio.create_task(self._accept_friend_request(username))
        
    def _handle_reject_request(self, username):
        """Handle rejecting a friend request"""
        asyncio.create_task(self._reject_friend_request(username))
        
    async def _accept_friend_request(self, from_username):
        """Accept a friend request"""
        try:
            print(f"[DEBUG] Accepting friend request from: {from_username}")
            response = await self.client.send_request("handle_friend_request", {
                "action": "accept",
                "from_username": from_username,
                "to_username": self.username
            })
            
            print(f"[DEBUG] Accept response: {response}")
            
            if response and response.get("status") == "ok":
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    f"Đã chấp nhận lời mời kết bạn từ {from_username}"
                )
                
                # Emit signal to update friends list
                self.friend_added.emit({
                    'friend_name': from_username,
                    'friend_id': None,  # Will be filled by parent
                    'last_message': '',
                    'last_message_time': '',
                    'unread_count': 0
                })
                
                # Reload requests
                await self._load_friend_requests()
            else:
                error_msg = response.get('message', 'Unknown error')
                
                # Check if it's a duplicate friendship error
                if "Duplicate entry" in error_msg and "unique_friendship" in error_msg:
                    # They are already friends, just remove the friend request
                    QtWidgets.QMessageBox.information(
                        self, "Thông báo", 
                        f"Bạn và {from_username} đã là bạn bè rồi. Đã xóa lời mời kết bạn."
                    )
                    
                    # Emit signal anyway to refresh friends list
                    self.friend_added.emit({
                        'friend_name': from_username,
                        'friend_id': None,
                        'last_message': '',
                        'last_message_time': '',
                        'unread_count': 0
                    })
                    
                    # Reload requests to remove this one
                    await self._load_friend_requests()
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "Lỗi", 
                        f"Không thể chấp nhận lời mời: {error_msg}"
                    )
                
        except Exception as e:
            print(f"[ERROR] Exception in accept: {e}")
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {str(e)}")
            
    async def _reject_friend_request(self, from_username):
        """Reject a friend request"""
        try:
            response = await self.client.send_request("handle_friend_request", {
                "action": "reject",
                "from_username": from_username,
                "to_username": self.username
            })
            
            if response and response.get("status") == "ok":
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    f"Đã từ chối lời mời kết bạn từ {from_username}"
                )
                
                # Reload requests
                await self._load_friend_requests()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Lỗi", 
                    f"Không thể từ chối lời mời: {response.get('message', 'Unknown error')}"
                )
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {str(e)}")
