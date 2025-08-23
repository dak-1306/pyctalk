import re
import asyncio
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QListWidget, QProgressBar, QMessageBox, QInputDialog
)
from .group_api_client import GroupAPIClient
from .group_chat_logic import GroupChatLogic


class GroupChatWindow(QDialog):
    def __init__(self, client, user_id, username):
        print(f"[DEBUG] Khởi tạo GroupChatWindow với user_id={user_id}, username={username}")
        super().__init__()
        self.api_client = GroupAPIClient(client)
        self.logic = GroupChatLogic(self, self.api_client, user_id, username)
        self.client = client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.setupUI()

        print("[DEBUG] Gọi load_user_groups từ GroupChatWindow")
        asyncio.create_task(self.logic.load_user_groups())

    def setupUI(self):
        self.setWindowTitle("PycTalk - Group Chat")
        self.setGeometry(100, 100, 800, 600)
        main_layout = QHBoxLayout()

        # Left panel
        left_panel = QVBoxLayout()
        self.groups_list = QListWidget()
        self.groups_list.setMaximumWidth(250)
        self.groups_list.itemClicked.connect(self._on_group_selected)
        left_panel.addWidget(QLabel("Nhóm của bạn:"))
        left_panel.addWidget(self.groups_list)

        # Right panel
        right_panel = QVBoxLayout()
        self.group_info_label = QLabel("Chọn một nhóm để bắt đầu chat")
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Nhập tin nhắn...")
        self.message_input.returnPressed.connect(self.send_message)
        self.send_btn = QPushButton("Gửi")
        self.send_btn.clicked.connect(self.send_message)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)
        self.send_progress = QProgressBar()
        self.send_progress.setVisible(False)

        right_panel.addWidget(self.group_info_label)
        right_panel.addWidget(self.messages_area)
        right_panel.addWidget(self.send_progress)
        right_panel.addLayout(input_layout)

        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        self.setLayout(main_layout)

    def _make_group_item(self, text, data):
        print(f"[DEBUG] _make_group_item: text={text}, data={data}")
        item = QtWidgets.QListWidgetItem(text)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, data)
        print(f"[DEBUG] Item created: {item}")
        return item

    def _on_group_selected(self, item):
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        print(f"[DEBUG][GroupChatWindow] Nhóm được chọn: {group_data}")
        asyncio.create_task(self.logic.select_group(group_data))

    def update_group_info(self, group_data):
        self.group_info_label.setText(f"Nhóm: {group_data['group_name']} (ID: {group_data['group_id']})")

    def display_messages(self, messages, offset, username):
        print(f"[DEBUG][GroupChatWindow] display_messages called. offset={offset}, username={username}, messages={messages}")
        if offset == 0:
            self.messages_area.clear()
        for i, msg in enumerate(messages):
            sender = msg.get('sender_name', 'Unknown')
            time_str = msg.get("time_send", "Unknown")
            content = msg.get('content', '')
            print(f"[DEBUG][GroupChatWindow] Tin nhắn #{i}: sender={sender}, time={time_str}, content={content}")
            if sender == username:
                self.messages_area.append(f"[Tôi - {time_str}]: {content}")
            else:
                self.messages_area.append(f"[{sender} - {time_str}]: {content}")

    def send_message(self):
        """Gửi tin nhắn async"""
