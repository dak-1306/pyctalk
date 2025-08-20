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
        self.message_input.setFocus()

    def create_new_group(self):
        group_name, ok = QInputDialog.getText(self, "Tạo nhóm mới", "Tên nhóm:")
        if not ok or not group_name.strip():
            return
        response = self.api_client.send_request("create_group", {
            "group_name": group_name.strip(),
            "user_id": self.user_id
        })
        if not response:
            QMessageBox.critical(self, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            QMessageBox.information(self, "Thành công", f"Đã tạo nhóm '{group_name}' thành công!")
            self.load_user_groups()
        else:
            QMessageBox.warning(self, "Lỗi", response.get("message", "Không thể tạo nhóm"))

    def add_member_dialog(self):
        if not self.current_group:
            return
        response = self.api_client.send_request("get_friends", {"user_id": self.user_id})
        if not response:
            QMessageBox.critical(self, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        friends = response.get("friends", []) if response.get("success") else []
        if not friends:
            QMessageBox.warning(self, "Lỗi", "Không có bạn bè để thêm")
            return
        friend_names = [f"{f['username']} (ID: {f['user_id']})" for f in friends]
        selected, ok = QInputDialog.getItem(self, "Thêm thành viên", "Chọn bạn để thêm:", friend_names, 0, False)
        if not ok or not selected:
            return
        match = re.search(r'ID: (\d+)', selected)
        if not match:
            QMessageBox.warning(self, "Lỗi", "Không thể lấy ID bạn bè")
            return
        add_user_id = int(match.group(1))
        response = self.api_client.send_request("add_member_to_group", {
            "group_id": self.current_group["group_id"],
            "user_id": add_user_id,
            "admin_id": self.user_id
        })
        if not response:
            QMessageBox.critical(self, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            QMessageBox.information(self, "Thành công", "Đã thêm thành viên thành công!")
            self.view_members()
        else:
            QMessageBox.critical(self, "Lỗi quyền", response.get("message", "Không thể thêm thành viên"))

    def view_members(self):
        if not self.current_group:
            return
        response = self.api_client.send_request("get_group_members", {
            "group_id": self.current_group["group_id"],
            "user_id": self.user_id
        })
        if not response:
            QMessageBox.critical(self, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            members_text = "Thành viên nhóm:\n\n"
            for m in response.get("members", []):
                members_text += f"• {m['username']} (ID: {m['user_id']})\n"
            QMessageBox.information(self, f"Thành viên nhóm {self.current_group['group_name']}", members_text)
        else:
            QMessageBox.warning(self, "Lỗi", response.get("message", "Không thể tải danh sách thành viên"))

    def refresh_messages(self):
        if self.current_group:
            self.message_offset = 0
            self.load_group_messages(offset=0, limit=50)

    def load_more_messages(self):
        if not self.current_group:
            return
        self.message_offset = getattr(self, 'message_offset', 0) + 50
        self.load_group_messages(offset=self.message_offset, limit=50)