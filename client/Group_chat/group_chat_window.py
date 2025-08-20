from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QListWidget, QProgressBar, QMessageBox
from .group_api_client import GroupAPIClient
from .group_chat_logic import GroupChatLogic
from .group_threads import GroupMessageSenderThread

class GroupChatWindow(QDialog):
    def __init__(self, client, user_id, username):
        super().__init__()
        self.api_client = GroupAPIClient(client)
        self.logic = GroupChatLogic(self, self.api_client, user_id, username)
        self.client = client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.message_sender_thread = None
        self.setupUI()
        self.logic.load_user_groups()

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
        item = QtWidgets.QListWidgetItem(text)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, data)
        return item

    def _on_group_selected(self, item):
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.logic.select_group(group_data)

    def update_group_info(self, group_data):
        self.group_info_label.setText(f"Nhóm: {group_data['group_name']} (ID: {group_data['group_id']})")

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

    def send_message(self):
        if not self.logic.current_group:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhóm trước")
            return
        content = self.message_input.text().strip()
        if not content:
            return
        request_data = {
            "action": "send_group_message",
            "data": {
                "sender_id": self.user_id,
                "group_id": self.logic.current_group["group_id"],
                "content": content
            }
        }
        self.message_sender_thread = GroupMessageSenderThread(self.client, request_data)
        self.message_sender_thread.message_sent.connect(self._on_message_sent)
        self.message_sender_thread.error_occurred.connect(self._on_message_error)
        self.message_sender_thread.start()

    def _on_message_sent(self, response):
        print(f"[DEBUG] Server response: {response}")
        # Đảm bảo response là dict và có key 'success' đúng kiểu bool
        if isinstance(response, dict) and response.get("success") is True:
            self.message_input.clear()
            self.logic.load_group_messages(offset=0)
        else:
            # Hiển thị thông báo lỗi kèm nội dung phản hồi để dễ debug
            QMessageBox.warning(self, "Lỗi", f"Không thể gửi tin nhắn. Phản hồi: {response}")

    def _on_message_error(self, error_message):
        QMessageBox.warning(self, "Lỗi", error_message)
