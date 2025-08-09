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
            # Tin nhắn gửi đi (bên phải, màu xanh)
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #0084FF;
                    color: white;
                    border-radius: 18px;
                    padding: 10px 15px;  /* Tăng padding */
                    font-size: 15px;     /* Tăng font size */
                    line-height: 1.4;    /* Thêm line height */
                }
            """)
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            # Tin nhắn nhận được (bên trái, màu xám)
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #E4E6EA;
                    color: black;
                    border-radius: 18px;
                    padding: 10px 15px;  /* Tăng padding */
                    font-size: 15px;     /* Tăng font size */
                    line-height: 1.4;    /* Thêm line height */
                }
            """)
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
        
        # Header bar (giống Messenger)
        self.header = QtWidgets.QWidget()
        self.header.setFixedHeight(70)  # Tăng từ 60 lên 70
        self.header.setStyleSheet("""
            background-color: #4267B2;
            border-bottom: 1px solid #ddd;
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        # Back button
        self.btnBack = QtWidgets.QPushButton("← Back")
        self.btnBack.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 18px;  /* Tăng từ 16px lên 18px */
                font-weight: bold;
                padding: 8px 12px;  /* Tăng padding */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        self.btnBack.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Friend name
        self.lblFriendName = QtWidgets.QLabel("Bạn bè")
        self.lblFriendName.setStyleSheet("""
            color: white;
            font-size: 20px;  /* Tăng từ 18px lên 20px */
            font-weight: bold;
        """)
        
        # Online status
        self.lblStatus = QtWidgets.QLabel("● Online")
        self.lblStatus.setStyleSheet("""
            color: #42b883;
            font-size: 14px;  /* Tăng từ 12px lên 14px */
        """)
        
        # Info button
        self.btnInfo = QtWidgets.QPushButton("ⓘ")
        self.btnInfo.setFixedSize(35, 35)
        self.btnInfo.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.btnInfo.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        header_layout.addWidget(self.btnBack)
        header_layout.addSpacing(20)
        
        # User info section
        user_info = QVBoxLayout()
        user_info.setSpacing(0)
        user_info.addWidget(self.lblFriendName)
        user_info.addWidget(self.lblStatus)
        
        header_layout.addLayout(user_info)
        header_layout.addStretch()
        header_layout.addWidget(self.btnInfo)
        
        # Chat area (scrollable)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Messages container
        self.messagesWidget = QtWidgets.QWidget()
        self.messagesLayout = QVBoxLayout(self.messagesWidget)
        self.messagesLayout.setContentsMargins(10, 10, 10, 10)
        self.messagesLayout.setSpacing(5)
        self.messagesLayout.addStretch()  # Push messages to bottom initially
        
        self.scrollArea.setWidget(self.messagesWidget)
        
        # Input area (giống Messenger)
        self.inputArea = QtWidgets.QWidget()
        self.inputArea.setFixedHeight(80)  # Tăng chiều cao từ 70 lên 80
        self.inputArea.setStyleSheet("""
            background-color: white;
            border-top: 1px solid #ddd;
        """)
        
        input_layout = QHBoxLayout(self.inputArea)
        input_layout.setContentsMargins(15, 12, 15, 12)  # Tăng margin từ 10 lên 12
        input_layout.setSpacing(12)  # Tăng spacing từ 10 lên 12
        
        # Attach button
        self.btnAttach = QtWidgets.QPushButton("📎")
        self.btnAttach.setFixedSize(45, 45)  # Tăng từ 40x40 lên 45x45
        self.btnAttach.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.btnAttach.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Message input
        self.txtMessage = QtWidgets.QLineEdit()
        self.txtMessage.setPlaceholderText("Aa")
        self.txtMessage.setFixedHeight(45)  # Đặt chiều cao cố định
        self.txtMessage.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: none;
                border-radius: 22px;
                padding: 12px 18px;
                font-size: 15px;
            }
            QLineEdit:focus {
                background-color: #e4e6ea;
            }
        """)
        
        # Like button
        self.btnLike = QtWidgets.QPushButton("👍")
        self.btnLike.setFixedSize(45, 45)  # Tăng kích thước
        self.btnLike.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.btnLike.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Send button
        self.btnSend = QtWidgets.QPushButton("➤")
        self.btnSend.setFixedSize(45, 45)  # Tăng kích thước
        self.btnSend.setStyleSheet("""
            QPushButton {
                background-color: #0084FF;
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #006bd6;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btnSend.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnSend.setEnabled(False)
        
        input_layout.addWidget(self.btnAttach)
        input_layout.addWidget(self.txtMessage)
        input_layout.addWidget(self.btnLike)
        input_layout.addWidget(self.btnSend)
        
        # Add all sections to main layout
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.scrollArea)
        main_layout.addWidget(self.inputArea)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Connect events
        self.connectEvents()
        
        # Add some sample messages for demo
        self.addSampleMessages()
        
    def connectEvents(self):
        """Connect UI events"""
        self.txtMessage.textChanged.connect(self.onMessageTextChanged)
        self.txtMessage.returnPressed.connect(self.sendMessage)
        self.btnSend.clicked.connect(self.sendMessage)
        self.btnLike.clicked.connect(self.sendLike)
        
    def onMessageTextChanged(self):
        """Enable/disable send button based on message content"""
        has_text = len(self.txtMessage.text().strip()) > 0
        self.btnSend.setEnabled(has_text)
        self.btnLike.setVisible(not has_text)
        self.btnSend.setVisible(has_text)
        
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
