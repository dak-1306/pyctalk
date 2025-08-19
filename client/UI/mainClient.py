# -*- coding: utf-8 -*-
# PycTalk - Main Window (refactor & polish)

from PyQt6 import QtCore, QtGui, QtWidgets

# Tùy môi trường của bạn, 2 import dưới có thể có/không.
# Mình bọc try/except để chạy demo không lỗi.
try:
    from Login.logout import LogoutHandler
except Exception:
    class LogoutHandler:
        def __init__(self, client, main_window): pass
        def logout(self, username): QtWidgets.QMessageBox.information(None, "Logout", f"Đăng xuất: {username}")

try:
    from Group_chat.group_chat_window import GroupChatWindow
except Exception:
    class GroupChatWindow(QtWidgets.QDialog):
        def __init__(self, client, user_id, username):
            super().__init__()
            self.setWindowTitle("Group Chat (demo)")
            self.resize(480, 360)
            t = QtWidgets.QTextEdit(self); t.setReadOnly(True)
            t.setPlainText("Demo Group Chat\n\nclient: {}\nuser_id: {}\nusername: {}".format(client, user_id, username))
            lay = QtWidgets.QVBoxLayout(self); lay.addWidget(t)


class Ui_MainWindow(object):
    def __init__(self, username, client, main_window):
        self.username = username
        self.client = client
        self.main_window = main_window
        self.group_chat_window = None

    def setupUi(self, MainWindow):
        from UI.friendsUI import Ui_FriendsWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(760, 520)
        MainWindow.setMinimumSize(560, 420)

        # ===== Central =====
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background:#f7fafc;")  # nền sáng, dễ nhìn

        # Sử dụng QHBoxLayout để chia sidebar và nội dung chính
        self.outer_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.outer_layout.setContentsMargins(16, 12, 16, 16)
        self.outer_layout.setSpacing(12)

        # ===== Sidebar bạn bè =====
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame#sidebar {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
            }
        """)
        sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Sử dụng giao diện danh sách bạn bè từ friendsUI
        # TabWidget chứa Friends / Groups
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setStyleSheet("""
            QTabWidget::pane { border:0; }
            QTabBar::tab {
                background:#f1f5f9; border:1px solid #e5e7eb; border-radius:6px;
                padding:6px 12px; margin-right:4px; font-weight:600; color:#334155;
            }
            QTabBar::tab:selected { background:#3b82f6; color:white; }
        """)

        # ----- Tab Friends -----
        self.friends_ui = Ui_FriendsWindow()
        from PyQt6.QtWidgets import QMainWindow
        self.friends_widget = QMainWindow()
        self.friends_ui.setupUi(self.friends_widget)
        self.friends_ui.addSampleFriends()
        friends_tab = QtWidgets.QWidget()
        f_lay = QtWidgets.QVBoxLayout(friends_tab)
        f_lay.setContentsMargins(0,0,0,0)
        f_lay.addWidget(self.friends_widget.centralWidget())
        self.tabWidget.addTab(friends_tab, "Friends")

        # ----- Tab Groups -----
        self.groups_list = QtWidgets.QListWidget()
        self.groups_list.setStyleSheet("""
            QListWidget { border:0; padding:6px; }
            QListWidget::item { padding:6px; border-radius:6px; }
            QListWidget::item:selected { background:#e0f2fe; }
        """)
        # demo vài nhóm
        self.groups_list.addItem("🌐 Developers")
        self.groups_list.addItem("🎮 Gamers")
        self.groups_list.addItem("📚 Study Group")

        groups_tab = QtWidgets.QWidget()
        g_lay = QtWidgets.QVBoxLayout(groups_tab)
        g_lay.setContentsMargins(0,0,0,0)
        g_lay.addWidget(self.groups_list)
        self.tabWidget.addTab(groups_tab, "Groups")

        sidebar_layout.addWidget(self.tabWidget)


        # Separator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        sidebar_layout.addWidget(line)

        # Nút tạo Group Chat
        self.btnGroupChat = QtWidgets.QPushButton("+ New Group Chat")
        self.btnGroupChat.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnGroupChat.setStyleSheet("""
            QPushButton {
                background:#f59e0b; color:white; border:none; border-radius:10px; padding:8px 12px;
                font-weight:600; margin:8px;
            }
            QPushButton:hover { background:#d97706; }
            QPushButton:pressed { background:#b45309; }
        """)
        sidebar_layout.addWidget(self.btnGroupChat)

        # ===== Nội dung chính =====
        self.main_content = QtWidgets.QWidget()
        self.main_content.setObjectName("main_content")
        self.main_layout = QtWidgets.QVBoxLayout(self.main_content)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ===== Topbar =====
        self.topbar = QtWidgets.QFrame()
        self.topbar.setObjectName("topbar")
        self.topbar.setStyleSheet("""
            QFrame#topbar {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)
        tb_layout = QtWidgets.QHBoxLayout(self.topbar)
        tb_layout.setContentsMargins(12, 8, 12, 8)

        self.logo_label = QtWidgets.QLabel()
        logo_pixmap = QtGui.QPixmap(28, 28)
        logo_pixmap.fill(QtGui.QColor('#3b82f6'))
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setFixedSize(28, 28)
        self.logo_label.setStyleSheet("border-radius:14px;")

        self.app_name = QtWidgets.QLabel("PycTalk")
        self.app_name.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Weight.Bold))
        self.app_name.setStyleSheet("color:#2563eb; margin-left:8px;")

        tb_layout.addWidget(self.logo_label, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        tb_layout.addWidget(self.app_name, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        tb_layout.addStretch(1)

        # user pill
        self.avatar_label = QtWidgets.QLabel()
        avatar = QtGui.QPixmap(22, 22); avatar.fill(QtGui.QColor("#e2e8f0"))
        self.avatar_label.setPixmap(avatar)
        self.avatar_label.setFixedSize(22, 22)
        self.avatar_label.setStyleSheet("border-radius:11px;")

        self.username_label = QtWidgets.QLabel(self.username or "Guest")
        self.username_label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Weight.DemiBold))
        self.username_label.setStyleSheet("color:#111827; padding-left:6px; padding-right:8px;")

        user_wrap = QtWidgets.QFrame()
        user_wrap.setStyleSheet("""
            QFrame { background:#f1f5f9; border:1px solid #e5e7eb; border-radius:14px; }
        """)
        uw = QtWidgets.QHBoxLayout(user_wrap); uw.setContentsMargins(8, 2, 8, 2)
        uw.addWidget(self.avatar_label)
        uw.addWidget(self.username_label)
        tb_layout.addWidget(user_wrap, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        # Spacer đẩy nút logout sang phải
        tb_layout.addSpacing(8)

        # Nút Logout trên Topbar
        self.btnLogout = QtWidgets.QPushButton("Logout")
        self.btnLogout.setObjectName("btnLogout")
        self.btnLogout.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnLogout.setStyleSheet("""
            QPushButton#btnLogout {
                background:#3b82f6; color:white; border:none; border-radius:8px; padding:6px 14px;
                font-weight:600;
            }
            QPushButton#btnLogout:hover { background:#2563eb; }
            QPushButton#btnLogout:pressed { background:#1d4ed8; }
        """)
        tb_layout.addWidget(self.btnLogout, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.main_layout.addWidget(self.topbar)
        self.main_layout.addSpacing(16)

        # ===== Body Card (center) =====
        self.card = QtWidgets.QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background:#ffffff;
                border:1px solid #e5e7eb;
                border-radius:16px;
            }
        """)
        card_shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=28, xOffset=0, yOffset=8, color=QtGui.QColor(0,0,0,40))
        self.card.setGraphicsEffect(card_shadow)

        card_outer = QtWidgets.QHBoxLayout(self.card)
        card_outer.setContentsMargins(20, 20, 20, 20)

        self.card_inner = QtWidgets.QFrame()
        ci_layout = QtWidgets.QVBoxLayout(self.card_inner)
        ci_layout.setContentsMargins(20, 24, 20, 24)
        ci_layout.setSpacing(18)

        self.title = QtWidgets.QLabel("PycTalk")
        title_font = QtGui.QFont("MV Boli", 26, QtGui.QFont.Weight.Bold)
        self.title.setFont(title_font)
        self.title.setStyleSheet("color:#0f172a;")
        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.subtitle = QtWidgets.QLabel("Xin chào, " + (self.username or "bạn") + " 👋")
        self.subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color:#475569; font-size:14px;")

        # Buttons row
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch(1)

        btn_row.addStretch(1)

        ci_layout.addWidget(self.title)
        ci_layout.addWidget(self.subtitle)
        ci_layout.addSpacing(8)
        ci_layout.addLayout(btn_row)

        card_outer.addStretch(1)
        card_outer.addWidget(self.card_inner, 1)
        card_outer.addStretch(1)

        # wrapper để căn giữa theo chiều dọc
        wrapper = QtWidgets.QWidget()
        wrap_layout = QtWidgets.QVBoxLayout(wrapper)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.addStretch(1)
        wrap_layout.addWidget(self.card)
        wrap_layout.addStretch(2)

        self.main_layout.addWidget(wrapper, 1)  # 🔧 Quan trọng: phải add widget nội dung!

        # Gắn sự kiện
        self.btnLogout.clicked.connect(self.on_logout_clicked)
        self.btnGroupChat.clicked.connect(self.on_group_chat_clicked)

        # Thêm sidebar và nội dung chính vào outer_layout
        self.outer_layout.addWidget(self.sidebar)
        self.outer_layout.addWidget(self.main_content, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        # ===== Topbar =====
        
    def _sync_login_state(self):
        is_ok = bool(self.client) and getattr(self.client, "is_logged_in", lambda: False)()
        self.btnGroupChat.setEnabled(is_ok)
        if is_ok:
            # cập nhật username chuẩn từ client (nếu có)
            try:
                self.username_label.setText(self.client.get_username())
                self.subtitle.setText(f"Xin chào, {self.client.get_username()} 👋")
            except Exception:
                pass

    def retranslateUi(self, MainWindow):
        _ = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_("MainWindow", "PycTalk - Main"))

    # ===== Actions =====
    def on_logout_clicked(self):
        if not self.client:
            QtWidgets.QMessageBox.information(self.main_window, "Logout", "Chưa gắn client, demo logout.")
            return
        self.logout_handler = LogoutHandler(self.client, self.main_window)
        self.logout_handler.logout(self.username)

    def on_group_chat_clicked(self):
        if not self.client or not self.client.is_logged_in():
            QtWidgets.QMessageBox.warning(self.main_window, "Lỗi", "Bạn chưa đăng nhập. Vui lòng đăng nhập lại.")
            return
        if self.group_chat_window is None or not self.group_chat_window.isVisible():
            self.group_chat_window = GroupChatWindow(
                self.client, self.client.get_user_id(), self.client.get_username()
            )
        self.group_chat_window.show()
        self.group_chat_window.raise_()
        self.group_chat_window.activateWindow()


# ===== Demo run =====
if __name__ == "__main__":
    import sys

    class FakeClient:
        def __init__(self, username="test"):
            self._u = username
        def is_logged_in(self): return True
        def get_user_id(self): return 1
        def get_username(self): return self._u

    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(username="test", client=FakeClient(), main_window=mw)
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec())
