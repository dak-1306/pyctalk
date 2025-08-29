from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal

class ClickableLabel(QtWidgets.QLabel):
    """Clickable label widget"""
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class TopBarWidget(QtWidgets.QFrame):
    # Signal for avatar click
    avatar_clicked = pyqtSignal()
    
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.username = username
        self._setup_ui(username)

    def _setup_ui(self, username):
        tb_layout = QtWidgets.QHBoxLayout(self)
        tb_layout.setContentsMargins(16, 10, 16, 10)

        # Spacer để căn giữa
        tb_layout.addStretch()

        # User info and controls (đơn giản hóa)
        user_container = QtWidgets.QFrame()
        user_container.setStyleSheet("""
            QFrame {
                background-color: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 18px;
            }
            QFrame:hover {
                background-color: rgba(99, 102, 241, 0.2);
                border-color: rgba(99, 102, 241, 0.5);
            }
        """)
        user_container.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        user_layout = QtWidgets.QHBoxLayout(user_container)
        user_layout.setContentsMargins(12, 6, 12, 6)
        
        # Use clickable avatar
        self.avatar_label = ClickableLabel()
        avatar = QtGui.QPixmap(28, 28)
        avatar.fill(QtGui.QColor("#6366f1"))
        self.avatar_label.setPixmap(avatar)
        self.avatar_label.setFixedSize(28, 28)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border-radius: 14px;
                border: 2px solid white;
            }
            QLabel:hover {
                border-color: #3b82f6;
            }
        """)
        
        self.username_label = QtWidgets.QLabel(username or "Guest")
        self.username_label.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Weight.DemiBold))
        self.username_label.setStyleSheet("color: #374151;")
        
        user_layout.addWidget(self.avatar_label)
        user_layout.addWidget(self.username_label)
        
        # Make the whole user container clickable
        user_container.mousePressEvent = lambda event: self.avatar_clicked.emit() if event.button() == QtCore.Qt.MouseButton.LeftButton else None
        
        tb_layout.addWidget(user_container)

        # Theme toggle button (giữ lại vì hữu ích)
        self.btnThemeToggle = QtWidgets.QPushButton("🌙")
        self.btnThemeToggle.setFixedSize(36, 36)
        self.btnThemeToggle.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        tb_layout.addWidget(self.btnThemeToggle)

        self.btnLogout = QtWidgets.QPushButton("Đăng xuất")
        self.btnLogout.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        tb_layout.addWidget(self.btnLogout)

    # Các phương thức cập nhật trạng thái, theme, ... có thể bổ sung tại đây
