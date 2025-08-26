import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor


class MessageBubble(QtWidgets.QWidget):
    """Modern message bubble component for chat"""
    
    def __init__(self, message, is_sent=True, timestamp=None, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_sent = is_sent
        self.timestamp = timestamp or datetime.datetime.now()
        print(f"[DEBUG][MessageBubble] Creating bubble: message='{message}', is_sent={is_sent}")
        self._setup_ui()
        
        # Force set size và visibility
        self.setMinimumHeight(50)
        self.setMaximumHeight(200)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        self.setVisible(True)
        self.show()
        
        print(f"[DEBUG][MessageBubble] Bubble setup completed, size={self.size()}, visible={self.isVisible()}")
    
    def setVisible(self, visible):
        print(f"[DEBUG][MessageBubble] setVisible called with: {visible}")
        super().setVisible(visible)
        print(f"[DEBUG][MessageBubble] setVisible result: {self.isVisible()}")
    
    def hideEvent(self, event):
        print(f"[DEBUG][MessageBubble] hideEvent triggered for message: {self.message}")
        super().hideEvent(event)
    
    def showEvent(self, event):
        print(f"[DEBUG][MessageBubble] showEvent triggered for message: {self.message}")
        super().showEvent(event)
    
    def _setup_ui(self):
        """Setup message bubble UI"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Đơn giản hóa để test - chỉ tạo 1 label cơ bản
        bubble = QtWidgets.QLabel()
        bubble.setText(self.message)
        bubble.setWordWrap(True)
        bubble.setMinimumHeight(30)
        bubble.setMaximumWidth(400)
        
        # Style đơn giản để test
        if self.is_sent:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #0084FF;
                    color: white;
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 14px;
                }
            """)
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #F0F0F0;
                    color: black;
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 14px;
                }
            """)
            layout.addWidget(bubble)
            layout.addStretch()
        
        # Force properties
        bubble.setVisible(True)
        bubble.show()
        print(f"[DEBUG][MessageBubble] Setup completed with simplified UI")
    
    def _create_avatar(self):
        """Create friend avatar for received messages"""
        avatar = QtWidgets.QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff7eb3, stop:1 #ff758c);
                color: white;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setText("F")
        return avatar
    
    def update_message(self, new_message):
        """Update message content"""
        self.message = new_message
        # Find the bubble label and update it
        for child in self.findChildren(QtWidgets.QLabel):
            if child.wordWrap():  # This is likely the message bubble
                child.setText(new_message)
                break
    
    def get_timestamp_str(self):
        """Get formatted timestamp string"""
        if hasattr(self.timestamp, 'strftime'):
            return self.timestamp.strftime("%H:%M")
        return str(self.timestamp)