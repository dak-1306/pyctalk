import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from client.Group_chat.group_api_client import GroupAPIClient
from client.Group_chat.group_chat_logic import GroupChatLogic
import asyncio

logger = logging.getLogger(__name__)

class EmbeddedGroupChatWidget(QtWidgets.QWidget):
    def __init__(self, client, user_id, username, group_data):
        super().__init__()
        self.api_client = GroupAPIClient(client)
        self.logic = GroupChatLogic(self, self.api_client, user_id, username)
        self.user_id = user_id
        self.username = username
        self.group_data = group_data
        self._setupUI()
        self.logic.current_group = group_data
        import asyncio
        asyncio.create_task(self.logic.load_group_messages())

    def _setupUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.group_info_label = QtWidgets.QLabel(f"Nhóm: {self.group_data['group_name']} (ID: {self.group_data['group_id']})")
        layout.addWidget(self.group_info_label)
        self.messages_area = QtWidgets.QTextEdit()
        self.messages_area.setReadOnly(True)
        layout.addWidget(self.messages_area)
        input_layout = QtWidgets.QHBoxLayout()
        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Nhập tin nhắn...")
        input_layout.addWidget(self.message_input)
        self.send_btn = QtWidgets.QPushButton("Gửi")
        self.send_btn.clicked.connect(lambda: asyncio.create_task(self.send_message()))
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def display_messages(self, messages, offset, username):
        if offset == 0:
            self.messages_area.clear()
        for msg in messages:
            sender = msg['sender_name']
            time_str = msg.get("time_send", "Unknown")
            if sender == username:
                self.messages_area.append(f"[Tôi - {time_str}]: {msg['content']}")
            else:
                self.messages_area.append(f"[{sender} - {time_str}]: {msg['content']}")

    def update_group_info(self, group_data):
        self.group_info_label.setText(f"Nhóm: {group_data['group_name']} (ID: {group_data['group_id']})")

    async def send_message(self):
        if not self.logic.current_group:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhóm trước")
            return
        content = self.message_input.text().strip()
        if not content:
            return
        response = await self.api_client.send_group_message(self.user_id, self.group_data["group_id"], content)
        if response and response.get("success"):
            self.message_input.clear()
            await self.logic.load_group_messages(offset=0)
        else:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể gửi tin nhắn")
