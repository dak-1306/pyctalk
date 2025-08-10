# Chat 1-1 UI giống Facebook Messenger
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QHBoxLayout, QWidget
import datetime

class MessageBubble(QtWidgets.QWidget):
    def __init__(self, message, is_sent=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_sent = is_sent
        self.timestamp = timestamp or datetime.datetime.now()
        self.setupUI()
    
    def setupUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)  # Tăng margin dọc từ 5 lên 8
        
        # Message bubble
        bubble = QtWidgets.QLabel()
        bubble.setText(self.message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(350)  # Tăng từ 300 lên 350
        bubble.setMinimumHeight(40)  # Tăng từ 35 lên 40
        
        if self.is_sent:
            # Tin nhắn gửi đi (bên phải, màu xanh Messenger)
            bubble.setStyleSheet("""
                QLabel {
                    background: #0084FF;
                    color: white;
                    border-radius: 20px;
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: 400;
                    line-height: 1.3;
                    border: none;
                }
            """)
            
            # Thêm avatar cho sent messages (tùy chọn)
            layout.addStretch()
            layout.addWidget(bubble)
            
        else:
            # Avatar cho received messages
            avatar = QtWidgets.QLabel()
            avatar.setFixedSize(32, 32)
            avatar.setStyleSheet("""
                QLabel {
                    background: #FF6B6B;
                    color: white;
                    border-radius: 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setText("F")  # First letter of friend name
            
            # Tin nhắn nhận được (bên trái, màu xám Messenger)
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #F0F0F0;
                    color: #1c1e21;
                    border-radius: 20px;
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: 400;
                    line-height: 1.3;
                    border: 1px solid #E4E6EA;
                }
            """)
            
            layout.addWidget(avatar)
            layout.addSpacing(8)
            layout.addWidget(bubble)
            layout.addStretch()
        
        self.setLayout(layout)

class Ui_ChatWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("ChatWindow")
        MainWindow.setMinimumSize(800, 600)
        MainWindow.resize(800, 600)
        MainWindow.setWindowTitle("PycTalk - Chat")
        
        # Central widget
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Main layout
        main_layout = QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header bar (giống Messenger Facebook)
        self.header = QtWidgets.QWidget()
        self.header.setFixedHeight(75)
        self.header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0084FF, stop:1 #00C6FF);
                border-bottom: 1px solid #e1e5e9;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Back button với icon đẹp hơn
        self.btnBack = QtWidgets.QPushButton("←")
        self.btnBack.setFixedSize(45, 45)
        self.btnBack.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                font-size: 24px;
                font-weight: bold;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        self.btnBack.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Avatar của friend
        self.friendAvatar = QtWidgets.QLabel()
        self.friendAvatar.setFixedSize(50, 50)
        self.friendAvatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF6B6B, stop:1 #FF8E8E);
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid rgba(255,255,255,0.4);
            }
        """)
        self.friendAvatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.friendAvatar.setText("F")  # Sẽ set dynamically
        
        # Friend name với style đẹp hơn
        self.lblFriendName = QtWidgets.QLabel("Bạn bè")
        self.lblFriendName.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: 600;
            }
        """)
        
        # Online status với animation dot
        self.lblStatus = QtWidgets.QLabel("● Active now")
        self.lblStatus.setStyleSheet("""
            QLabel {
                color: #90EE90;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # Action buttons (call, video, info)
        buttons_widget = QtWidgets.QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Call button
        self.btnCall = QtWidgets.QPushButton("📞")
        self.btnCall.setFixedSize(45, 45)
        self.btnCall.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btnCall.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Video call button
        self.btnVideo = QtWidgets.QPushButton("📹")
        self.btnVideo.setFixedSize(45, 45)
        self.btnVideo.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btnVideo.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Info button
        self.btnInfo = QtWidgets.QPushButton("ⓘ")
        self.btnInfo.setFixedSize(45, 45)
        self.btnInfo.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btnInfo.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        buttons_layout.addWidget(self.btnCall)
        buttons_layout.addWidget(self.btnVideo)
        buttons_layout.addWidget(self.btnInfo)
        
        header_layout.addWidget(self.btnBack)
        header_layout.addWidget(self.friendAvatar)
        
        # User info section
        user_info = QVBoxLayout()
        user_info.setSpacing(2)
        user_info.addWidget(self.lblFriendName)
        user_info.addWidget(self.lblStatus)
        
        header_layout.addLayout(user_info)
        header_layout.addStretch()
        header_layout.addWidget(buttons_widget)
        
        # Chat area với background pattern giống Messenger
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c8c8c8, stop:1 #b8b8b8);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a8a8a8, stop:1 #989898);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Messages container với padding đẹp hơn
        self.messagesWidget = QtWidgets.QWidget()
        self.messagesLayout = QVBoxLayout(self.messagesWidget)
        self.messagesLayout.setContentsMargins(20, 20, 20, 20)
        self.messagesLayout.setSpacing(8)
        self.messagesLayout.addStretch()  # Push messages to bottom initially
        
        self.scrollArea.setWidget(self.messagesWidget)
        
        # Input area như Messenger với gradient
        self.inputArea = QtWidgets.QWidget()
        self.inputArea.setFixedHeight(85)
        self.inputArea.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-top: 1px solid #e4e6ea;
            }
        """)
        
        input_layout = QHBoxLayout(self.inputArea)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(15)
        
        # Attach button với style Messenger
        self.btnAttach = QtWidgets.QPushButton("📎")
        self.btnAttach.setFixedSize(50, 50)
        self.btnAttach.setStyleSheet("""
            QPushButton {
                background-color: #e4e6ea;
                color: #0084FF;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d3d6;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #bcc0c4;
            }
        """)
        self.btnAttach.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Message input với style Messenger
        self.txtMessage = QtWidgets.QLineEdit()
        self.txtMessage.setPlaceholderText("Type a message...")
        self.txtMessage.setFixedHeight(50)
        self.txtMessage.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: none;
                border-radius: 25px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: 400;
                color: #1c1e21;
            }
            QLineEdit:focus {
                background-color: #e4e6ea;
                outline: none;
                border: 2px solid #0084FF;
            }
            QLineEdit::placeholder {
                color: #8a8d91;
                font-style: italic;
            }
        """)
        
        # Emoji button
        self.btnEmoji = QtWidgets.QPushButton("�")
        self.btnEmoji.setFixedSize(50, 50)
        self.btnEmoji.setStyleSheet("""
            QPushButton {
                background-color: #e4e6ea;
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #d0d3d6;
            }
            QPushButton:pressed {
                background-color: #bcc0c4;
            }
        """)
        self.btnEmoji.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Send button với gradient đẹp hơn
        self.btnSend = QtWidgets.QPushButton("➤")
        self.btnSend.setFixedSize(50, 50)
        self.btnSend.setStyleSheet("""
            QPushButton {
                background: #0084FF;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0066CC;
            }
            QPushButton:pressed {
                background: #004499;
            }
            QPushButton:disabled {
                background: #E4E6EA;
                color: #BCC0C4;
            }
        """)
        self.btnSend.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnSend.setEnabled(True)  # Enable by default
        
        # Layout input area
        input_layout.addWidget(self.btnAttach)
        input_layout.addWidget(self.txtMessage)
        input_layout.addWidget(self.btnEmoji)
        input_layout.addWidget(self.btnSend)
        
        # Add all sections to main layout
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.scrollArea)
        main_layout.addWidget(self.inputArea)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Set central widget
        MainWindow.setCentralWidget(self.centralwidget)
        
    def addMessage(self, message, is_sent=True):
        """Add a message to the chat"""
        # Remove the stretch before adding new message
        item_count = self.messagesLayout.count()
        if item_count > 0:
            last_item = self.messagesLayout.takeAt(item_count - 1)
            if last_item.spacerItem():
                del last_item
        
        # Add the message bubble
        bubble = MessageBubble(message, is_sent)
        self.messagesLayout.addWidget(bubble)
        
        # Add stretch to keep messages at bottom
        self.messagesLayout.addStretch()
        
        # Auto scroll to bottom
        QTimer.singleShot(100, self.scrollToBottom)
        
    def scrollToBottom(self):
        """Scroll to the bottom of the chat"""
        scrollbar = self.scrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def sendMessage(self):
        """Send a message"""
        message_text = self.txtMessage.text().strip()
        if message_text:
            self.addMessage(message_text, True)
            self.txtMessage.clear()
            
            # Simulate receiving a reply (for demo)
            QTimer.singleShot(1000, lambda: self.simulateReply(message_text))
            
    def sendLike(self):
        """Send a like emoji"""
        self.addMessage("👍", True)
        
    def simulateReply(self, original_message):
        """Simulate receiving a reply message"""
        replies = [
            "Chào bạn! 😊",
            "OK, mình hiểu rồi",
            "Cảm ơn bạn nhé!",
            "Haha được đó 😄",
            "👍",
            f"Bạn vừa nói: '{original_message}'"
        ]
        import random
        reply = random.choice(replies)
        self.addMessage(reply, False)
        
    def addSampleMessages(self):
        """Add some sample messages for demo"""
        self.addMessage("Chào bạn! Bạn có khỏe không?", False)
        self.addMessage("Chào bạn! Mình khỏe, còn bạn thì sao?", True)
        self.addMessage("Mình cũng ổn. Hôm nay bạn làm gì vậy?", False)
        self.addMessage("Mình đang làm project PycTalk này đây 😊", True)
        self.addMessage("Wow nghe hay đấy! 👍", False)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_ChatWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
