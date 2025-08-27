from PyQt6 import QtCore, QtGui, QtWidgets
import asyncio
class SidebarWidget(QtWidgets.QFrame):
    def __init__(self, has_friends_ui, client, user_id, username, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        self.client = client
        self.user_id = user_id
        self.username = username
        self.has_friends_ui = has_friends_ui
        self._setup_ui()

    def _setup_ui(self):
        sidebar_layout = QtWidgets.QVBoxLayout(self)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)

        # Friends tab
        if self.has_friends_ui:
            self._setup_friends_tab()
        else:
            self._setup_fallback_friends_tab()

        # Groups tab
        self._setup_groups_tab()
        sidebar_layout.addWidget(self.tabWidget)

        # Action buttons
        self._setup_sidebar_actions(sidebar_layout)

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
            self.tabWidget.addTab(friends_tab, "👥 Bạn bè")
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
        self.tabWidget.addTab(friends_tab, "👥 Bạn bè")

    def _setup_groups_tab(self):
        groups_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(groups_tab)


        # Thay thế QListWidget bằng GroupListWindow
        from client.UI.messenger_ui.group_list_window import GroupListWindow
        self.groups_widget = GroupListWindow(user_id=self.user_id, client=self.client)
        layout.addWidget(self.groups_widget)
        # Đảm bảo tương thích với code cũ
        self.groups_list = self.groups_widget

        # Action buttons trong tab nhóm
        group_actions = QtWidgets.QHBoxLayout()
        self.create_group_btn = QtWidgets.QPushButton("+ Tạo nhóm")
        self.join_group_btn = QtWidgets.QPushButton("🔗 Tham gia")
        
        # Connect create group button
        self.create_group_btn.clicked.connect(self._show_create_group_window)
        
        group_actions.addWidget(self.create_group_btn)
        group_actions.addWidget(self.join_group_btn)
        layout.addLayout(group_actions)

        self.tabWidget.addTab(groups_tab, "👥 Nhóm")

    def _setup_sidebar_actions(self, layout):
        actions_frame = QtWidgets.QFrame()
        actions_layout = QtWidgets.QVBoxLayout(actions_frame)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        actions_layout.addWidget(separator)

        # Nút kết bạn mới
        self.btnAddFriend = QtWidgets.QPushButton("➕ Kết bạn")
        self.btnAddFriend.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        actions_layout.addWidget(self.btnAddFriend)

        # Nút xem lời mời kết bạn
        self.btnFriendRequests = QtWidgets.QPushButton("📩 Lời mời kết bạn")
        self.btnFriendRequests.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        actions_layout.addWidget(self.btnFriendRequests)

        # Nút xem lời mời đã gửi
        self.btnSentRequests = QtWidgets.QPushButton("📤 Lời mời đã gửi")
        self.btnSentRequests.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        actions_layout.addWidget(self.btnSentRequests)

        # Nút quản lý bạn bè
        self.btnManageFriends = QtWidgets.QPushButton("👥 Quản lý bạn bè")
        self.btnManageFriends.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        actions_layout.addWidget(self.btnManageFriends)

        # Tích hợp logic gửi kết bạn
        self.btnAddFriend.clicked.connect(self._show_add_friend_dialog)
        
        # Tích hợp logic xem lời mời kết bạn
        self.btnFriendRequests.clicked.connect(self._show_friend_requests)
        
        # Tích hợp logic xem lời mời đã gửi
        self.btnSentRequests.clicked.connect(self._show_sent_requests)
        
        # Tích hợp logic quản lý bạn bè
        self.btnManageFriends.clicked.connect(self._show_friends_management)

        self.btnSettings = QtWidgets.QPushButton("⚙️ Cài đặt")
        self.btnSettings.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        actions_layout.addWidget(self.btnSettings)

        layout.addWidget(actions_frame)

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
