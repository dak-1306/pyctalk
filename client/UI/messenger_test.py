# Test Messenger-style UI
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from UI.chatUI_clean import Ui_ChatWindow, MessageBubble
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class MessengerTestWindow(QMainWindow):
    """Test window cho giao diện Messenger"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_ChatWindow()
        self.ui.setupUi(self)
        
        # Set friend info
        self.ui.lblFriendName.setText("Trần Thị B")
        self.ui.friendAvatar.setText("T")
        self.ui.lblStatus.setText("● Active 2 minutes ago")
        
        # Add sample messages
        self.add_sample_messages()
        
        # Connect events
        self.setup_connections()
    
    def setup_connections(self):
        """Setup button connections"""
        self.ui.btnSend.clicked.connect(self.send_message)
        self.ui.txtMessage.returnPressed.connect(self.send_message)
        self.ui.txtMessage.textChanged.connect(self.on_text_changed)
        self.ui.btnBack.clicked.connect(self.close)
        
        # Mock connections for other buttons
        self.ui.btnCall.clicked.connect(lambda: print("📞 Voice call clicked"))
        self.ui.btnVideo.clicked.connect(lambda: print("📹 Video call clicked"))
        self.ui.btnInfo.clicked.connect(lambda: print("ⓘ Info clicked"))
        self.ui.btnAttach.clicked.connect(lambda: print("📎 Attach clicked"))
        self.ui.btnEmoji.clicked.connect(self.show_emoji_picker)
    
    def on_text_changed(self, text):
        """Enable/disable send button based on text"""
        self.ui.btnSend.setEnabled(bool(text.strip()))
    
    def add_sample_messages(self):
        """Add sample messages để test"""
        sample_messages = [
            ("Chào bạn! Bạn có khỏe không? 👋", False),
            ("Chào! Mình khỏe, cảm ơn bạn. Còn bạn thì sao? 😊", True),
            ("Mình cũng ổn. Project PycTalk này tiến triển như thế nào rồi?", False),
            ("Đang làm giao diện chat giống Messenger đây! Nhìn đẹp không? ✨", True),
            ("Wow nhìn rất đẹp và professional! Khi nào có thể demo được?", False),
            ("Có thể demo ngay bây giờ luôn! 🚀", True),
            ("Tuyệt vời! Giao diện này giống Messenger thật sự! 👍", False),
        ]
        
        for message, is_sent in sample_messages:
            self.add_message(message, is_sent)
        
        # Scroll to bottom after adding messages
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def add_message(self, message, is_sent):
        """Add message bubble to chat"""
        # Remove stretch nếu có
        layout = self.ui.messagesLayout
        if layout.count() > 0:
            last_item = layout.takeAt(layout.count() - 1)
            if last_item.spacerItem():
                del last_item
        
        # Add message bubble
        bubble = MessageBubble(message, is_sent)
        layout.addWidget(bubble)
        
        # Add stretch lại
        layout.addStretch()
        
        # Auto scroll
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Scroll to bottom of chat"""
        scrollbar = self.ui.scrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send new message"""
        text = self.ui.txtMessage.text().strip()
        if not text:
            return
        
        # Add sent message
        self.add_message(text, True)
        
        # Clear input
        self.ui.txtMessage.clear()
        
        # Simulate reply after 2 seconds
        QTimer.singleShot(2000, lambda: self.simulate_reply(text))
    
    def simulate_reply(self, original_message):
        """Simulate friend reply"""
        replies = [
            "Tôi hiểu rồi! 👍",
            "Cảm ơn bạn! 😊",
            "Nghe hay quá! ✨",
            "OK được đó! 👌",
            "Haha thú vị nhỉ! 😄",
            "Sounds good! 🚀",
        ]
        
        import random
        reply = random.choice(replies)
        self.add_message(reply, False)
    
    def show_emoji_picker(self):
        """Show emoji picker (simple implementation)"""
        emojis = ["😀", "😂", "😍", "👍", "❤️", "🔥", "💯", "🎉", "🚀", "✨"]
        
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        
        for emoji in emojis:
            action = QAction(emoji, self)
            action.triggered.connect(lambda checked, e=emoji: self.insert_emoji(e))
            menu.addAction(action)
        
        # Show menu at emoji button position
        button_pos = self.ui.btnEmoji.mapToGlobal(self.ui.btnEmoji.rect().bottomLeft())
        menu.exec(button_pos)
    
    def insert_emoji(self, emoji):
        """Insert emoji into message input"""
        current_text = self.ui.txtMessage.text()
        self.ui.txtMessage.setText(current_text + emoji)
        self.ui.txtMessage.setFocus()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set modern style
    app.setStyle('Fusion')
    
    window = MessengerTestWindow()
    window.show()
    
    print("🚀 Messenger-style UI Test")
    print("Features:")
    print("  ✅ Gradient header with avatar")
    print("  ✅ Message bubbles with proper styling")  
    print("  ✅ Modern input area with emoji button")
    print("  ✅ Call/Video/Info buttons")
    print("  ✅ Auto-scroll and real-time typing")
    print("  ✅ Send button enable/disable")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
