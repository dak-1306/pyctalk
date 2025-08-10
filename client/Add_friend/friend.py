from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QHBoxLayout,
    QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from Request.handle_request_client import PycTalkClient

class FriendManagementWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.client = PycTalkClient()
        self.setWindowTitle("Quản lý bạn bè")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.resize(500, 700)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Tạo tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Tab 1: Danh sách bạn bè
        self.friends_tab = QWidget()
        self.friends_layout = QVBoxLayout(self.friends_tab)
        self.friends_list = QListWidget()
        self.friends_layout.addWidget(self.friends_list)
        self.tab_widget.addTab(self.friends_tab, "Bạn bè")
        
        # Tab 2: Lời mời kết bạn
        self.requests_tab = QWidget()
        self.requests_layout = QVBoxLayout(self.requests_tab)
        self.requests_list = QListWidget()
        self.requests_layout.addWidget(self.requests_list)
        self.tab_widget.addTab(self.requests_tab, "Lời mời")
        
        # Tab 3: Gợi ý kết bạn
        self.suggestions_tab = QWidget()
        self.suggestions_layout = QVBoxLayout(self.suggestions_tab)
        self.suggestions_list = QListWidget()
        self.suggestions_layout.addWidget(self.suggestions_list)
        self.tab_widget.addTab(self.suggestions_tab, "Gợi ý")
        
        # Load dữ liệu
        self.load_friends()
        self.load_requests()
        self.load_suggestions()

    def load_friends(self):
        """Tải danh sách bạn bè"""
        try:
            if not self.client.connect():
                return
                
            request = {
                "action": "get_friends",
                "data": {"username": self.username}
            }
            response = self.client.send_json(request)
            
            if response and response.get("status") == "ok":
                for friend in response.get("data", []):
                    self.add_friend_item(friend)
                    
        except Exception as e:
            print(f"❌ Lỗi khi tải danh sách bạn bè: {e}")
        finally:
            self.client.disconnect()

    def load_requests(self):
        """Tải lời mời kết bạn"""
        try:
            if not self.client.connect():
                return
                
            request = {
                "action": "get_friend_requests",
                "data": {"username": self.username}
            }
            response = self.client.send_json(request)
            
            if response and response.get("status") == "ok":
                for req in response.get("data", []):
                    self.add_request_item(req)
                    
        except Exception as e:
            print(f"❌ Lỗi khi tải lời mời kết bạn: {e}")
        finally:
            self.client.disconnect()

    def load_suggestions(self):
        """Tải gợi ý kết bạn"""
        try:
            if not self.client.connect():
                return
                
            request = {
                "action": "get_suggestions",
                "data": {"username": self.username}
            }
            response = self.client.send_json(request)
            
            if response and response.get("status") == "ok":
                for user in response.get("data", []):
                    self.add_suggestion_item(user)
                    
        except Exception as e:
            print(f"❌ Lỗi khi tải gợi ý kết bạn: {e}")
        finally:
            self.client.disconnect()

    def add_friend_item(self, friend_name):
        """Thêm item bạn bè vào list"""
        item = QListWidgetItem()
        widget = QWidget()
        layout = QHBoxLayout()
        
        label = QLabel(friend_name)
        label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # Nút chat
        chat_btn = QPushButton("Chat")
        chat_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        chat_btn.clicked.connect(lambda _, f=friend_name: self.start_chat(f))
        
        # Nút xóa bạn
        remove_btn = QPushButton("Xóa")
        remove_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        remove_btn.clicked.connect(lambda _, f=friend_name: self.remove_friend(f))
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(chat_btn)
        layout.addWidget(remove_btn)
        
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #2e2e2e; margin: 2px;")
        item.setSizeHint(widget.sizeHint())
        self.friends_list.addItem(item)
        self.friends_list.setItemWidget(item, widget)

    def add_request_item(self, from_user):
        """Thêm lời mời kết bạn vào list"""
        item = QListWidgetItem()
        widget = QWidget()
        layout = QHBoxLayout()
        
        label = QLabel(f"{from_user} muốn kết bạn")
        label.setStyleSheet("font-size: 14px;")
        
        # Nút chấp nhận
        accept_btn = QPushButton("Chấp nhận")
        accept_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        accept_btn.clicked.connect(lambda _, u=from_user: self.accept_request(u))
        
        # Nút từ chối
        reject_btn = QPushButton("Từ chối")
        reject_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        reject_btn.clicked.connect(lambda _, u=from_user: self.reject_request(u))
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(accept_btn)
        layout.addWidget(reject_btn)
        
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #2e2e2e; margin: 2px;")
        item.setSizeHint(widget.sizeHint())
        self.requests_list.addItem(item)
        self.requests_list.setItemWidget(item, widget)

    def add_suggestion_item(self, user_name):
        """Thêm gợi ý kết bạn vào list"""
        item = QListWidgetItem()
        widget = QWidget()
        layout = QHBoxLayout()
        
        label = QLabel(user_name)
        label.setStyleSheet("font-size: 14px;")
        
        # Nút kết bạn
        add_btn = QPushButton("Kết bạn")
        add_btn.setStyleSheet("background-color: #3a3a3a; color: white; padding: 5px;")
        add_btn.clicked.connect(lambda _, u=user_name: self.send_friend_request(u))
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(add_btn)
        
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #2e2e2e; margin: 2px;")
        item.setSizeHint(widget.sizeHint())
        self.suggestions_list.addItem(item)
        self.suggestions_list.setItemWidget(item, widget)

    def start_chat(self, friend_name):
        """Bắt đầu chat với bạn bè"""
        # TODO: Implement chat functionality
        QMessageBox.information(self, "Chat", f"Bắt đầu chat với {friend_name}")

    def remove_friend(self, friend_name):
        """Xóa bạn bè"""
        reply = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa {friend_name} khỏi danh sách bạn bè?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if not self.client.connect():
                    return
                    
                request = {
                    "action": "remove_friend",
                    "data": {
                        "username": self.username,
                        "friend_name": friend_name
                    }
                }
                response = self.client.send_json(request)
                
                if response and response.get("status") == "ok":
                    QMessageBox.information(self, "Thành công", f"Đã xóa {friend_name} khỏi danh sách bạn bè")
                    # Refresh list
                    self.friends_list.clear()
                    self.load_friends()
                    
            except Exception as e:
                print(f"❌ Lỗi khi xóa bạn bè: {e}")
            finally:
                self.client.disconnect()

    def accept_request(self, from_user):
        """Chấp nhận lời mời kết bạn"""
        try:
            if not self.client.connect():
                return
                
            request = {
                "action": "accept_friend",
                "data": {
                    "username": self.username,
                    "from_user": from_user
                }
            }
            response = self.client.send_json(request)
            
            if response and response.get("status") == "ok":
                QMessageBox.information(self, "Thành công", f"Đã chấp nhận lời mời từ {from_user}")
                # Refresh lists
                self.requests_list.clear()
                self.friends_list.clear()
                self.load_requests()
                self.load_friends()
                
        except Exception as e:
            print(f"❌ Lỗi khi chấp nhận lời mời: {e}")
        finally:
            self.client.disconnect()

    def reject_request(self, from_user):
        """Từ chối lời mời kết bạn"""
        try:
            if not self.client.connect():
                return
                
            request = {
                "action": "reject_friend",
                "data": {
                    "username": self.username,
                    "from_user": from_user
                }
            }
            response = self.client.send_json(request)
            
            if response and response.get("status") == "ok":
                QMessageBox.information(self, "Thành công", f"Đã từ chối lời mời từ {from_user}")
                # Refresh list
                self.requests_list.clear()
                self.load_requests()
                
        except Exception as e:
            print(f"❌ Lỗi khi từ chối lời mời: {e}")
        finally:
            self.client.disconnect()

    def send_friend_request(self, to_user):
        """Gửi lời mời kết bạn"""
        try:
            client = PycTalkClient()
            if not client.connect():
                return
                
            request = {
                "action": "add_friend",
                "data": {
                    "from_user": self.username,
                    "to_user": to_user
                }
            }
            response = client.send_json(request)
            
            if response and response.get("status") == "ok":
                QMessageBox.information(self, "Thành công", f"Đã gửi lời mời kết bạn đến {to_user}")
                
        except Exception as e:
            print(f"❌ Lỗi khi gửi lời mời kết bạn: {e}")
        finally:
            client.disconnect()
