import logging
import sys
import os
import asyncio
from typing import Optional, Dict
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal, QTimer, QPropertyAnimation
from PyQt6.QtGui import QAction
# UI widgets
from client.UI.ui_main.topbar_widget import TopBarWidget
from client.UI.ui_main.sidebar_widget import SidebarWidget
from client.UI.ui_main.main_card_widget import MainCardWidget
from client.UI.messenger_ui.my_profile_window import MyProfileWindow
from client.Group_chat.embedded_group_chat_widget import EmbeddedGroupChatWidget
# Logic/helpers
from .status_thread import StatusUpdateThread
from .settings_manager import SettingsManager
from .notification_manager import NotificationManager
from .animation_helper import AnimationHelper
from client.Login.logout import LogoutHandler
# Group chat
logger = logging.getLogger(__name__)
# Ensure root path for database imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class Ui_MainWindow(QtCore.QObject):
    """Main UI class for PycTalk application"""
    user_status_changed = pyqtSignal(bool)
    theme_changed = pyqtSignal(str)

    def __init__(self, username: str, client, main_window: QtWidgets.QMainWindow):
        super().__init__()
        self.username = username
        self.client = client
        self.main_window = main_window
        self.user_id = self._get_user_id_from_client(client)
        # self.group_chat_window đã bị loại bỏ
        self.settings = SettingsManager()
        self.notification_manager = NotificationManager(main_window)
        self.status_thread: Optional[StatusUpdateThread] = None
        self.animations: Dict[str, QPropertyAnimation] = {}
        self.is_connected = False
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._check_connection_status)
        self.current_theme = self.settings.get("theme", "light")
        # Cache cho chat windows để tránh mất tin nhắn
        self.chat_windows_cache = {}  # {friend_id: (chat_window, api_client)}
        self.current_chat_friend_id = None
        self.card_container = None  # Lưu reference để ẩn/hiện

    def _get_user_id_from_client(self, client):
        if hasattr(client, 'get_user_id'):
            try:
                return int(client.get_user_id())
            except Exception:
                return None
        return None
        
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        """Setup the complete UI with enhanced features"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 650)
        MainWindow.setMinimumSize(700, 500)
        MainWindow.setWindowFlags(
            MainWindow.windowFlags() |
            QtCore.Qt.WindowType.WindowMinMaxButtonsHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint
        )
        self._setup_central_widget(MainWindow)
        self._setup_sidebar(True)
        self._setup_main_content()
        self._setup_status_bar(MainWindow)
        self._setup_menu_bar(MainWindow)
        self._connect_signals()
        self._apply_theme()
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
        """Setup sidebar with friend list and group list"""
        self.sidebar = SidebarWidget(
            has_friends_ui,
            self.client,
            self.user_id,
            self.username
        )
        # Connect friend selection signal
        if hasattr(self.sidebar, 'friends_widget') and hasattr(self.sidebar.friends_widget, 'friend_selected'):
            self.sidebar.friends_widget.friend_selected.connect(self._open_chat_window_1v1)
        # Expose sidebar attributes for compatibility
        self.tabWidget = self.sidebar.tabWidget
        self.groups_list = self.sidebar.groups_list
    # self.btnGroupChat đã bị loại bỏ
        self.btnSettings = self.sidebar.btnSettings
        self.outer_layout.addWidget(self.sidebar)
    def _open_chat_window_1v1(self, chat_data):
        """Open 1-1 chat window when a friend is selected"""
        from client.Chat1_1.chat_window_widget import ChatWindow
        from client.Chat1_1.chat1v1_client import Chat1v1Client
        
        print(f"[DEBUG][MainWindow] _open_chat_window_1v1 called with chat_data={chat_data}")
        print(f"[DEBUG][MainWindow] self.user_id={self.user_id}")
        
        # Ensure current_user_id is set
        chat_data['current_user_id'] = chat_data.get('current_user_id', self.user_id)
        try:
            chat_data['current_user_id'] = int(chat_data['current_user_id'])
        except Exception:
            pass
            
        friend_id = chat_data.get('friend_id', 1)
        
        print(f"[DEBUG][MainWindow] After processing: current_user_id={chat_data['current_user_id']}, friend_id={friend_id}")
        
        # Ẩn card_container nếu đang hiển thị
        try:
            if hasattr(self, 'card_container') and self.card_container and self.card_container.isVisible():
                self.card_container.hide()
        except RuntimeError:
            # Widget đã bị xóa, bỏ qua
            print("[DEBUG][MainWindow] card_container đã bị xóa, bỏ qua")
            self.card_container = None

        # Xóa tất cả widgets cũ trong main_layout (trừ topbar) để tránh đè lên nhau
        widgets_to_remove = []
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            # Giữ lại topbar, xóa các widget khác
            if widget and getattr(widget, 'objectName', lambda: None)() != "topbar":
                widgets_to_remove.append(widget)
        for widget in widgets_to_remove:
            self.main_layout.removeWidget(widget)
            widget.hide()
            # Không dùng deleteLater() vì có thể cần dùng lại từ cache
        
        # Ẩn chat window hiện tại (nếu có)
        if self.current_chat_friend_id and self.current_chat_friend_id in self.chat_windows_cache:
            current_chat_window, _ = self.chat_windows_cache[self.current_chat_friend_id]
            current_chat_window.hide()
            # Không cần removeWidget nữa vì đã xóa ở trên
        
        # Kiểm tra cache, nếu đã có thì dùng lại
        if friend_id in self.chat_windows_cache:
            chat_window, api_client = self.chat_windows_cache[friend_id]
            # Sử dụng logic đã có trong cache và reconnect signals
            chat_window.logic = api_client.logic
            api_client.logic.reconnect_ui_signals()
            self.main_layout.addWidget(chat_window)
            chat_window.show()
            # Force show all message bubbles when restoring from cache
            if hasattr(chat_window, '_force_show_all_messages'):
                chat_window._force_show_all_messages()
        else:
            # Tạo mới chat window và cache lại
            chat_window = ChatWindow(chat_data, pyctalk_client=self.client)
            # Debug: Check values before creating Chat1v1Client
            print(f"[DEBUG][MainWindow] Creating Chat1v1Client with:")
            print(f"  chat_data={chat_data}")
            print(f"  current_user_id={chat_data.get('current_user_id')}")
            print(f"  friend_id={friend_id}")
            
            # Khởi tạo api_client và logic, gán logic cho chat_window
            api_client = Chat1v1Client(
                chat_window,
                pyctalk_client=self.client,
                current_user_id=chat_data['current_user_id'],
                friend_id=friend_id
            )
            # Sử dụng logic đã được tạo trong Chat1v1Client
            chat_window.logic = api_client.logic
            
            # Cache lại để dùng lại sau
            self.chat_windows_cache[friend_id] = (chat_window, api_client)
            
            self.main_layout.addWidget(chat_window)
            chat_window.show()
            
        self.current_chat_friend_id = friend_id

    def _handle_chat_friend_from_sidebar(self, friend_data):
        """Handle chat request from sidebar friends management"""
        print(f"[DEBUG][MainWindow] Chat request from sidebar: {friend_data}")
        self._open_chat_window_1v1(friend_data)

    def _show_main_view(self):
        """Hiển thị main view (card) và ẩn chat windows"""
        # Xóa tất cả widgets cũ trong main_layout (trừ topbar)
        widgets_to_remove = []
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            # Giữ lại topbar, xóa các widget khác
            if widget and getattr(widget, 'objectName', lambda: None)() != "topbar":
                widgets_to_remove.append(widget)
        for widget in widgets_to_remove:
            self.main_layout.removeWidget(widget)
            widget.hide()
        
        # Ẩn chat window hiện tại
        if self.current_chat_friend_id and self.current_chat_friend_id in self.chat_windows_cache:
            current_chat_window, _ = self.chat_windows_cache[self.current_chat_friend_id]
            current_chat_window.hide()
            # Không cần removeWidget nữa vì đã xóa ở trên

        # Hiển thị card_container
        try:
            if hasattr(self, 'card_container') and self.card_container:
                self.main_layout.addWidget(self.card_container, 1)
                self.card_container.show()
        except RuntimeError:
            # Widget đã bị xóa, tạo lại
            print("[DEBUG][MainWindow] card_container đã bị xóa, tạo lại")
            self._setup_main_card()
            if self.card_container:
                self.main_layout.addWidget(self.card_container, 1)
                self.card_container.show()
        
        self.current_chat_friend_id = None

    def _setup_main_content(self):
        """Setup main content area"""
        self.main_content = QtWidgets.QWidget()
        self.main_content.setObjectName("main_content")
        self.main_layout = QtWidgets.QVBoxLayout(self.main_content)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(12)
        self._setup_topbar()
        self._setup_main_card()
        self.outer_layout.addWidget(self.main_content, 1)
    
    def _setup_topbar(self):
        """Setup topbar widget"""
        self.topbar = TopBarWidget(self.username)
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
        """Setup main welcome card"""
        self.card_container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(self.card_container)
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
        self.main_layout.addWidget(self.card_container, 1)
    
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
    # self.btnGroupChat đã bị loại bỏ
        self.btnSettings.clicked.connect(self.show_settings)
        self.btnThemeToggle.clicked.connect(self.toggle_theme)
        
        # Avatar click to open profile
        if hasattr(self.topbar, 'avatar_clicked'):
            self.topbar.avatar_clicked.connect(self._open_my_profile)
        
        # Sidebar signal connections
        if hasattr(self.sidebar, '_handle_chat_friend_from_management'):
            # Override the sidebar's chat handler to use main window's method
            self.sidebar._handle_chat_friend_from_management = self._handle_chat_friend_from_sidebar
        
        # Window events
        self.main_window.closeEvent = self.closeEvent
        
        # Groups list double-click
        if hasattr(self.groups_list, 'group_selected'):
            self.groups_list.group_selected.connect(self.on_group_double_clicked)
    
    def _apply_theme(self):
        """Apply theme based on current mode"""
        if hasattr(self, 'current_theme') and self.current_theme == 'light':
            self._apply_light_theme()
        else:
            self._apply_dark_theme()
    
    def _apply_light_theme(self):
        """Apply light theme matching login style"""
        self.centralwidget.setStyleSheet("""
            /* Light theme */
            QWidget {
                background-color: #f5f5f5;
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            
            /* Chat area */
            QScrollArea {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            
            /* Sidebar */
            QListWidget {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                selection-background-color: #3fc1c9;
                selection-color: white;
            }
            
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #eeeeee;
            }
            
            QListWidget::item:hover {
                background-color: #f0f8ff;
            }
            
            /* Input area */
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                color: #2c3e50;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3fc1c9;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #3fc1c9;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2fb3bb;
            }
            
            QPushButton:pressed {
                background-color: #1a8b93;
            }
            
            /* Theme toggle button */
            QPushButton#theme_toggle {
                background-color: #364f6b;
                color: white;
                padding: 8px;
                border-radius: 6px;
            }
            
            QPushButton#theme_toggle:hover {
                background-color: #2a3e54;
            }
        """)
    
    def _apply_dark_theme(self):
        """Apply dark theme matching login style"""
        self.centralwidget.setStyleSheet("""
            /* Dark theme matching login */
            QWidget {
                background-color: #1e2a38;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            
            /* Chat area */
            QScrollArea {
                background-color: #2c3e50;
                border: 1px solid #364f6b;
                border-radius: 8px;
            }
            
            /* Sidebar */
            QListWidget {
                background-color: #364f6b;
                border: 1px solid #4a5f7a;
                border-radius: 8px;
                selection-background-color: #3fc1c9;
                selection-color: white;
            }
            
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #4a5f7a;
                color: #ffffff;
            }
            
            QListWidget::item:hover {
                background-color: #4a5f7a;
            }
            
            /* Input area */
            QLineEdit, QTextEdit {
                background-color: #fafdff;
                border: 2px solid #3fc1c9;
                border-radius: 8px;
                padding: 8px;
                color: #2c3e50;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border-color: #a05a00;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #3fc1c9;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2fb3bb;
            }
            
            QPushButton:pressed {
                background-color: #1a8b93;
            }
            
            /* Theme toggle button */
            QPushButton#theme_toggle {
                background-color: #a05a00;
                color: white;
                padding: 8px;
                border-radius: 6px;
            }
            
            QPushButton#theme_toggle:hover {
                background-color: #8a4a00;
            }
        """)
    
    def _apply_modern_theme(self):
        """Apply modern theme matching login/register style"""
        self.centralwidget.setStyleSheet("""
            /* Main background matching login */
            QWidget { 
                background: #1e2a38; 
                color: #fafdff; 
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            /* Sidebar styling */
            QFrame#sidebar { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a3441, stop:1 #1e2a38);
                border: 2px solid #3fc1c9;
                border-radius: 20px;
                margin: 5px;
            }
            
            /* Top bar styling */
            QFrame#topbar { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3fc1c9, stop:1 #364f6b);
                border: none;
                border-radius: 15px;
                margin: 5px;
            }
            
            /* Main content area */
            QFrame#main_card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafdff, stop:1 #e8f4f8);
                border: 2px solid #3fc1c9;
                border-radius: 25px;
                margin: 5px;
                color: #1e2a38;
            }
            
            /* Modern buttons */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3fc1c9, stop:1 #2b8a94);
                color: white; 
                border: none; 
                border-radius: 15px; 
                padding: 12px 20px; 
                font-weight: 600; 
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover { 
                background-color: #36b3bb;
            }
            QPushButton:pressed { 
                background-color: #2da5ad;
            }
            
            /* Tab styling */
            QTabWidget::pane { 
                border: 2px solid #3fc1c9; 
                border-radius: 15px;
                background: #fafdff;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3fc1c9, stop:1 #2b8a94);
                border: none;
                border-radius: 12px;
                padding: 10px 18px; 
                margin: 3px; 
                font-weight: 600; 
                color: white;
                min-width: 80px;
            }
            QTabBar::tab:selected { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a05a00, stop:1 #7a4300);
                color: white;
                border: 2px solid #fafdff;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #364f6b, stop:1 #2a3441);
            }
            
            /* List widgets */
            QListWidget { 
                border: 2px solid #3fc1c9;
                border-radius: 15px;
                padding: 10px; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafdff, stop:1 #e8f4f8);
                color: #1e2a38;
            }
            QListWidget::item { 
                padding: 15px; 
                border-radius: 12px; 
                margin: 3px;
                background: transparent; 
                border: 1px solid transparent;
                font-weight: 500;
            }
            QListWidget::item:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3fc1c9, stop:1 #2b8a94);
                color: white;
                border: 1px solid #fafdff;
            }
            QListWidget::item:selected { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a05a00, stop:1 #7a4300);
                color: white;
                border: 2px solid #fafdff;
                font-weight: 600;
            }
            
            /* Input fields */
            QLineEdit {
                padding: 12px 18px; 
                border: 2px solid #3fc1c9; 
                border-radius: 20px;
                background: #fafdff; 
                font-size: 15px;
                color: #1e2a38;
            }
            QLineEdit:focus { 
                border: 2.5px solid #364f6b;
                background: white;
            }
            QLineEdit::placeholder {
                color: #7a5a1e;
                font-style: italic;
            }
            
            /* Text areas */
            QTextEdit { 
                border: 2px solid #3fc1c9; 
                border-radius: 15px; 
                background: #fafdff;
                padding: 12px; 
                font-size: 14px;
                color: #1e2a38;
            }
            QTextEdit:focus {
                border: 2.5px solid #364f6b;
                background: white;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background: #1e2a38;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3fc1c9;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #364f6b;
            }
            
            /* Labels */
            QLabel {
                color: #fafdff;
                font-weight: 500;
            }
            
            /* Menu and status bar */
            QMenuBar {
                background: #1e2a38;
                color: #fafdff;
                border: none;
                padding: 5px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
                border-radius: 8px;
            }
            QMenuBar::item:selected {
                background: #3fc1c9;
            }
            
            QStatusBar {
                background: #1e2a38;
                color: #3fc1c9;
                border-top: 1px solid #3fc1c9;
                font-weight: 500;
            }
        """)
        
        if hasattr(self, 'btnThemeToggle'):
            self.btnThemeToggle.setText("�")
    
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
            logger.error(f"[Ui_MainWindow] Lỗi kiểm tra kết nối: {e}")
            self._update_connection_status(False)
    
    def _update_connection_status(self, is_connected: bool):
        """Update UI based on connection status"""
        self.is_connected = is_connected
        self.status_indicator.setText("🟢 Đã kết nối" if is_connected else "🔴 Mất kết nối")
        self.status_connection.setText("Kết nối ổn định" if is_connected else "Đang kết nối lại...")
    # self.btnGroupChat đã bị loại bỏ
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
        MainWindow.setWindowTitle(_translate("MainWindow", f"🚀 PycTalk - {self.username}"))
        MainWindow.setWindowIcon(QtGui.QIcon())  # Could add custom icon later
    
    def _open_my_profile(self):
        """Open current user's profile window"""
        try:
            # Check if profile window is already open
            if hasattr(self, '_profile_window') and self._profile_window and self._profile_window.isVisible():
                print("[DEBUG] Profile window already open, bringing to front")
                self._profile_window.raise_()
                self._profile_window.activateWindow()
                return
                
            print(f"[DEBUG] Opening profile for user: {self.username} (ID: {self.user_id})")
            self._profile_window = MyProfileWindow(
                client=self.client,
                user_id=self.user_id,
                username=self.username,
                parent=self.main_window
            )
            self._profile_window.show()
        except Exception as e:
            print(f"[ERROR] Failed to open profile window: {e}")
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "Lỗi",
                f"Không thể mở cửa sổ hồ sơ: {str(e)}"
            )
    
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
        self.change_theme(new_theme)
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
            import asyncio
            async def load_groups():
                response = await api_client.get_user_groups(int(user_id))
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
            asyncio.create_task(load_groups())
        except Exception as e:
            self.groups_list.clear()
            self.groups_list.addItem(f"Lỗi tải nhóm: {e}")
    
    def on_logout_clicked(self):
        """Handle logout button click with confirmation"""
        try:
            # Hiển thị confirmation dialog
            reply = QtWidgets.QMessageBox.question(
                self.main_window,
                "Xác nhận đăng xuất",
                "Bạn có chắc chắn muốn đăng xuất?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            
            # Nếu user chọn No, không làm gì cả
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                return
            
            # Nếu user chọn Yes, thực hiện đăng xuất
            if not self.client:
                QtWidgets.QMessageBox.information(
                    self.main_window, 
                    "Đăng xuất", 
                    "Demo logout - chưa kết nối client thực tế."
                )
                self._logout_and_show_login()
                return
                
            self.logout_handler = LogoutHandler(self.client, self.main_window)
            # Gọi async logout
            asyncio.create_task(self.logout_handler.logout(self.username))
            
        except Exception as e:
            logger.error(f"[Ui_MainWindow] Lỗi đăng xuất: {e}")
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "Lỗi đăng xuất",
                f"Có lỗi xảy ra khi đăng xuất: {str(e)}"
            )
    
    def _logout_and_show_login(self):
        """Chuyển về trang đăng nhập"""
        try:
            # Import ở đây để tránh circular import
            from client.Login.login_signIn import LoginWindow
            
            # Tạo và hiện trang đăng nhập
            self.login_window = LoginWindow()
            self.login_window.show()
            
            # Đóng cửa sổ hiện tại
            self.main_window.close()
            
        except Exception as e:
            logger.error(f"[Ui_MainWindow] Lỗi chuyển về trang đăng nhập: {e}")
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "Lỗi",
                f"Không thể chuyển về trang đăng nhập: {str(e)}"
            )
    
    def on_group_chat_clicked(self):
        """Handle group chat button click: đã loại bỏ GroupChatWindow"""
        QtWidgets.QMessageBox.information(
            self.main_window,
            "Thông báo",
            "Chức năng chat nhóm đã được loại bỏ."
        )
    
    def on_group_double_clicked(self, group_data):
        """Khi click vào nhóm, chỉ còn khung chat nhóm, khung welcome phải biến mất hoàn toàn"""
        # Chỉ log khi chuyển nhóm
        logger.info(f"[Ui_MainWindow] Chuyển sang nhóm: {group_data.get('group_name')} (ID: {group_data.get('group_id')})")
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
        
        # Xóa tham chiếu đến các widget đã bị xóa
        self.status_message = None
        self.card_container = None  # Đặt về None vì đã bị xóa
        # Thêm khung chat nhóm mới
        print(f"[DEBUG] Creating EmbeddedGroupChatWidget with user_id={self.user_id}, username='{self.username}'")
        chat_widget = EmbeddedGroupChatWidget(self.client, self.user_id, self.username, group_data)
        self.main_layout.addWidget(chat_widget, 1)
        # Luôn reload lại tin nhắn khi chuyển nhóm
        if hasattr(chat_widget, 'logic'):
            import asyncio
            asyncio.create_task(chat_widget.logic.load_group_messages(offset=0))
    
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
            # Hide tray icon
            if self.notification_manager.tray_icon:
                self.notification_manager.tray_icon.hide()
            logger.info("[Ui_MainWindow] Đã cleanup tài nguyên thành công")
        except Exception as e:
            logger.error(f"[Ui_MainWindow] Lỗi khi cleanup: {e}")
