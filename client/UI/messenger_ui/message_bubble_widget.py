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
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup message bubble UI"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # Message bubble label
        bubble = QtWidgets.QLabel()
        bubble.setText(self.message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(400)
        bubble.setMinimumHeight(45)
        
        if self.is_sent:
            # Sent messages (right, blue gradient)
            bubble.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0084FF, stop:1 #0066CC);
                    color: white;
                    border-radius: 22px;
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: 400;
                }
            """)
            layout.addStretch()
            layout.addWidget(bubble)
            
        else:
            # Received messages (left, gray) with avatar
            avatar = self._create_avatar()
            
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #F0F0F0;
                    color: #1c1e21;
                    border-radius: 22px;
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: 400;
                    border: 1px solid #E4E6EA;
                }
            """)
            
            layout.addWidget(avatar)
            layout.addSpacing(8)
            layout.addWidget(bubble)
            layout.addStretch()
    
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