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

        # Timestamp label
        timestamp_label = QtWidgets.QLabel()
        timestamp_label.setText(self.get_timestamp_str())
        timestamp_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                padding-left: 6px;
                padding-right: 6px;
            }
        """)
        timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
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
            # Bubble and timestamp in vertical layout
            bubble_layout = QtWidgets.QVBoxLayout()
            bubble_layout.setSpacing(2)
            bubble_layout.addWidget(bubble)
            bubble_layout.addWidget(timestamp_label)
            bubble_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addStretch()
            layout.addLayout(bubble_layout)
        
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
            # Bubble and timestamp in vertical layout
            bubble_layout = QtWidgets.QVBoxLayout()
            bubble_layout.setSpacing(2)
            bubble_layout.addWidget(bubble)
            bubble_layout.addWidget(timestamp_label)
            bubble_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(avatar)
            layout.addSpacing(8)
            layout.addLayout(bubble_layout)
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