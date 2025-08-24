from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor
from ..UI.messenger_ui.message_bubble_widget import MessageBubble

class ChatWindow(QtWidgets.QWidget):
    def showEvent(self, event):
        """Reload lịch sử chat khi widget được hiển thị lại (quay lại bạn bè)"""
        super().showEvent(event)
        try:
            if getattr(self.logic, "current_friend_id", None):
                import asyncio
                asyncio.create_task(self.logic.get_chat_history(self.logic.user_id, self.logic.current_friend_id))
        except Exception as e:
            import logging
            logging.exception("Failed to reload chat history on showEvent: %s", e)
    """Individual chat window UI only"""
    back_clicked = pyqtSignal()
    message_send_requested = pyqtSignal(str)   # UI phát tín hiệu khi muốn gửi tin nhắn

    def __init__(self, chat_data=None, parent=None, **kwargs):
        super().__init__(parent)
        self.chat_data = chat_data or {
            'friend_name': kwargs.get('friend_username', 'Friend'),
            'friend_id': kwargs.get('friend_id', 1),
            'current_username': kwargs.get('current_username', 'You'),
            'friend_avatar': kwargs.get('friend_avatar', ''),
            'last_message': kwargs.get('last_message', ''),
            'unread_count': kwargs.get('unread_count', 0)
        }
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self._create_header(layout)
        self._create_chat_area(layout)
        self._create_input_area(layout)

    # ===== UI components =====
    def _create_header(self, main_layout):
        header = QtWidgets.QWidget()
        header.setFixedHeight(75)
        header.setStyleSheet("background-color: #667eea; border-bottom: 1px solid #e1e5e9;")
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(20,0,20,0)
        layout.setSpacing(15)

        self.btn_back = QtWidgets.QPushButton("←")
        self.btn_back.clicked.connect(self.back_clicked.emit)

        friend_avatar = QtWidgets.QLabel(self.chat_data['friend_name'][0].upper())
        friend_avatar.setFixedSize(50,50)
        friend_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        friend_name = QtWidgets.QLabel(self.chat_data['friend_name'])
        friend_name.setStyleSheet("color:white; font-size:18px; font-weight:bold;")

        layout.addWidget(self.btn_back)
        layout.addWidget(friend_avatar)
        layout.addWidget(friend_name)
        layout.addStretch()
        main_layout.addWidget(header)

    def _create_chat_area(self, main_layout):
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.messages_widget = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout(self.messages_widget)
        self.messages_layout.addStretch()
        self.scroll_area.setWidget(self.messages_widget)
        main_layout.addWidget(self.scroll_area)

    def _create_input_area(self, main_layout):
        input_area = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(input_area)

        self.txt_message = QtWidgets.QLineEdit()
        self.txt_message.setPlaceholderText("Type a message...")

        self.btn_send = QtWidgets.QPushButton("➤")
        self.btn_send.clicked.connect(self._on_send_clicked)

        layout.addWidget(self.txt_message)
        layout.addWidget(self.btn_send)
        main_layout.addWidget(input_area)

    # ===== UI actions =====
    def _on_send_clicked(self):
        text = self.txt_message.text().strip()
        if text:
            self.message_send_requested.emit(text)
            self.txt_message.clear()

    def add_message(self, message, is_sent, timestamp=None):
        print(f"[DEBUG][ChatWindow] add_message: message={message}, is_sent={is_sent}, timestamp={timestamp}")
        bubble = MessageBubble(message, is_sent, timestamp)
        self.messages_layout.insertWidget(self.messages_layout.count()-1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def clear_messages(self):
        while self.messages_layout.count() > 1:
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
