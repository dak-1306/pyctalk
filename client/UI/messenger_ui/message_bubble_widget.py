import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from .time_formatter import TimeFormatter


class MessageBubble(QtWidgets.QWidget):
    """Modern message bubble component for chat"""
    sender_clicked = pyqtSignal(str)  # Signal when sender name is clicked
    timestamp_clicked = pyqtSignal(str)  # Signal when timestamp is clicked
    
    def __init__(self, message, is_sent=True, timestamp=None, sender_name=None, show_sender_name=False, show_timestamp=False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_sent = is_sent
        self.timestamp = timestamp or datetime.datetime.now()
        self.sender_name = sender_name
        self.show_sender_name = show_sender_name
        self.show_timestamp = show_timestamp  # New parameter to control timestamp display
        self.timestamp_label = None  # Reference to timestamp label for click events
        print(f"[DEBUG][MessageBubble] Creating bubble: message='{message}', is_sent={is_sent}, sender_name={sender_name}, show_sender_name={show_sender_name}, show_timestamp={show_timestamp}")
        self._setup_ui()
        
        # Force set size và visibility
        self.setMinimumHeight(50)
        self.setMaximumHeight(200)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        self.setVisible(True)
        self.show()
        
        print(f"[DEBUG][MessageBubble] Bubble setup completed, size={self.size()}, visible={self.isVisible()}")
    
    def setVisible(self, visible):
        print(f"[DEBUG][MessageBubble] setVisible called with: {visible} for message: '{self.message}'")
        import traceback
        if not visible:
            print(f"[DEBUG][MessageBubble] HIDE CALL STACK:")
            traceback.print_stack()
            # Only prevent hiding during initial layout operations
            # Allow hiding if this is part of normal UI operations
            print(f"[DEBUG][MessageBubble] Allowing hide for layout operations")
        super().setVisible(visible)
        print(f"[DEBUG][MessageBubble] setVisible result: {self.isVisible()}")
    
    def hide(self):
        print(f"[DEBUG][MessageBubble] hide() called for message: '{self.message}' - ALLOWING")
        super().hide()
    
    def hideEvent(self, event):
        print(f"[DEBUG][MessageBubble] hideEvent triggered for message: {self.message}")
        super().hideEvent(event)
    
    def showEvent(self, event):
        print(f"[DEBUG][MessageBubble] showEvent triggered for message: {self.message}")
        super().showEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click to toggle timestamp"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle timestamp visibility
            self.toggle_timestamp_visibility()
        super().mousePressEvent(event)
    
    def _setup_ui(self):
        """Setup message bubble UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 2, 5, 2)
        main_layout.setSpacing(2)
        
        # Hiển thị tên người gửi nếu cần (chỉ cho tin nhắn nhận được)
        if not self.is_sent and self.show_sender_name and self.sender_name:
            sender_label = QtWidgets.QLabel(f"👤 {self.sender_name}")
            sender_label.setStyleSheet("""
                QLabel {
                    color: #0084FF;
                    font-size: 12px;
                    font-weight: bold;
                    margin-left: 10px;
                    margin-bottom: 2px;
                }
                QLabel:hover {
                    color: #006BB3;
                    text-decoration: underline;
                }
            """)
            sender_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            sender_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            sender_label.mousePressEvent = lambda event: self.sender_clicked.emit(self.sender_name)
            main_layout.addWidget(sender_label)
        
        # Container cho bubble chính
        bubble_layout = QtWidgets.QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bubble chính
        bubble = QtWidgets.QLabel()
        bubble.setText(self.message)
        bubble.setWordWrap(True)
        bubble.setMinimumHeight(30)
        bubble.setMaximumWidth(400)
        
        # Style cho bubble
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
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
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
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch()
        
        main_layout.addLayout(bubble_layout)
        
        # Hiển thị timestamp nếu cần
        if self.show_timestamp:
            timestamp_str = TimeFormatter.format_message_time(self.timestamp, show_time=True)
            if timestamp_str:
                self.timestamp_label = QtWidgets.QLabel(timestamp_str)
                self.timestamp_label.setStyleSheet("""
                    QLabel {
                        color: #8E8E93;
                        font-size: 11px;
                        margin: 2px 0;
                    }
                    QLabel:hover {
                        color: #007AFF;
                    }
                """)
                
                # Align timestamp based on message direction
                if self.is_sent:
                    self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                else:
                    self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                
                # Make timestamp clickable to toggle visibility
                self.timestamp_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                main_layout.addWidget(self.timestamp_label)
        
        # Force properties
        bubble.setVisible(True)
        bubble.show()
        print(f"[DEBUG][MessageBubble] Setup completed with sender name support")
    
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
        """Get formatted timestamp string using TimeFormatter"""
        return TimeFormatter.format_message_time(self.timestamp, show_time=True)
    
    def toggle_timestamp_visibility(self):
        """Toggle timestamp visibility when bubble is clicked"""
        if self.timestamp_label:
            self.timestamp_label.setVisible(not self.timestamp_label.isVisible())
        elif not self.show_timestamp:
            # Create and show timestamp if not already shown
            timestamp_str = self.get_timestamp_str()
            if timestamp_str:
                self.timestamp_label = QtWidgets.QLabel(timestamp_str)
                self.timestamp_label.setStyleSheet("""
                    QLabel {
                        color: #8E8E93;
                        font-size: 11px;
                        margin: 2px 0;
                    }
                """)
                
                if self.is_sent:
                    self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                else:
                    self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                
                self.layout().addWidget(self.timestamp_label)
                self.show_timestamp = True