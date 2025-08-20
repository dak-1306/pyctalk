from PyQt6 import QtCore, QtGui, QtWidgets

class MainCardWidget(QtWidgets.QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(600)
        self.setObjectName("main_card")
        self._setup_ui(username)

    def _setup_ui(self, username):
        # Card shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        card_layout = QtWidgets.QVBoxLayout(self)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)

        # Welcome content
        self.title = QtWidgets.QLabel("PycTalk")
        title_font = QtGui.QFont("Segoe UI", 32, QtGui.QFont.Weight.Bold)
        self.title.setFont(title_font)
        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.title)

        self.subtitle = QtWidgets.QLabel(f"Xin chào, {username or 'bạn'} 👋")
        self.subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setFont(QtGui.QFont("Segoe UI", 16))
        card_layout.addWidget(self.subtitle)

        self.status_message = QtWidgets.QLabel("Sẵn sàng để trò chuyện!")
        self.status_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_message)

        # Quick actions
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setSpacing(16)
        quick_chat_btn = QtWidgets.QPushButton("💬 Chat nhanh")
        quick_chat_btn.setMinimumHeight(45)
        actions_layout.addWidget(quick_chat_btn)
        find_friends_btn = QtWidgets.QPushButton("👥 Tìm bạn bè")
        find_friends_btn.setMinimumHeight(45)
        actions_layout.addWidget(find_friends_btn)
        card_layout.addLayout(actions_layout)

    # Có thể bổ sung các phương thức cập nhật nội dung, trạng thái, ... tại đây
