from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from .chat_list_item_widget import ChatListItem

class GroupListWindow(QtWidgets.QWidget):
    """Group list window for messenger (dùng lại UI của ChatListItemWidget)"""
    group_selected = pyqtSignal(dict)  # Signal when group is selected to chat

    def __init__(self, user_id=None, client=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.client = client
        self._setup_ui()
        import asyncio
        asyncio.create_task(self._load_groups())

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search bar
        self._create_search_bar(layout)
        # Groups list
        self._create_groups_list(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)

    def _create_search_bar(self, main_layout):
        search_container = QtWidgets.QWidget()
        search_container.setFixedHeight(60)
        search_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #f0f2f5;
            }
        """)
        search_layout = QtWidgets.QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 10, 20, 10)
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm nhóm...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 15px;
                color: #1c1e21;
            }
            QLineEdit:focus {
                background-color: #e4e6ea;
                border: 2px solid #0084FF;
            }
            QLineEdit::placeholder {
                color: #8a8d91;
            }
        """)
        self.search_input.textChanged.connect(self._filter_groups)
        search_layout.addWidget(self.search_input)
        main_layout.addWidget(search_container)

    def _create_groups_list(self, main_layout):
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: #c8c8c8;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
        """)
        self.groups_container = QtWidgets.QWidget()
        self.groups_layout = QtWidgets.QVBoxLayout(self.groups_container)
        self.groups_layout.setContentsMargins(10, 10, 10, 10)
        self.groups_layout.setSpacing(5)
        self.groups_layout.addStretch()
        scroll_area.setWidget(self.groups_container)
        main_layout.addWidget(scroll_area)

    async def _load_groups(self):
        """Lấy danh sách nhóm từ server qua GroupAPIClient"""
        if self.client is None or self.user_id is None:
            self._display_groups([])
            return
        try:
            from Group_chat.group_api_client import GroupAPIClient
            api_client = GroupAPIClient(self.client)
            response = await api_client.get_user_groups(int(self.user_id))
            groups = response.get("groups", []) if response and response.get("success") else []
            # Truyền nguyên group dict vào UI
            self._display_groups(groups)
        except Exception as e:
            print(f"[ERROR][GroupListWindow] Error loading groups: {e}")
            self._display_groups([])

    def _display_groups(self, groups):
        while self.groups_layout.count() > 1:
            child = self.groups_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for group in groups:
            chat_item = ChatListItem({
                'friend_id': group.get('group_id'),
                'friend_name': group.get('group_name', str(group.get('group_id'))),
                'last_message': group.get('last_message', ''),
                'last_message_time': group.get('last_message_time', ''),
                'unread_count': group.get('unread_count', 0),
                'member_count': group.get('member_count', 0),
                'original_group': group  # lưu group gốc
            })
            # Truyền đúng group gốc vào signal
            chat_item.clicked.connect(lambda _, g=group: self._on_group_selected(g))
            self.groups_layout.insertWidget(self.groups_layout.count() - 1, chat_item)

    def _on_group_selected(self, chat_data):
        self.group_selected.emit(chat_data)

    def _filter_groups(self, search_text):
        search_text = search_text.lower()
        for i in range(self.groups_layout.count()):
            item = self.groups_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatListItem):
                chat_item = item.widget()
                group_name = chat_item.chat_data.get('friend_name', '').lower()
                last_message = chat_item.chat_data.get('last_message', '').lower()
                is_visible = (search_text in group_name or search_text in last_message)
                chat_item.setVisible(is_visible)

    def refresh_groups(self):
        import asyncio
        asyncio.create_task(self._load_groups())

    def add_group(self, group_data):
        chat_item = ChatListItem(group_data)
        chat_item.clicked.connect(self._on_group_selected)
        self.groups_layout.insertWidget(self.groups_layout.count() - 1, chat_item)

    def update_group(self, group_id, last_message, timestamp):
        for i in range(self.groups_layout.count()):
            item = self.groups_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatListItem):
                chat_item = item.widget()
                if chat_item.chat_data.get('friend_id') == group_id:
                    chat_item.chat_data['last_message'] = last_message
                    chat_item.chat_data['last_message_time'] = timestamp
                    chat_item.update_chat_data(chat_item.chat_data)
                    break
