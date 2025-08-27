from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
import asyncio

class SentRequestItem(QtWidgets.QWidget):
    """Widget for individual sent friend request with actions"""
    cancel_requested = pyqtSignal(dict)  # request_data
    
    def __init__(self, request_data, parent=None):
        super().__init__(parent)
        self.request_data = request_data
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        # Avatar placeholder
        avatar_label = QtWidgets.QLabel("👤")
        avatar_label.setFixedSize(45, 45)
        avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #f39c12;
                border-radius: 22px;
                background-color: #fef9e7;
                font-size: 20px;
            }
        """)
        layout.addWidget(avatar_label)
        
        # Request info
        info_layout = QtWidgets.QVBoxLayout()
        
        # Receiver name
        receiver_name = self.request_data.get('receiver_username', 'Unknown')
        name_label = QtWidgets.QLabel(f"<b>{receiver_name}</b>")
        name_label.setStyleSheet("font-size: 15px; color: #2c3e50;")
        
        # Status and date
        created_at = self.request_data.get('created_at', '')
        if created_at:
            # Format date if needed
            date_str = str(created_at).split()[0] if ' ' in str(created_at) else str(created_at)
            status_label = QtWidgets.QLabel(f"📅 Đã gửi: {date_str}")
        else:
            status_label = QtWidgets.QLabel("📅 Đã gửi lời mời")
        status_label.setStyleSheet("color: #f39c12; font-size: 12px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(status_label)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Status badge
        status_badge = QtWidgets.QLabel("⏳ Đang chờ")
        status_badge.setStyleSheet("""
            QLabel {
                background-color: #f39c12;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        status_badge.setFixedHeight(24)
        layout.addWidget(status_badge)
        
        # Cancel button
        cancel_btn = QtWidgets.QPushButton("🗑️ Thu hồi")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        cancel_btn.clicked.connect(lambda: self.cancel_requested.emit(self.request_data))
        layout.addWidget(cancel_btn)
        
        # Add border to the item
        self.setStyleSheet("""
            SentRequestItem {
                border: 1px solid #f1c40f;
                border-radius: 8px;
                background-color: #fffbf0;
                margin: 2px;
            }
            SentRequestItem:hover {
                background-color: #fef5e7;
                border-color: #f39c12;
            }
        """)

class SentRequestsWindow(QtWidgets.QDialog):
    """Window to manage sent friend requests"""
    
    def __init__(self, client, username, parent=None):
        super().__init__(parent)
        self.client = client
        self.username = username
        self.sent_requests = []
        
        self.setWindowTitle("Lời mời kết bạn đã gửi")
        self.setFixedSize(650, 600)
        self.setModal(True)
        
        # Set window flags to ensure it appears on top
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.WindowTitleHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        
        self._setup_ui()
        
        # Load sent requests on startup
        asyncio.create_task(self._load_sent_requests())
        
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("📤 Lời mời kết bạn đã gửi")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        refresh_btn = QtWidgets.QPushButton("🔄 Làm mới")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(lambda: asyncio.create_task(self._load_sent_requests()))
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-size: 12px;
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
        
        # Info label
        info_label = QtWidgets.QLabel("💡 Đây là danh sách những lời mời kết bạn bạn đã gửi và đang chờ phản hồi")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 8px; background-color: #ecf0f1; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Đang tải danh sách...")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Sent requests list area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
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
        
        self.requests_container = QtWidgets.QWidget()
        self.requests_layout = QtWidgets.QVBoxLayout(self.requests_container)
        self.requests_layout.setContentsMargins(10, 10, 10, 10)
        self.requests_layout.setSpacing(8)
        self.requests_layout.addStretch()
        
        scroll_area.setWidget(self.requests_container)
        layout.addWidget(scroll_area)
        
        # Footer with statistics
        self.stats_label = QtWidgets.QLabel("📊 Thống kê: 0 lời mời đang chờ")
        self.stats_label.setStyleSheet("color: #34495e; font-size: 12px; padding: 5px;")
        layout.addWidget(self.stats_label)
        
    async def _load_sent_requests(self):
        """Load sent friend requests from server"""
        try:
            self.status_label.setText("Đang tải...")
            
            response = await self.client.send_request("get_sent_friend_requests", {
                "username": self.username
            })
            
            print(f"[DEBUG] Sent requests response: {response}")
            
            if response and response.get("status") == "ok":
                self.sent_requests = response.get("data", [])
                self._display_sent_requests(self.sent_requests)
                
                count = len(self.sent_requests)
                if count == 0:
                    self.status_label.setText("Bạn chưa gửi lời mời kết bạn nào")
                    self.stats_label.setText("📊 Thống kê: 0 lời mời đang chờ")
                else:
                    self.status_label.setText(f"Có {count} lời mời đang chờ phản hồi")
                    self.stats_label.setText(f"📊 Thống kê: {count} lời mời đang chờ")
            else:
                self.status_label.setText("Lỗi tải dữ liệu")
                self.stats_label.setText("📊 Thống kê: Lỗi tải dữ liệu")
                print(f"[ERROR] Failed to load sent requests: {response}")
                
        except Exception as e:
            self.status_label.setText("Lỗi kết nối")
            self.stats_label.setText("📊 Thống kê: Lỗi kết nối")
            print(f"[ERROR] Exception loading sent requests: {e}")
            
    def _display_sent_requests(self, requests):
        """Display sent requests in the UI"""
        # Clear existing items (except stretch)
        while self.requests_layout.count() > 1:
            item = self.requests_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add request items
        for request in requests:
            request_item = SentRequestItem(request)
            request_item.cancel_requested.connect(self._handle_cancel_request)
            self.requests_layout.insertWidget(self.requests_layout.count() - 1, request_item)
            
    def _handle_cancel_request(self, request_data):
        """Handle request to cancel a sent friend request"""
        receiver_name = request_data.get('receiver_username')
        
        # Confirm cancellation
        reply = QtWidgets.QMessageBox.question(
            self, "Xác nhận", 
            f"Bạn có chắc chắn muốn thu hồi lời mời kết bạn gửi tới {receiver_name}?",
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            asyncio.create_task(self._cancel_friend_request(receiver_name))
            
    async def _cancel_friend_request(self, receiver_username):
        """Cancel a sent friend request"""
        try:
            print(f"[DEBUG] Cancelling friend request to: {receiver_username}")
            response = await self.client.send_request("cancel_friend_request", {
                "sender_username": self.username,
                "receiver_username": receiver_username
            })
            
            print(f"[DEBUG] Cancel request response: {response}")
            
            if response and response.get("status") == "ok":
                QtWidgets.QMessageBox.information(
                    self, "Thành công", 
                    f"Đã thu hồi lời mời kết bạn gửi tới {receiver_username}"
                )
                
                # Reload sent requests list
                await self._load_sent_requests()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Lỗi", 
                    f"Không thể thu hồi lời mời: {response.get('message', 'Unknown error')}"
                )
                
        except Exception as e:
            print(f"[ERROR] Exception cancelling friend request: {e}")
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {str(e)}")
