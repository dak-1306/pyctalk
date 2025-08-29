import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from .time_formatter import TimeFormatter


class MessageBubble(QtWidgets.QWidget):
    """Modern message bubble component for chat"""
    sender_clicked = pyqtSignal(str)  # Signal when sender name is clicked
    timestamp_clicked = pyqtSignal(str)  # Signal when timestamp is clicked
    
    def __init__(self, message, is_sent=True, timestamp=None, sender_name=None, show_sender_name=False, show_timestamp=False, is_read=None, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_sent = is_sent
        self.timestamp = timestamp or datetime.datetime.now()
        self.sender_name = sender_name
        self.show_sender_name = show_sender_name
        self.show_timestamp = show_timestamp  # New parameter to control timestamp display
        self.is_read = is_read  # Message read status (for sent messages)
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
        # Only allow hiding during layout operations, preserve message bubbles
        super().setVisible(visible)
    
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
        """Setup message bubble UI với styling đẹp như Zalo/Messenger"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(3)
        
        # Set object name for specific styling
        self.setObjectName("MessageBubbleWidget")
        
        # Set widget background to transparent with higher specificity
        self.setStyleSheet("""
            #MessageBubbleWidget {
                background-color: transparent !important;
            }
            #MessageBubbleWidget QWidget {
                background-color: transparent !important;
            }
            #MessageBubbleWidget QLabel {
                background-color: transparent !important;
            }
        """)
        
        # Hiển thị tên người gửi nếu cần (chỉ cho tin nhắn nhận được)
        if not self.is_sent and self.show_sender_name and self.sender_name:
            sender_label = QtWidgets.QLabel(f"{self.sender_name}")
            sender_label.setStyleSheet("""
                QLabel {
                    color: #0084FF;
                    font-size: 12px;
                    font-weight: 600;
                    margin-left: 44px;
                    margin-bottom: 2px;
                    padding: 0px;
                }
            """)
            sender_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            sender_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            sender_label.mousePressEvent = lambda event: self.sender_clicked.emit(self.sender_name)
            main_layout.addWidget(sender_label)
        
        # Container cho bubble chính với avatar
        bubble_container = QtWidgets.QHBoxLayout()
        bubble_container.setContentsMargins(0, 0, 0, 0)
        bubble_container.setSpacing(8)
        
        # Avatar cho tin nhắn nhận được
        if not self.is_sent:
            avatar_label = QtWidgets.QLabel()
            avatar_label.setFixedSize(32, 32)
            avatar_label.setStyleSheet("""
                QLabel {
                    background-color: #0084FF;
                    border-radius: 16px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            # Hiển thị chữ cái đầu của tên
            initial = self.sender_name[0].upper() if self.sender_name else "?"
            avatar_label.setText(initial)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bubble_container.addWidget(avatar_label, alignment=Qt.AlignmentFlag.AlignBottom)
        
        # Bubble chính
        bubble_widget = QtWidgets.QWidget()
        bubble_layout = QtWidgets.QVBoxLayout(bubble_widget)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(0)
        
        bubble = QtWidgets.QLabel()
        bubble.setText(self.message)
        bubble.setWordWrap(True)
        bubble.setMinimumHeight(32)
        bubble.setMaximumWidth(320)
        bubble.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Minimum)
        
        # Style cho bubble với hiệu ứng đẹp
        if self.is_sent:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #0084FF;
                    color: white;
                    border-radius: 18px;
                    padding: 10px 14px;
                    font-size: 14px;
                    line-height: 1.4;
                }
            """)
            bubble_widget.setMaximumWidth(320)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #f1f3f4;
                    color: #1a1a1a;
                    border-radius: 18px;
                    padding: 10px 14px;
                    font-size: 14px;
                    line-height: 1.4;
                    border: 1px solid #e4e6ea;
                }
            """)
            bubble_widget.setMaximumWidth(320)
        
        bubble_layout.addWidget(bubble)
        
        # Thêm animation hover effect
        bubble.enterEvent = lambda event: self._on_bubble_hover(True)
        bubble.leaveEvent = lambda event: self._on_bubble_hover(False)
        
        # Căn chỉnh bubble
        if self.is_sent:
            bubble_container.addStretch()
            bubble_container.addWidget(bubble_widget)
        else:
            bubble_container.addWidget(bubble_widget)
            bubble_container.addStretch()
        
        main_layout.addLayout(bubble_container)
        
        # Hiển thị timestamp nếu cần
        if self.show_timestamp:
            timestamp_str = TimeFormatter.format_message_time(self.timestamp, show_time=True)
            if timestamp_str:
                timestamp_container = QtWidgets.QHBoxLayout()
                timestamp_container.setContentsMargins(0, 0, 0, 0)
                
                self.timestamp_label = QtWidgets.QLabel(timestamp_str)
                self.timestamp_label.setStyleSheet("""
                    QLabel {
                        color: #8E8E93;
                        font-size: 11px;
                        margin: 2px 0;
                        padding: 0;
                        background-color: transparent !important;
                        selection-background-color: transparent;
                        selection-color: #8E8E93;
                    }
                """)
                
                # Align timestamp based on message direction
                if self.is_sent:
                    timestamp_container.addStretch()
                    timestamp_container.addWidget(self.timestamp_label)
                else:
                    # Offset để align với bubble (do có avatar)
                    timestamp_container.addSpacing(40)
                    timestamp_container.addWidget(self.timestamp_label)
                    timestamp_container.addStretch()
                
                # Make timestamp clickable to toggle visibility
                self.timestamp_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                main_layout.addLayout(timestamp_container)
        
        # Add message status indicator for sent messages
        if self.is_sent:
            self._add_status_indicator(main_layout)
        
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
                background-color: #0084FF;
                color: white;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setText("F")
        return avatar
    
    def _add_status_indicator(self, main_layout):
        """Add message status indicator for sent messages"""
        if self.is_read is None:
            # Status unknown, show "Sent"
            status_text = "Đã gửi"
            status_icon = "✓"
            status_color = "#8E8E93"
        elif self.is_read:
            # Message has been read
            status_text = "Đã xem"
            status_icon = "✓✓"
            status_color = "#007AFF"
        else:
            # Message sent but not read
            status_text = "Đã gửi"
            status_icon = "✓"
            status_color = "#8E8E93"
        
        # Create status indicator
        self.status_label = QtWidgets.QLabel(f"{status_icon} {status_text}")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                font-size: 10px;
                margin: 2px 0;
                padding: 0;
                background-color: transparent !important;
                selection-background-color: transparent;
                selection-color: {status_color};
            }}
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.status_label)
    
    def update_read_status(self, is_read):
        """Update the read status of the message"""
        self.is_read = is_read
        if hasattr(self, 'status_label') and self.status_label:
            if is_read:
                self.status_label.setText("✓✓ Đã xem")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #007AFF;
                        font-size: 10px;
                        margin: 2px 0;
                        padding: 0;
                        background-color: transparent !important;
                        selection-background-color: transparent;
                        selection-color: #007AFF;
                    }
                """)
            else:
                self.status_label.setText("✓ Đã gửi")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #8E8E93;
                        font-size: 10px;
                        margin: 2px 0;
                        padding: 0;
                        background-color: transparent !important;
                        selection-background-color: transparent;
                        selection-color: #8E8E93;
                    }
                """)
    
    def hide_status_indicator(self):
        """Hide the status indicator for this message"""
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.hide()
            print(f"[DEBUG][MessageBubble] Hidden status indicator for message: {self.message[:20]}...")
    
    def show_status_indicator(self):
        """Show the status indicator for this message"""
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.show()
            print(f"[DEBUG][MessageBubble] Shown status indicator for message: {self.message[:20]}...")
    
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
                        padding: 0;
                        background-color: transparent !important;
                        selection-background-color: transparent;
                        selection-color: #8E8E93;
                    }
                """)
                
                if self.is_sent:
                    self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                else:
                    self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                
                self.layout().addWidget(self.timestamp_label)
                self.show_timestamp = True
    
    def _on_bubble_hover(self, is_hovering):
        """Handle bubble hover effect - tinh tế hơn"""
        # Remove hover background effects to keep clean look
        pass