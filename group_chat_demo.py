"""
Demo script để test các cải thiện giao diện Group Chat
"""
import sys
import asyncio
from PyQt6 import QtWidgets
from qasync import QEventLoop, QApplication

# Import các component cần thiết
from client.Group_chat.embedded_group_chat_widget import EmbeddedGroupChatWidget
from client.Login.login_signIn import LoginWindow

class GroupChatDemo(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Group Chat UI Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Mock data cho demo
        self.mock_client = MockClient()
        self.mock_user_id = "1"
        self.mock_username = "test_user"
        self.mock_group_data = {
            "group_id": "1",
            "group_name": "Nhóm Demo",
            "created_by": "1"
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập UI demo"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Tiêu đề demo
        title = QtWidgets.QLabel("🎨 Group Chat UI Demo - Các cải thiện mới:")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #0084FF;
                padding: 10px;
                background-color: #f7f8fa;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Danh sách tính năng
        features = QtWidgets.QLabel("""
        ✨ Các cải thiện mới:
        • Emoji picker với popup menu đa dạng
        • Typing indicator khi gõ tin nhắn
        • Dark mode toggle với animation mượt mà
        • Responsive design cho các màn hình khác nhau
        • Message reactions với animation
        • Cải thiện animations và hover effects
        • Theme support toàn diện (light/dark)
        """)
        features.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                padding: 10px;
                background-color: #ffffff;
                border: 1px solid #e4e6ea;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        features.setWordWrap(True)
        layout.addWidget(features)
        
        # Group chat widget
        self.group_chat = EmbeddedGroupChatWidget(
            self.mock_client,
            self.mock_user_id,
            self.mock_username,
            self.mock_group_data
        )
        layout.addWidget(self.group_chat)
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
    def create_control_panel(self):
        """Tạo panel điều khiển để test các tính năng"""
        panel = QtWidgets.QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #f7f8fa;
                border-top: 1px solid #e4e6ea;
                padding: 10px;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(panel)
        
        # Button để thêm tin nhắn demo
        add_message_btn = QtWidgets.QPushButton("📝 Thêm tin nhắn demo")
        add_message_btn.clicked.connect(self.add_demo_message)
        layout.addWidget(add_message_btn)
        
        # Button để test typing indicator
        typing_btn = QtWidgets.QPushButton("⌨️ Test typing indicator")
        typing_btn.clicked.connect(self.test_typing_indicator)
        layout.addWidget(typing_btn)
        
        # Button để test emoji picker
        emoji_btn = QtWidgets.QPushButton("😊 Test emoji picker")
        emoji_btn.clicked.connect(self.test_emoji_picker)
        layout.addWidget(emoji_btn)
        
        # Button để toggle theme
        theme_btn = QtWidgets.QPushButton("🌓 Toggle theme")
        theme_btn.clicked.connect(self.toggle_demo_theme)
        layout.addWidget(theme_btn)
        
        layout.addStretch()
        return panel
    
    def add_demo_message(self):
        """Thêm tin nhắn demo"""
        import random
        messages = [
            "Xin chào mọi người! 👋",
            "Hôm nay thời tiết đẹp quá! ☀️",
            "Ai muốn đi chơi không? 🎮",
            "Project này hay quá! 👍",
            "Cảm ơn mọi người đã hỗ trợ! ❤️"
        ]
        
        message = random.choice(messages)
        is_sent = random.choice([True, False])
        sender_name = "user_demo" if not is_sent else None
        
        self.group_chat.add_message(
            message, 
            is_sent, 
            sender_name=sender_name,
            show_sender_name=not is_sent
        )
    
    def test_typing_indicator(self):
        """Test typing indicator"""
        self.group_chat.show_typing_indicator("Alice")
    
    def test_emoji_picker(self):
        """Test emoji picker"""
        self.group_chat._show_emoji_picker()
    
    def toggle_demo_theme(self):
        """Toggle theme cho demo"""
        self.group_chat.toggle_theme()

class MockClient:
    """Mock client để demo"""
    def __init__(self):
        self.connection = None
    
    async def send_json(self, data):
        """Mock send_json method"""
        print(f"[MOCK] Sending: {data}")
        return {"success": True}

def main():
    """Main function để chạy demo"""
    app = QApplication(sys.argv)
    
    # Setup qasync event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Tạo và hiển thị demo window
    demo = GroupChatDemo()
    demo.show()
    
    # Chạy event loop
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
