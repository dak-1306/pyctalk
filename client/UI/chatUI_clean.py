# Facebook Messenger-style Chat UI
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QHBoxLayout, QWidget
import datetime

class MessageBubble(QtWidgets.QWidget):
    """Message bubble giống Messenger"""
    
    def __init__(self, message, is_sent=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_sent = is_sent
        self.timestamp = timestamp or datetime.datetime.now()
        self.setupUI()
    
    def setupUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 8, 15, 8)
        
        # Message bubble
        bubble = QtWidgets.QLabel()
        bubble.setText(self.message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(400)
        bubble.setMinimumHeight(45)
        
        if self.is_sent:
            # Sent messages (right, blue)
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
        
        self.setLayout(layout)

class Ui_ChatWindow(object):
    """Messenger-style Chat Window UI"""
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("ChatWindow")
        MainWindow.setMinimumSize(800, 600)
        MainWindow.resize(900, 700)
        MainWindow.setWindowTitle("PycTalk - Messenger")
        
        # Central widget
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Main layout
        main_layout = QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Chat area
        self.create_chat_area(main_layout)
        
        # Input area
        self.create_input_area(main_layout)
        
        # Set central widget
        MainWindow.setCentralWidget(self.centralwidget)
    
    def create_header(self, main_layout):
        """Create header like Messenger"""
        self.header = QtWidgets.QWidget()
        self.header.setFixedHeight(75)
        self.header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-bottom: 1px solid #e1e5e9;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Back button
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
        """)
        self.btnBack.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Friend avatar
        self.friendAvatar = QtWidgets.QLabel()
        self.friendAvatar.setFixedSize(50, 50)
        self.friendAvatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff7eb3, stop:1 #ff758c);
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                border: 3px solid rgba(255,255,255,0.3);
            }
        """)
        self.friendAvatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.friendAvatar.setText("F")
        
        # Friend info
        user_info = QVBoxLayout()
        user_info.setSpacing(2)
        
        self.lblFriendName = QtWidgets.QLabel("Bạn bè")
        self.lblFriendName.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: 600;
            }
        """)
        
        self.lblStatus = QtWidgets.QLabel("● Active now")
        self.lblStatus.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        user_info.addWidget(self.lblFriendName)
        user_info.addWidget(self.lblStatus)
        
        # Action buttons
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
        
        # Add to header layout
        header_layout.addWidget(self.btnBack)
        header_layout.addWidget(self.friendAvatar)
        header_layout.addLayout(user_info)
        header_layout.addStretch()
        header_layout.addWidget(buttons_widget)
        
        main_layout.addWidget(self.header)
    
    def create_chat_area(self, main_layout):
        """Create scrollable chat area"""
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
        
        # Messages container
        self.messagesWidget = QtWidgets.QWidget()
        self.messagesLayout = QVBoxLayout(self.messagesWidget)
        self.messagesLayout.setContentsMargins(20, 20, 20, 20)
        self.messagesLayout.setSpacing(8)
        self.messagesLayout.addStretch()
        
        self.scrollArea.setWidget(self.messagesWidget)
        main_layout.addWidget(self.scrollArea)
    
    def create_input_area(self, main_layout):
        """Create input area like Messenger"""
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
        
        # Attach button
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
            }
        """)
        self.btnAttach.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Message input
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
        """)
        
        # Emoji button
        self.btnEmoji = QtWidgets.QPushButton("😊")
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
        """)
        self.btnEmoji.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Send button
        self.btnSend = QtWidgets.QPushButton("➤")
        self.btnSend.setFixedSize(50, 50)
        self.btnSend.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0084FF, stop:1 #0066CC);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0066CC, stop:1 #004499);
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        self.btnSend.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnSend.setEnabled(False)
        
        # Add to layout
        input_layout.addWidget(self.btnAttach)
        input_layout.addWidget(self.txtMessage)
        input_layout.addWidget(self.btnEmoji)
        input_layout.addWidget(self.btnSend)
        
        main_layout.addWidget(self.inputArea)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_ChatWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
