import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QTimer
from UI.ui_main.topbar_widget import TopBarWidget
from UI.ui_main.sidebar_widget import SidebarWidget
logger = logging.getLogger(__name__)

from .status_thread import StatusUpdateThread
from .settings_manager import SettingsManager
from .notification_manager import NotificationManager
from .animation_helper import AnimationHelper
from Group_chat.group_chat_window import GroupChatWindow
from UI.ui_main.embedded_group_chat_widget import EmbeddedGroupChatWidget
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QPropertyAnimation
from Group_chat.group_api_client import GroupAPIClient
from typing import Optional, Dict
from Group_chat.group_chat_logic import GroupChatLogic


class Ui_MainWindow(QtCore.QObject):
    # Signals
    user_status_changed = pyqtSignal(bool)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, username: str, client, main_window: QtWidgets.QMainWindow):
        super().__init__()
        self.username = username
        self.client = client
        self.main_window = main_window
        # Tự động lấy user_id từ client nếu có
        self.user_id = None
        if hasattr(client, 'get_user_id'):
            try:
                self.user_id = int(client.get_user_id())
            except Exception:
                self.user_id = None
        self.group_chat_window: Optional[GroupChatWindow] = None
        self.settings = SettingsManager()
        self.notification_manager = NotificationManager(main_window)
        self.status_thread: Optional[StatusUpdateThread] = None
        self.animations: Dict[str, QPropertyAnimation] = {}
        self.is_connected = False
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._check_connection_status)
        self.current_theme = self.settings.get("theme", "light")
        
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        """Setup the complete UI with enhanced features"""
        has_friends_ui = True  # Đã dùng SidebarWidget với FriendListWindow, không cần import Ui_FriendsWindow
            
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 650)
        MainWindow.setMinimumSize(700, 500)
        
        # Enhanced window properties
        MainWindow.setWindowFlags(
            MainWindow.windowFlags() | 
            QtCore.Qt.WindowType.WindowMinMaxButtonsHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint
        )
        
        self._setup_central_widget(MainWindow)
        self._setup_sidebar(has_friends_ui)
        self._setup_main_content()
        self._setup_status_bar(MainWindow)
        self._setup_menu_bar(MainWindow)
        self._connect_signals()
        self._apply_theme()
        
        # Start background services
        self._start_status_monitoring()
        
        logger.info("UI setup completed successfully")
    
    def _setup_central_widget(self, MainWindow):
        """Setup central widget and main layout"""
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.outer_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.outer_layout.setContentsMargins(12, 8, 12, 12)
        self.outer_layout.setSpacing(12)
        
        MainWindow.setCentralWidget(self.centralwidget)
    
    def _setup_sidebar(self, has_friends_ui: bool):
        """Setup enhanced sidebar using SidebarWidget"""
        self.sidebar = SidebarWidget(
            has_friends_ui,
            self.client,
            self.user_id,
            self.username
        )
        # Kết nối signal mở khung chat 1-1
        if hasattr(self.sidebar, 'friends_widget') and hasattr(self.sidebar.friends_widget, 'friend_selected'):
            self.sidebar.friends_widget.friend_selected.connect(self._open_chat_window_1v1)
        # Gán các thuộc tính cần thiết để tương thích với code cũ
        self.tabWidget = self.sidebar.tabWidget
        self.groups_list = self.sidebar.groups_list
        self.btnGroupChat = self.sidebar.btnGroupChat
        self.btnSettings = self.sidebar.btnSettings
        self.outer_layout.addWidget(self.sidebar)
    def _open_chat_window_1v1(self, chat_data):
        """Mở khung chat 1-1 khi chọn bạn bè, chỉ hiển thị một khung chat duy nhất"""
        from UI.messenger_ui.chat_window_widget import ChatWindow
        # Xóa tất cả widget con khỏi main_layout (trừ topbar)
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            widget = item.widget()
            if widget and widget != self.topbar:
                self.main_layout.removeWidget(widget)
                widget.setParent(None)
        # Thêm khung chat mới
        chat_window = ChatWindow(chat_data, pyctalk_client=self.client)
        self.main_layout.addWidget(chat_window)
        chat_window.show()

    def _setup_main_content(self):
        """Setup main content area with enhanced features"""
        self.main_content = QtWidgets.QWidget()
        self.main_content.setObjectName("main_content")
        self.main_layout = QtWidgets.QVBoxLayout(self.main_content)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(12)
        
        # Enhanced topbar
        self._setup_topbar()
        
        # Main card with welcome content
        self._setup_main_card()
        
        self.outer_layout.addWidget(self.main_content, 1)
    
    def _setup_topbar(self):
        """Setup enhanced topbar using TopBarWidget"""
        self.topbar = TopBarWidget(self.username)
        # Gán các thuộc tính cần thiết để tương thích với code cũ
        self.status_indicator = self.topbar.status_indicator
        self.btnThemeToggle = self.topbar.btnThemeToggle
        self.btnLogout = self.topbar.btnLogout
        self.avatar_label = self.topbar.avatar_label
        self.username_label = self.topbar.username_label
        self.main_layout.addWidget(self.topbar)
    
    def _setup_user_controls(self, layout):
        """Setup user avatar, name and logout controls"""
        # User info container
        user_container = QtWidgets.QFrame()
        user_layout = QtWidgets.QHBoxLayout(user_container)
        user_layout.setContentsMargins(12, 6, 12, 6)
        
        # Avatar
        self.avatar_label = QtWidgets.QLabel()
        avatar = QtGui.QPixmap(28, 28)
        avatar.fill(QtGui.QColor("#6366f1"))
        self.avatar_label.setPixmap(avatar)
        self.avatar_label.setFixedSize(28, 28)
        
        # Username
        self.username_label = QtWidgets.QLabel(self.username or "Guest")
        self.username_label.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Weight.DemiBold))
        
        user_layout.addWidget(self.avatar_label)
        user_layout.addWidget(self.username_label)
        
        layout.addWidget(user_container)
        
        # Theme toggle
        self.btnThemeToggle = QtWidgets.QPushButton("🌙")
        self.btnThemeToggle.setFixedSize(36, 36)
        self.btnThemeToggle.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.btnThemeToggle)
        
        # Logout button
        self.btnLogout = QtWidgets.QPushButton("Đăng xuất")
        self.btnLogout.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.btnLogout)
    
    def _setup_main_card(self):
        """Setup main welcome card using MainCardWidget"""
        from UI.ui_main.main_card_widget import MainCardWidget
        card_container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(card_container)
        container_layout.addStretch(1)
        self.card = MainCardWidget(self.username)
        self.title = self.card.title
        self.subtitle = self.card.subtitle
        self.status_message = self.card.status_message
        card_wrapper = QtWidgets.QHBoxLayout()
        card_wrapper.addStretch(1)
        card_wrapper.addWidget(self.card)
        card_wrapper.addStretch(1)
        container_layout.addLayout(card_wrapper)
        container_layout.addStretch(2)
        self.main_layout.addWidget(card_container, 1)
    
    def _setup_welcome_content(self, layout):
        """Setup welcome content in main card"""
        # Main title
        self.title = QtWidgets.QLabel("PycTalk")
        title_font = QtGui.QFont("Segoe UI", 32, QtGui.QFont.Weight.Bold)
        self.title.setFont(title_font)
        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        
        # Welcome message
        self.subtitle = QtWidgets.QLabel(f"Xin chào, {self.username or 'bạn'} 👋")
        self.subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setFont(QtGui.QFont("Segoe UI", 16))
        layout.addWidget(self.subtitle)
        
        # Status message
        self.status_message = QtWidgets.QLabel("Sẵn sàng để trò chuyện!")
        self.status_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_message)
    
    def _setup_quick_actions(self, layout):
        """Setup quick action buttons"""
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setSpacing(16)
        
        # Quick chat button
        quick_chat_btn = QtWidgets.QPushButton("💬 Chat nhanh")
        quick_chat_btn.setMinimumHeight(45)
        actions_layout.addWidget(quick_chat_btn)
        
        # Find friends button  
        find_friends_btn = QtWidgets.QPushButton("👥 Tìm bạn bè")
        find_friends_btn.setMinimumHeight(45)
        actions_layout.addWidget(find_friends_btn)
        
        layout.addLayout(actions_layout)
    
    def _setup_status_bar(self, MainWindow):
        """Setup status bar with connection info"""
        self.status_bar = MainWindow.statusBar()
        
        # Connection status
        self.status_connection = QtWidgets.QLabel("Đã sẵn sàng")
        self.status_bar.addWidget(self.status_connection)
        
        # User count (if available)
        self.status_users = QtWidgets.QLabel("0 người dùng trực tuyến")
        self.status_bar.addPermanentWidget(self.status_users)
        
        # Version info
        version_label = QtWidgets.QLabel("v2.0")
        self.status_bar.addPermanentWidget(version_label)
    
    def _setup_menu_bar(self, MainWindow):
        """Setup application menu bar"""
        menubar = MainWindow.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&Tệp')
        
        # Settings action
        settings_action = QAction('⚙️ &Cài đặt', MainWindow)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('🚪 &Thoát', MainWindow)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(MainWindow.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&Hiển thị')
        
        # Theme actions
        light_theme_action = QAction('☀️ Giao diện sáng', MainWindow)
        light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        view_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('🌙 Giao diện tối', MainWindow)
        dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        view_menu.addAction(dark_theme_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Trợ giúp')
        
        about_action = QAction('ℹ️ &Giới thiệu', MainWindow)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Connect all signals and slots"""
        # Button clicks
        self.btnLogout.clicked.connect(self.on_logout_clicked)
        self.btnGroupChat.clicked.connect(self.on_group_chat_clicked)
        self.btnSettings.clicked.connect(self.show_settings)
        self.btnThemeToggle.clicked.connect(self.toggle_theme)
        
        # Window events
        self.main_window.closeEvent = self.closeEvent
        
        # Groups list double-click
        self.groups_list.itemDoubleClicked.connect(self.on_group_double_clicked)
    
    def _apply_theme(self):
        """Apply current theme to the interface"""
        if self.current_theme == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_light_theme(self):
        """Apply light theme styles"""
        self.centralwidget.setStyleSheet("""
            QWidget { background: #f8fafc; color: #1f2937; }
            QFrame#sidebar { 
                background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px;
            }
            QFrame#topbar { 
                background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
            }
            QFrame#main_card {
                background: #ffffff; border: 1px solid #e5e7eb; border-radius: 20px;
            }
            QPushButton {
                background: #3b82f6; color: white; border: none; border-radius: 8px; 
                padding: 10px 16px; font-weight: 600; font-size: 14px;
            }
            QPushButton:hover { background: #2563eb; }
            QPushButton:pressed { background: #1d4ed8; }
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background: #f1f5f9; border: 1px solid #e5e7eb; border-radius: 8px;
                padding: 8px 16px; margin: 2px; font-weight: 600; color: #374151;
            }
            QTabBar::tab:selected { background: #3b82f6; color: white; }
            QListWidget { 
                border: 0; padding: 8px; background: transparent;
            }
            QListWidget::item { 
                padding: 12px; border-radius: 8px; margin: 2px;
                background: transparent; border: 1px solid transparent;
            }
            QListWidget::item:hover { background: #f1f5f9; border: 1px solid #e5e7eb; }
            QListWidget::item:selected { background: #dbeafe; border: 1px solid #3b82f6; }
            QLineEdit {
                padding: 8px 12px; border: 2px solid #e5e7eb; border-radius: 8px;
                background: white; font-size: 14px;
            }
            QLineEdit:focus { border-color: #3b82f6; }
            QTextEdit { 
                border: 1px solid #e5e7eb; border-radius: 8px; background: white;
                padding: 8px; font-size: 14px;
            }
        """)
        
        self.btnThemeToggle.setText("🌙")
    
    def _apply_dark_theme(self):
        """Apply dark theme styles"""
        self.centralwidget.setStyleSheet("""
            QWidget { background: #111827; color: #f9fafb; }
            QFrame#sidebar { 
                background: #1f2937; border: 1px solid #374151; border-radius: 16px;
            }
            QFrame#topbar { 
                background: #1f2937; border: 1px solid #374151; border-radius: 12px;
            }
            QFrame#main_card {
                background: #1f2937; border: 1px solid #374151; border-radius: 20px;
            }
            QPushButton {
                background: #6366f1; color: white; border: none; border-radius: 8px; 
                padding: 10px 16px; font-weight: 600; font-size: 14px;
            }
            QPushButton:hover { background: #5b21b6; }
            QPushButton:pressed { background: #4c1d95; }
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background: #374151; border: 1px solid #4b5563; border-radius: 8px;
                padding: 8px 16px; margin: 2px; font-weight: 600; color: #d1d5db;
            }
            QTabBar::tab:selected { background: #6366f1; color: white; }
            QListWidget { 
                border: 0; padding: 8px; background: transparent;
            }
            QListWidget::item { 
                padding: 12px; border-radius: 8px; margin: 2px;
                background: transparent; border: 1px solid transparent; color: #e5e7eb;
            }
            QListWidget::item:hover { background: #374151; border: 1px solid #4b5563; }
            QListWidget::item:selected { background: #4338ca; border: 1px solid #6366f1; }
            QLineEdit {
                padding: 8px 12px; border: 2px solid #4b5563; border-radius: 8px;
                background: #374151; color: #f9fafb; font-size: 14px;
            }
            QLineEdit:focus { border-color: #6366f1; }
            QTextEdit { 
                border: 1px solid #4b5563; border-radius: 8px; background: #374151;
                padding: 8px; font-size: 14px; color: #f9fafb;
            }
        """)
        
        self.btnThemeToggle.setText("☀️")
    
    def _start_status_monitoring(self):
        """Start background status monitoring"""
        if self.client:
            self.status_thread = StatusUpdateThread(self.client)
            self.status_thread.status_changed.connect(self._on_status_changed)
            self.status_thread.start()
        
        # Start connection timer
        self.connection_timer.start(30000)  # Check every 30 seconds
    
    def _check_connection_status(self):
        """Check and update connection status"""
        try:
            if self.client and hasattr(self.client, 'is_logged_in'):
                is_connected = self.client.is_logged_in()
                self._update_connection_status(is_connected)
            else:
                self._update_connection_status(False)
        except Exception as e:
            logger.error(f"Connection status check failed: {e}")
            self._update_connection_status(False)
    
    def _update_connection_status(self, is_connected: bool):
        """Update UI based on connection status"""
        self.is_connected = is_connected
        self.status_indicator.setText("🟢 Đã kết nối" if is_connected else "🔴 Mất kết nối")
        self.status_connection.setText("Kết nối ổn định" if is_connected else "Đang kết nối lại...")
        self.btnGroupChat.setEnabled(is_connected)
        # Chỉ cập nhật status_message nếu nó còn tồn tại và chưa bị xóa
        if hasattr(self, "status_message") and self.status_message is not None:
            try:
                self.status_message.setText("Sẵn sàng để trò chuyện!" if is_connected else "Đang thử kết nối lại...")
            except RuntimeError:
                # Nếu widget đã bị xóa, bỏ qua
                self.status_message = None
        self.user_status_changed.emit(is_connected)
    
    def _on_status_changed(self, is_connected: bool, status_text: str):
        """Handle status update from background thread"""
        self._update_connection_status(is_connected)
        if not is_connected:
            self.notification_manager.show_notification(
                "Kết nối", "Đã mất kết nối với máy chủ"
            )
    
    def retranslateUi(self, MainWindow):
        """Set window title and other translatable strings"""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PycTalk - Enhanced Chat Client"))
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = QtWidgets.QDialog(self.main_window)
        dialog.setWindowTitle("Cài đặt")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Theme selection
        theme_group = QtWidgets.QGroupBox("Giao diện")
        theme_layout = QtWidgets.QVBoxLayout(theme_group)
        
        light_radio = QtWidgets.QRadioButton("☀️ Giao diện sáng")
        dark_radio = QtWidgets.QRadioButton("🌙 Giao diện tối")
        
        if self.current_theme == "light":
            light_radio.setChecked(True)
        else:
            dark_radio.setChecked(True)
        
        theme_layout.addWidget(light_radio)
        theme_layout.addWidget(dark_radio)
        layout.addWidget(theme_group)
        
        # Notifications
        notif_group = QtWidgets.QGroupBox("Thông báo")
        notif_layout = QtWidgets.QVBoxLayout(notif_group)
        
        show_notifs = QtWidgets.QCheckBox("Hiển thị thông báo hệ thống")
        show_notifs.setChecked(self.settings.get("show_notifications", True))
        
        sound_notifs = QtWidgets.QCheckBox("Âm thanh thông báo")
        sound_notifs.setChecked(self.settings.get("sound_notifications", True))
        
        notif_layout.addWidget(show_notifs)
        notif_layout.addWidget(sound_notifs)
        layout.addWidget(notif_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QtWidgets.QPushButton("OK")
        cancel_button = QtWidgets.QPushButton("Hủy")
        
        def save_settings():
            theme = "light" if light_radio.isChecked() else "dark"
            if theme != self.current_theme:
                self.change_theme(theme)
            
            self.settings.set("show_notifications", show_notifs.isChecked())
            self.settings.set("sound_notifications", sound_notifs.isChecked())
            dialog.accept()
        
        ok_button.clicked.connect(save_settings)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self.main_window,
            "Giới thiệu PycTalk",
            """
            <h3>PycTalk Enhanced v2.0</h3>
            <p>Ứng dụng chat hiện đại được xây dựng với PyQt6</p>
            
            <p><b>Tính năng:</b></p>
            <ul>
                <li>Giao diện hiện đại với chủ đề sáng/tối</li>
                <li>Chat nhóm và chat riêng tư</li>
                <li>Thông báo hệ thống</li>
                <li>Quản lý bạn bè và nhóm</li>
                <li>Theo dõi trạng thái kết nối</li>
            </ul>
            
            <p><b>Phiên bản:</b> 2.0.0<br>
            <b>Tác giả:</b> PycTalk Team<br>
            <b>Công nghệ:</b> Python, PyQt6</p>
            """
        )
    
    def change_theme(self, theme: str):
        """Change application theme"""
        if theme != self.current_theme:
            self.current_theme = theme
            self.settings.set("theme", theme)
            self._apply_theme()
            self.theme_changed.emit(theme)
            
            # Animate theme transition
            self.animations['theme'] = AnimationHelper.fade_in(self.centralwidget, 200)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        new_theme = "dark" if self.current_theme == "light" else "light"
    def on_create_group_clicked(self):
        # Bước 1: Nhập tên nhóm
        group_name, ok = QtWidgets.QInputDialog.getText(
            self.main_window, "Tạo nhóm mới", "Nhập tên nhóm:"
        )
        if not (ok and group_name):
            return
        # Bước 2: Lấy danh sách bạn bè từ server
        from Group_chat.group_api_client import GroupAPIClient
        api_client = GroupAPIClient(self.client)
        user_id = getattr(self, 'user_id', None)
        if user_id is None:
            QtWidgets.QMessageBox.warning(self.main_window, "Lỗi", "Không tìm thấy user_id")
            return
        friends_response = api_client.get_friends(int(user_id))
        if not (friends_response and friends_response.get("success")):
            QtWidgets.QMessageBox.warning(self.main_window, "Lỗi", "Không thể lấy danh sách bạn bè")
            return
        friends = friends_response.get("friends", [])
        if not friends:
            QtWidgets.QMessageBox.information(self.main_window, "Thông báo", "Bạn chưa có bạn bè để thêm vào nhóm.")
            selected_ids = []
        else:
            # Bước 3: Hiển thị dialog chọn bạn bè
            dialog = QtWidgets.QDialog(self.main_window)
            dialog.setWindowTitle("Chọn bạn để thêm vào nhóm")
            dialog.resize(350, 400)
            vbox = QtWidgets.QVBoxLayout(dialog)
            label = QtWidgets.QLabel("Chọn bạn bè để thêm vào nhóm:")
            vbox.addWidget(label)
            list_widget = QtWidgets.QListWidget()
            list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
            for f in friends:
                item = QtWidgets.QListWidgetItem(f"{f['username']} (ID: {f['user_id']})")
                item.setData(QtCore.Qt.ItemDataRole.UserRole, f['user_id'])
                list_widget.addItem(item)
            vbox.addWidget(list_widget)
            btn_box = QtWidgets.QHBoxLayout()
            ok_btn = QtWidgets.QPushButton("OK")
            cancel_btn = QtWidgets.QPushButton("Hủy")
            btn_box.addWidget(ok_btn)
            btn_box.addWidget(cancel_btn)
            vbox.addLayout(btn_box)
            selected_ids = []
            def accept():
                nonlocal selected_ids
                selected_ids = [item.data(QtCore.Qt.ItemDataRole.UserRole) for item in list_widget.selectedItems()]
                dialog.accept()
            ok_btn.clicked.connect(accept)
            cancel_btn.clicked.connect(dialog.reject)
            if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return
        # Bước 4: Tạo nhóm với danh sách bạn bè đã chọn
        result = api_client.create_group_with_members(group_name, int(user_id), selected_ids)
        if result and result.get("success"):
            QtWidgets.QMessageBox.information(self.main_window, "Thành công", "Tạo nhóm thành công!")
            self._reload_groups_list()
        else:
            QtWidgets.QMessageBox.warning(self.main_window, "Lỗi", f"Tạo nhóm thất bại: {result.get('error', 'Không rõ lỗi')}")

    def _reload_groups_list(self):
        """Reload group list from server"""
        try:
            from Group_chat.group_api_client import GroupAPIClient
            api_client = GroupAPIClient(self.client)
            user_id = getattr(self, 'user_id', None)
            if user_id is None:
                self.groups_list.clear()
                self.groups_list.addItem("Không tìm thấy user_id")
                return
            response = api_client.get_user_groups(int(user_id))
            self.groups_list.clear()
            if response and response.get("success"):
                for group in response.get("groups", []):
                    group_name = group["group_name"]
                    member_count = f"{group.get('member_count', 'N/A')} thành viên" if 'member_count' in group else ""
                    item = QtWidgets.QListWidgetItem(f"{group_name}\n{member_count}")
                    item.setSizeHint(QtCore.QSize(0, 50))
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, group)
                    self.groups_list.addItem(item)
            else:
                self.groups_list.addItem("Không thể tải danh sách nhóm")
        except Exception as e:
            self.groups_list.clear()
            self.groups_list.addItem(f"Lỗi tải nhóm: {e}")
    
    def on_logout_clicked(self):
        """Handle logout button click"""
        try:
            if not self.client:
                QtWidgets.QMessageBox.information(
                    self.main_window, 
                    "Đăng xuất", 
                    "Demo logout - chưa kết nối client thực tế."
                )
                return
            
            self.logout_handler = LogoutHandler(self.client, self.main_window)
            self.logout_handler.logout(self.username)
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "Lỗi đăng xuất",
                f"Có lỗi xảy ra khi đăng xuất: {str(e)}"
            )
    
    def on_group_chat_clicked(self):
        """Handle group chat button click: mở cửa sổ GroupChatWindow"""
        try:
            # Truyền đúng tham số cho GroupChatWindow
            user_id = getattr(self.client, 'get_user_id', lambda: None)()
            username = getattr(self.client, 'get_username', lambda: self.username)()
            self.group_chat_window = GroupChatWindow(self.client, user_id, username)
            self.group_chat_window.show()
            self.group_chat_window.raise_()
            self.group_chat_window.activateWindow()
            # Có thể thêm animation nếu muốn
        except Exception as e:
            logger.error(f"Không thể mở GroupChatWindow: {e}")
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "Lỗi",
                f"Không thể mở cửa sổ chat nhóm: {str(e)}"
            )
    
    def on_group_double_clicked(self, item):
        """Khi click vào nhóm, chỉ còn khung chat nhóm, khung welcome phải biến mất hoàn toàn"""
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        # Chỉ giữ lại topbar, xóa toàn bộ các widget khác trong main_layout
        widgets_to_remove = []
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            # Giữ lại topbar, xóa các widget khác
            if widget and getattr(widget, 'objectName', lambda: None)() != "topbar":
                widgets_to_remove.append(widget)
        for widget in widgets_to_remove:
            self.main_layout.removeWidget(widget)
            widget.hide()
            widget.deleteLater()
        # Xóa tham chiếu đến status_message để tránh lỗi khi widget đã bị xóa
        self.status_message = None
        # Thêm khung chat nhóm mới
        chat_widget = EmbeddedGroupChatWidget(self.client, self.user_id, self.username, group_data)
        self.main_layout.addWidget(chat_widget, 1)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.settings.get("minimize_to_tray", True) and self.notification_manager.tray_icon:
            event.ignore()
            self.main_window.hide()
            self.notification_manager.show_notification(
                "PycTalk",
                "Ứng dụng vẫn chạy trong khay hệ thống"
            )
        else:
            self._cleanup_resources()
            event.accept()
    
    def _cleanup_resources(self):
        """Clean up resources before closing"""
        try:
            # Stop status monitoring thread
            if self.status_thread:
                self.status_thread.stop()
            
            # Stop timers
            self.connection_timer.stop()
            
            # Close group chat window
            if self.group_chat_window:
                self.group_chat_window.close()
            
            # Hide tray icon
            if self.notification_manager.tray_icon:
                self.notification_manager.tray_icon.hide()
                
            logger.info("Resources cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
