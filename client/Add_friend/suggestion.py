from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
from Request.handle_request_client import PycTalkClient

class SuggestionFriendWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.client = PycTalkClient()
        self.setWindowTitle("Gợi ý kết bạn")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.resize(400, 600)
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.load_suggestions()

    def load_suggestions(self):
        # Kết nối đến server và lấy danh sách gợi ý
        try:
            if not self.client.connect():
                print("❌ Không thể kết nối đến server để lấy gợi ý")
                return
                
            request = {
                "action": "get_suggestions",
                "data": {"username": self.username}
            }
            response = self.client.send_json(request)
            
            if response and response.get("status") == "ok":
                for user in response.get("data", []):
                    self.add_user_item(user)
            else:
                print("❌ Không thể lấy danh sách gợi ý từ server")
                
        except Exception as e:
            print(f"❌ Lỗi khi lấy gợi ý: {e}")
        finally:
            self.client.disconnect()

    def add_user_item(self, user):
        item = QListWidgetItem()
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(user)
        label.setStyleSheet("font-size: 14px;")
        btn = QPushButton("Kết bạn")
        btn.setStyleSheet("background-color: #3a3a3a; color: white; padding: 5px;")
        btn.clicked.connect(lambda _, u=user: self.send_friend_request(u))
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #2e2e2e;")
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def send_friend_request(self, to_user):
        try:
            client = PycTalkClient()
            if not client.connect():
                print("❌ Không thể kết nối đến server để gửi lời mời kết bạn")
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
                print(f"✅ Đã gửi lời mời kết bạn đến {to_user}")
            else:
                print(f"❌ Không thể gửi lời mời kết bạn đến {to_user}")
                
        except Exception as e:
            print(f"❌ Kết bạn thất bại: {e}")
        finally:
            client.disconnect()
