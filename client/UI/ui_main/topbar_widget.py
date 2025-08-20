from PyQt6 import QtCore, QtGui, QtWidgets

class TopBarWidget(QtWidgets.QFrame):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self._setup_ui(username)

    def _setup_ui(self, username):
        tb_layout = QtWidgets.QHBoxLayout(self)
        tb_layout.setContentsMargins(16, 10, 16, 10)

        # App branding
        branding_layout = QtWidgets.QHBoxLayout()
        self.logo_label = QtWidgets.QLabel()
        logo_pixmap = QtGui.QPixmap(32, 32)
        logo_pixmap.fill(QtGui.QColor('#3b82f6'))
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setFixedSize(32, 32)
        self.app_name = QtWidgets.QLabel("PycTalk")
        self.app_name.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        branding_layout.addWidget(self.logo_label)
        branding_layout.addWidget(self.app_name)
        branding_layout.addStretch()
        tb_layout.addLayout(branding_layout)

        # Status indicator
        self.status_indicator = QtWidgets.QLabel("🔴 Chưa kết nối")
        self.status_indicator.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        tb_layout.addWidget(self.status_indicator)
        tb_layout.addStretch()

        # User info and controls
        user_container = QtWidgets.QFrame()
        user_layout = QtWidgets.QHBoxLayout(user_container)
        user_layout.setContentsMargins(12, 6, 12, 6)
        self.avatar_label = QtWidgets.QLabel()
        avatar = QtGui.QPixmap(28, 28)
        avatar.fill(QtGui.QColor("#6366f1"))
        self.avatar_label.setPixmap(avatar)
        self.avatar_label.setFixedSize(28, 28)
        self.username_label = QtWidgets.QLabel(username or "Guest")
        self.username_label.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Weight.DemiBold))
        user_layout.addWidget(self.avatar_label)
        user_layout.addWidget(self.username_label)
        tb_layout.addWidget(user_container)

        self.btnThemeToggle = QtWidgets.QPushButton("🌙")
        self.btnThemeToggle.setFixedSize(36, 36)
        self.btnThemeToggle.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        tb_layout.addWidget(self.btnThemeToggle)

        self.btnLogout = QtWidgets.QPushButton("Đăng xuất")
        self.btnLogout.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        tb_layout.addWidget(self.btnLogout)

    # Các phương thức cập nhật trạng thái, theme, ... có thể bổ sung tại đây
