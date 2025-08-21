from PyQt6 import QtCore, QtGui, QtWidgets

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
            from UI.messenger_ui.friend_list_window import FriendListWindow
            self.friends_widget = FriendListWindow(self.username, user_id=self.user_id, client=self.client)
            friends_tab = QtWidgets.QWidget()
            f_lay = QtWidgets.QVBoxLayout(friends_tab)
            f_lay.setContentsMargins(0, 0, 0, 0)
            f_lay.addWidget(self.friends_widget)
            self.tabWidget.addTab(friends_tab, "👥 Bạn bè")
        except Exception as e:
            self._setup_fallback_friends_tab()

    def _setup_fallback_friends_tab(self):
        friends_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(friends_tab)
        search_bar = QtWidgets.QLineEdit()
        search_bar.setPlaceholderText("🔍 Tìm kiếm bạn bè...")
        layout.addWidget(search_bar)
        friends_list = QtWidgets.QListWidget()
        # Không dùng dữ liệu ảo, chỉ hiển thị thông báo
        friends_list.addItem("Không có dữ liệu bạn bè hoặc không kết nối được database.")
        layout.addWidget(friends_list)
        self.tabWidget.addTab(friends_tab, "👥 Bạn bè")

    def _setup_groups_tab(self):
        groups_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(groups_tab)
        group_search = QtWidgets.QLineEdit()
        group_search.setPlaceholderText("🔍 Tìm nhóm...")
        layout.addWidget(group_search)
        from Group_chat.group_api_client import GroupAPIClient
        self.groups_list = QtWidgets.QListWidget()
        layout.addWidget(self.groups_list)
        try:
            api_client = GroupAPIClient(self.client)
            if self.user_id is None:
                self.groups_list.addItem("Không tìm thấy user_id")
            else:
                response = api_client.get_user_groups(int(self.user_id))
                if response and response.get("success"):
                    self.groups_list.clear()
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
            self.groups_list.addItem(f"Lỗi tải nhóm: {e}")
        group_actions = QtWidgets.QHBoxLayout()
        self.create_group_btn = QtWidgets.QPushButton("+ Tạo nhóm")
        self.join_group_btn = QtWidgets.QPushButton("🔗 Tham gia")
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

        # Tích hợp logic gửi kết bạn
        self.btnAddFriend.clicked.connect(self._show_add_friend_dialog)

        self.btnGroupChat = QtWidgets.QPushButton("🚀 Tạo Group Chat")
        self.btnGroupChat.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        actions_layout.addWidget(self.btnGroupChat)

        self.btnSettings = QtWidgets.QPushButton("⚙️ Cài đặt")
        self.btnSettings.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        actions_layout.addWidget(self.btnSettings)
        layout.addWidget(actions_frame)

    def _show_add_friend_dialog(self):
        from Add_friend.friend import FriendClient
        # Hiển thị dialog nhập username cần kết bạn
        username, ok = QtWidgets.QInputDialog.getText(self, "Kết bạn mới", "Nhập username muốn kết bạn:")
        if not ok or not username:
            return
        friend_client = FriendClient(self.client)
        response = friend_client.send_friend_request(username)
        if response and response.get("success"):
            QtWidgets.QMessageBox.information(self, "Thành công", f"Đã gửi yêu cầu kết bạn tới {username}!")
        else:
            error_msg = response.get("error", "Gửi yêu cầu thất bại.") if response else "Không nhận được phản hồi từ server."
            QtWidgets.QMessageBox.warning(self, "Lỗi", error_msg)

    # Có thể bổ sung các phương thức truy cập widget, reload, ... tại đây
