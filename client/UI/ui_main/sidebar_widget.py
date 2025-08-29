from PyQt6 import QtCore, QtGui, QtWidgets
import asyncio
class SidebarWidget(QtWidgets.QFrame):
    def __init__(self, has_friends_ui, client, user_id, username, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(320)  # Tăng width để 2 tabs hiển thị vừa vặn
        self.setStyleSheet("""
            SidebarWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc,
                    stop:1 #e2e8f0);
                border-right: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        self.client = client
        self.user_id = user_id
        self.username = username
        self.has_friends_ui = has_friends_ui
        self._setup_ui()

    def _setup_ui(self):
        sidebar_layout = QtWidgets.QVBoxLayout(self)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Compact menu bar
        self._setup_compact_menu(sidebar_layout)

        # Add some spacing and visual separation
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: rgba(0, 0, 0, 0.1);
                margin: 0px 8px;
            }
        """)
        sidebar_layout.addWidget(separator)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)

        # Disable scroll buttons and elide mode for clean display
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.tabBar().setElideMode(QtCore.Qt.TextElideMode.ElideNone)
        self.tabWidget.tabBar().setExpanding(True)  # Make tabs expand to fill available space

        # Custom styling for tabs
        self.tabWidget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
                border-radius: 0px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(248, 250, 252, 0.95));
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 10px 6px;
                margin: 0px;
                font-size: 11px;
                font-weight: 600;
                color: #6b7280;
                min-width: 80px;
                max-width: 100px;
                flex: 1;
                transition: all 0.3s ease;
                text-align: center;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(99, 102, 241, 0.12),
                    stop:1 rgba(79, 70, 229, 0.08));
                color: #6366f1;
                border-color: rgba(99, 102, 241, 0.4);
                transform: translateY(-1px);
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f8fafc);
                color: #6366f1;
                border-color: rgba(99, 102, 241, 0.6);
                border-bottom: 3px solid #6366f1;
                font-weight: 700;
            }
            QTabBar::tab:first {
                margin-left: 0px;
                border-top-left-radius: 12px;
            }
            QTabBar::tab:last {
                margin-right: 0px;
                border-top-right-radius: 12px;
            }
            /* Hide scroll buttons */
            QTabBar::scroller {
                width: 0px;
            }
            QTabBar QToolButton {
                display: none;
            }
        """)

        self.tabWidget.currentChanged.connect(self._on_tab_changed)

        # Friends tab
        if self.has_friends_ui:
            self._setup_friends_tab()
        else:
            self._setup_fallback_friends_tab()

        # Groups tab
        self._setup_groups_tab()
        sidebar_layout.addWidget(self.tabWidget)

        # Remove the old action buttons section
        # self._setup_sidebar_actions(sidebar_layout)

    def _setup_compact_menu(self, layout):
        """Setup compact menu bar that changes based on selected tab"""
        # Menu container
        self.menu_container = QtWidgets.QFrame()
        self.menu_container.setFixedHeight(45)
        self.menu_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(248, 250, 252, 0.95));
                border-bottom: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 0px;
            }
        """)

        self.menu_layout = QtWidgets.QHBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(8, 4, 8, 4)
        self.menu_layout.setSpacing(4)

        # Initially show friends menu
        self._update_menu_for_tab(0)

        layout.addWidget(self.menu_container)

    def _on_tab_changed(self, index):
        """Handle tab change to update menu"""
        self._update_menu_for_tab(index)

    def _update_menu_for_tab(self, tab_index):
        """Update menu based on selected tab"""
        # Clear current menu
        while self.menu_layout.count():
            child = self.menu_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add stretch at the beginning
        self.menu_layout.addStretch()

        if tab_index == 0:  # Friends tab
            self._create_friends_menu()
        else:  # Groups tab
            self._create_groups_menu()

        # Add stretch at the end
        self.menu_layout.addStretch()

    def _create_friends_menu(self):
        """Create compact friends menu"""
        # Add Friend button
        add_btn = self._create_compact_button("👥", "Thêm bạn", self._show_add_friend_dialog)
        self.menu_layout.addWidget(add_btn)

        # Friend Requests button
        requests_btn = self._create_compact_button("📨", "Lời mời", self._show_friend_requests)
        self.menu_layout.addWidget(requests_btn)

        # Sent Requests button
        sent_btn = self._create_compact_button("📤", "Đã gửi", self._show_sent_requests)
        self.menu_layout.addWidget(sent_btn)

        # Manage Friends button
        manage_btn = self._create_compact_button("⚙️", "Quản lý", self._show_friends_management)
        self.menu_layout.addWidget(manage_btn)

        # Settings button (always visible)
        settings_btn = self._create_compact_button("🔧", "Cài đặt", self._show_settings)
        self.menu_layout.addWidget(settings_btn)

    def _create_groups_menu(self):
        """Create compact groups menu"""
        # Create Group button
        create_btn = self._create_compact_button("➕", "Tạo nhóm", self._show_create_group_window)
        self.menu_layout.addWidget(create_btn)

        # Join Group button
        join_btn = self._create_compact_button("🔗", "Tham gia", self._show_join_group_window)
        self.menu_layout.addWidget(join_btn)

        # Settings button (always visible)
        settings_btn = self._create_compact_button("🔧", "Cài đặt", self._show_settings)
        self.menu_layout.addWidget(settings_btn)

    def _create_compact_button(self, icon, tooltip, callback):
        """Create a compact icon button with hover effects"""
        btn = QtWidgets.QPushButton(icon)
        btn.setFixedSize(32, 32)
        btn.setToolTip(tooltip)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                padding: 4px;
                margin: 2px;
                color: #6b7280;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background-color: rgba(99, 102, 241, 0.15);
                border: 1px solid rgba(99, 102, 241, 0.3);
                color: #6366f1;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: rgba(99, 102, 241, 0.25);
                border: 1px solid rgba(99, 102, 241, 0.5);
                color: #4f46e5;
                transform: scale(0.95);
            }
            QPushButton:disabled {
                color: #d1d5db;
                background-color: transparent;
                border: none;
            }
        """)

        btn.clicked.connect(callback)
        return btn

    def _setup_friends_tab(self):
        try:
            from client.UI.messenger_ui.friend_list_window import FriendListWindow
            print(f"[DEBUG][SidebarWidget] Khởi tạo FriendListWindow với username={self.username}, user_id={self.user_id}, client={self.client}")
            self.friends_widget = FriendListWindow(
                self.username, user_id=self.user_id, client=self.client
            )
            friends_tab = QtWidgets.QWidget()
            f_lay = QtWidgets.QVBoxLayout(friends_tab)
            f_lay.setContentsMargins(0, 0, 0, 0)
            f_lay.addWidget(self.friends_widget)
            self.tabWidget.addTab(friends_tab, "�‍👨‍👦‍👦 Bạn bè")
        except Exception as e:
            print(f"[ERROR][SidebarWidget] Lỗi khi import/khởi tạo FriendListWindow: {e}")
            self._setup_fallback_friends_tab()

    def _setup_fallback_friends_tab(self):
        friends_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(friends_tab)
        search_bar = QtWidgets.QLineEdit()
        search_bar.setPlaceholderText("🔍 Tìm kiếm bạn bè...")
        layout.addWidget(search_bar)
        friends_list = QtWidgets.QListWidget()
        friends_list.addItem("Không có dữ liệu bạn bè hoặc không kết nối được database.")
        layout.addWidget(friends_list)
        self.tabWidget.addTab(friends_tab, "�‍👨‍👦‍👦 Bạn bè")

    def _setup_groups_tab(self):
        groups_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(groups_tab)


        # Thay thế QListWidget bằng GroupListWindow
        from client.UI.messenger_ui.group_list_window import GroupListWindow
        self.groups_widget = GroupListWindow(user_id=self.user_id, client=self.client)
        layout.addWidget(self.groups_widget)
        # Đảm bảo tương thích với code cũ
        self.groups_list = self.groups_widget

        self.tabWidget.addTab(groups_tab, "�‍👩‍👧‍👦 Nhóm")

    def _create_modern_button(self, text, icon_name, callback):
        """Create a modern styled button"""
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                color: #374151;
                text-align: left;
                margin: 1px 0px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                border-color: rgba(99, 102, 241, 0.3);
                color: #6366f1;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
            }
        """)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.clicked.connect(callback)

        # Store button reference for later access
        setattr(self, f"btn{icon_name}", btn)

        return btn

    def _show_add_friend_dialog(self):
        from Add_friend.friend import FriendClient
        username, ok = QtWidgets.QInputDialog.getText(
            self, "Kết bạn mới", "Nhập username muốn kết bạn:"
        )
        if not ok or not username:
            return

        friend_client = FriendClient(self.client)

        def on_friend_request_response(response):
            print(f"[DEBUG] Friend request response: {response}")
            if response and response.get("status") == "ok":
                QtWidgets.QMessageBox.information(
                    self, "Thành công", f"Đã gửi yêu cầu kết bạn tới {username}!"
                )
            else:
                error_msg = (
                    response.get("message", "Gửi yêu cầu thất bại.")
                    if response else "Không nhận được phản hồi từ server."
                )
                print(f"[DEBUG] Friend request error: {error_msg}")
                QtWidgets.QMessageBox.warning(self, "Lỗi", error_msg)

        import asyncio
        asyncio.create_task(friend_client.send_friend_request(username, on_friend_request_response))

    def _show_friend_requests(self):
        """Hiển thị cửa sổ lời mời kết bạn"""
        from client.UI.messenger_ui.friend_requests_window import FriendRequestsWindow
        
        self.friend_requests_window = FriendRequestsWindow(self.client, self.username, self)
        self.friend_requests_window.friend_added.connect(self._on_friend_added)
        self.friend_requests_window.show()
        
    def _show_sent_requests(self):
        """Hiển thị cửa sổ lời mời đã gửi"""
        from client.UI.messenger_ui.sent_requests_window import SentRequestsWindow
        
        self.sent_requests_window = SentRequestsWindow(self.client, self.username, self)
        self.sent_requests_window.show()
        
    def _show_friends_management(self):
        """Hiển thị cửa sổ quản lý bạn bè"""
        from client.UI.messenger_ui.friends_management_window import FriendsManagementWindow
        
        self.friends_management_window = FriendsManagementWindow(self.client, self.username, self.user_id, self)
        # Connect signal để xử lý khi user chọn nhắn tin với bạn bè
        self.friends_management_window.chat_friend_requested.connect(self._handle_chat_friend_from_management)
        self.friends_management_window.show()
        
    def _handle_chat_friend_from_management(self, friend_data):
        """Handle when user wants to chat with a friend from friends management"""
        print(f"[DEBUG] Chat with friend requested from management: {friend_data}")
        
        # Find the parent window (main window) and call the chat method
        parent_window = self.parent()
        while parent_window and not hasattr(parent_window, '_open_chat_window_1v1'):
            parent_window = parent_window.parent()
            
        if parent_window and hasattr(parent_window, '_open_chat_window_1v1'):
            parent_window._open_chat_window_1v1(friend_data)
        else:
            print("[ERROR] Could not find main window to open chat")
        
    def _on_friend_added(self, friend_data):
        """Handle when a friend is added from friend requests"""
        # Refresh friends list
        if hasattr(self, 'friends_widget') and hasattr(self.friends_widget, 'refresh_conversations'):
            self.friends_widget.refresh_conversations()

    def _show_create_group_window(self):
        """Hiển thị cửa sổ tạo nhóm mới"""
        from client.UI.messenger_ui.create_group_window import CreateGroupWindow
        
        self.create_group_window = CreateGroupWindow(self.client, self.username, self.user_id, self)
        # Connect signal để refresh danh sách nhóm khi tạo nhóm thành công
        self.create_group_window.group_created.connect(self._on_group_created)
        self.create_group_window.show()
        
    def _on_group_created(self, group_data):
        """Handle when a new group is created"""
        print(f"[DEBUG] New group created: {group_data}")
        
        # Refresh groups list
        if hasattr(self, 'groups_widget') and hasattr(self.groups_widget, 'refresh_groups'):
            self.groups_widget.refresh_groups()
        elif hasattr(self, 'groups_widget') and hasattr(self.groups_widget, '_load_groups'):
            asyncio.create_task(self.groups_widget._load_groups())

    def _show_join_group_window(self):
        """Hiển thị cửa sổ tham gia nhóm"""
        # Create a simple join group dialog since join_group_window doesn't exist
        group_id, ok = QtWidgets.QInputDialog.getText(
            self, "🔗 Tham gia nhóm", "Nhập ID nhóm muốn tham gia:"
        )
        if not ok or not group_id:
            return
            
        # TODO: Implement actual join group functionality
        QtWidgets.QMessageBox.information(
            self, "Thông báo", f"Chức năng tham gia nhóm với ID '{group_id}' sẽ được phát triển sau!"
        )
        
    def _on_group_joined(self, group_data):
        """Handle when user joins a group"""
        print(f"[DEBUG] User joined group: {group_data}")
        
        # Refresh groups list
        if hasattr(self, 'groups_widget') and hasattr(self.groups_widget, 'refresh_groups'):
            self.groups_widget.refresh_groups()
        elif hasattr(self, 'groups_widget') and hasattr(self.groups_widget, '_load_groups'):
            asyncio.create_task(self.groups_widget._load_groups())
            
    def _show_settings(self):
        """Show settings dialog"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("⚙️ Cài đặt")
        dialog.setModal(True)
        dialog.resize(450, 350)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme selection
        theme_group = QtWidgets.QGroupBox("🎨 Giao diện")
        theme_layout = QtWidgets.QVBoxLayout(theme_group)
        
        light_radio = QtWidgets.QRadioButton("☀️ Giao diện sáng")
        dark_radio = QtWidgets.QRadioButton("🌙 Giao diện tối")
        
        # Get current theme from parent window
        parent_window = self.parent()
        while parent_window and not hasattr(parent_window, 'current_theme'):
            parent_window = parent_window.parent()
            
        if parent_window and hasattr(parent_window, 'current_theme'):
            if parent_window.current_theme == "light":
                light_radio.setChecked(True)
            else:
                dark_radio.setChecked(True)
        
        theme_layout.addWidget(light_radio)
        theme_layout.addWidget(dark_radio)
        layout.addWidget(theme_group)
        
        # Notifications
        notif_group = QtWidgets.QGroupBox("🔔 Thông báo")
        notif_layout = QtWidgets.QVBoxLayout(notif_group)
        
        show_notifs = QtWidgets.QCheckBox("Hiển thị thông báo hệ thống")
        sound_notifs = QtWidgets.QCheckBox("Âm thanh thông báo")
        
        # Get settings from parent window
        if parent_window and hasattr(parent_window, 'settings'):
            show_notifs.setChecked(parent_window.settings.get("show_notifications", True))
            sound_notifs.setChecked(parent_window.settings.get("sound_notifications", True))
        
        notif_layout.addWidget(show_notifs)
        notif_layout.addWidget(sound_notifs)
        layout.addWidget(notif_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QtWidgets.QPushButton("✅ OK")
        cancel_button = QtWidgets.QPushButton("❌ Hủy")
        
        def save_settings():
            # Save theme
            theme = "light" if light_radio.isChecked() else "dark"
            if parent_window and hasattr(parent_window, 'change_theme'):
                parent_window.change_theme(theme)
            
            # Save notification settings
            if parent_window and hasattr(parent_window, 'settings'):
                parent_window.settings.set("show_notifications", show_notifs.isChecked())
                parent_window.settings.set("sound_notifications", sound_notifs.isChecked())
            
            dialog.accept()
        
        ok_button.clicked.connect(save_settings)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
