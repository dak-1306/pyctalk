import re
from datetime import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QListWidget, QMessageBox, QInputDialog, QProgressBar
)
from .threads import MessageSenderThread
from .api_client import APIClient

class GroupChatWindow(QDialog):
    def __init__(self, client, user_id, username):
        super().__init__()
        self.api_client = APIClient(client)
        self.client = client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.message_sender_thread = None
        self.setupUI()
        self.load_user_groups()

    def setupUI(self):
        self.setWindowTitle("PycTalk - Group Chat")
        self.setGeometry(100, 100, 800, 600)
        main_layout = QHBoxLayout()

        # === Left Panel ===
        left_panel = QVBoxLayout()
        groups_header = QHBoxLayout()
        groups_label = QLabel("Nhóm của bạn:")
        groups_label.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold))
        create_group_btn = QPushButton("Tạo nhóm")
        create_group_btn.clicked.connect(self.create_new_group)
        create_group_btn.setStyleSheet("background-color:#4CAF50;color:white;border-radius:5px;")
        groups_header.addWidget(groups_label)
        groups_header.addWidget(create_group_btn)

        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.select_group)
        self.groups_list.setMaximumWidth(250)

        left_panel.addLayout(groups_header)
        left_panel.addWidget(self.groups_list)

        # === Right Panel ===
        right_panel = QVBoxLayout()
        self.group_info_label = QLabel("Chọn một nhóm để bắt đầu chat")
        self.group_info_label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Weight.Bold))
        self.group_info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setStyleSheet("background-color:#f5f5f5;border:1px solid #ddd;")

        # Label trạng thái phía dưới vùng chat
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            "font-size: 13px; color: #3b82f6; margin-top: 4px; margin-bottom: 8px;"
        )
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Nhập tin nhắn và nhấn Enter...")
        self.message_input.setMinimumHeight(40)
        self.message_input.setStyleSheet(
            "font-size: 15px; "
            "border-radius: 10px; "
            "padding: 8px; "
            "border: 1px solid #b0b8c1; "
            "background-color: #f7f9fc; "
        )
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setEnabled(False)

        self.send_progress = QProgressBar()
        self.send_progress.setVisible(False)
        self.send_progress.setRange(0, 0)
        self.send_progress.setMaximumHeight(3)

        self.send_btn = QPushButton("Gửi")
        self.send_btn.setMinimumWidth(90)
        self.send_btn.setMinimumHeight(40)
        self.send_btn.setIcon(QtGui.QIcon.fromTheme("mail-send"))
        self.send_btn.setStyleSheet(
            "font-weight: bold; "
            "font-size: 15px; "
            "color: white; "
            "background-color: #3b82f6; "
            "border-radius: 10px; "
            "border: none; "
            "padding: 8px 18px; "
            "box-shadow: 0 2px 8px rgba(59,130,246,0.15); "
        )
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)

        input_layout.setSpacing(14)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)

        actions_layout = QHBoxLayout()
        self.add_member_btn = QPushButton("Thêm thành viên")
        self.add_member_btn.setToolTip("Thêm bạn vào nhóm")
        self.add_member_btn.setIcon(QtGui.QIcon.fromTheme("list-add"))
        self.add_member_btn.clicked.connect(self.add_member_dialog)
        self.add_member_btn.setEnabled(False)

        self.view_members_btn = QPushButton("Xem thành viên")
        self.view_members_btn.setToolTip("Xem danh sách thành viên nhóm")
        self.view_members_btn.setIcon(QtGui.QIcon.fromTheme("user-group"))
        self.view_members_btn.clicked.connect(self.view_members)
        self.view_members_btn.setEnabled(False)

        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.setToolTip("Tải lại tin nhắn mới nhất")
        self.refresh_btn.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
        self.refresh_btn.clicked.connect(self.refresh_messages)
        self.refresh_btn.setEnabled(False)

        self.load_more_btn = QPushButton("Tải thêm")
        self.load_more_btn.setToolTip("Xem thêm tin nhắn cũ")
        self.load_more_btn.setIcon(QtGui.QIcon.fromTheme("go-down"))
        self.load_more_btn.clicked.connect(self.load_more_messages)
        self.load_more_btn.setEnabled(False)

        # Căn đều và thêm khoảng cách giữa các nút
        for btn in [self.add_member_btn, self.view_members_btn, self.refresh_btn, self.load_more_btn]:
            btn.setMinimumWidth(150)
            btn.setMinimumHeight(40)
            btn.setStyleSheet(
                "margin-right: 12px; "
                "font-weight: bold; "
                "font-size: 16px; "
                "color: #222; "
                "background-color: #e0e7ef; "
                "border-radius: 8px; "
                "border: 1px solid #b0b8c1; "
            )
            actions_layout.addWidget(btn)

        right_panel.addWidget(self.group_info_label)
        right_panel.addWidget(self.messages_area)
        right_panel.addWidget(self.status_label)
        right_panel.addWidget(self.send_progress)
        right_panel.addLayout(input_layout)
        right_panel.addLayout(actions_layout)

        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        self.setLayout(main_layout)

    def closeEvent(self, event):
        if self.message_sender_thread and self.message_sender_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Xác nhận thoát",
                "Đang gửi tin nhắn. Bạn có chắc muốn thoát không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self.message_sender_thread.quit()
            self.message_sender_thread.wait(1000)
        # Nếu có thay đổi chưa lưu (ví dụ: tin nhắn chưa gửi)
        if self.message_input.text().strip():
            reply = QMessageBox.question(
                self,
                "Xác nhận thoát",
                "Bạn có tin nhắn chưa gửi. Bạn có chắc muốn thoát không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        super().closeEvent(event)

    def load_user_groups(self):
        response = self.api_client.send_request("get_user_groups", {"user_id": self.user_id})
        if not response:
            QMessageBox.critical(self, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            self.groups_list.clear()
            for group in response.get("groups", []):
                item_text = f"{group['group_name']} (ID: {group['group_id']})"
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, group)
                self.groups_list.addItem(item)
        else:
            QMessageBox.warning(self, "Lỗi", response.get("message", "Không thể tải danh sách nhóm"))

    def select_group(self, item):
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.current_group = group_data
        self.group_info_label.setText(f"Nhóm: {group_data['group_name']} (ID: {group_data['group_id']})")
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.add_member_btn.setEnabled(True)
        self.view_members_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.message_offset = 0
        self.load_group_messages()
        self.load_more_btn.setEnabled(True)

    def load_group_messages(self, offset=0, limit=50):
        if not self.current_group:
            return
        response = self.api_client.send_request("get_group_messages", {
            "group_id": self.current_group["group_id"],
            "user_id": self.user_id,
            "limit": limit,
            "offset": offset
        })
        if not response:
            QMessageBox.critical(self, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            if offset == 0:
                self.messages_area.clear()
            total_msgs = len(response.get("messages", []))
            for msg in response.get("messages", []):
                if msg["time_send"]:
                    try:
                        dt = datetime.fromisoformat(msg["time_send"])
                        time_str = dt.strftime("%H:%M:%S")
                    except:
                        time_str = msg["time_send"]
                else:
                    time_str = "Unknown"
                if msg['sender_name'] == self.username:
                    # Tin nhắn của mình: căn phải, màu xanh, bo góc, bóng nhẹ
                    self.messages_area.append(
                        f'<div style="display:flex;justify-content:flex-end;margin:8px 0;">'
                        f'<div style="max-width:60%;background:#e6f3ff;border-radius:16px 16px 4px 16px;padding:10px 16px;box-shadow:0 2px 8px rgba(59,130,246,0.08);">'
                        f'<div style="font-size:13px;color:#3b82f6;text-align:right;">Tôi • {time_str}</div>'
                        f'<div style="font-size:15px;color:#222;text-align:right;">{msg["content"]}</div>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    # Tin nhắn người khác: căn trái, màu xám, bo góc
                    self.messages_area.append(
                        f'<div style="display:flex;justify-content:flex-start;margin:8px 0;">'
                        f'<div style="max-width:60%;background:#f3f4f6;border-radius:16px 16px 16px 4px;padding:10px 16px;box-shadow:0 2px 8px rgba(59,130,246,0.04);">'
                        f'<div style="font-size:13px;color:#555;text-align:left;">{msg["sender_name"]} • {time_str}</div>'
                        f'<div style="font-size:15px;color:#222;text-align:left;">{msg["content"]}</div>'
                        f'</div>'
                        f'</div>'
                    )
            # Hiển thị số lượng tin nhắn đã tải
            self.status_label.setText(f"Đang xem {total_msgs} tin nhắn.")
            # Tự động cuộn xuống cuối khi có tin nhắn mới
            self.messages_area.verticalScrollBar().setValue(self.messages_area.verticalScrollBar().maximum())

    def send_message(self):
        if not self.current_group:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhóm trước")
            return
        content = self.message_input.text().strip()
        if not content:
            return
        if self.message_sender_thread and self.message_sender_thread.isRunning():
            return
        self.show_sending_state()
        request_data = {
            "action": "send_group_message",
            "data": {
                "sender_id": self.user_id,
                "group_id": self.current_group["group_id"],
                "content": content
            }
        }
        self.message_sender_thread = MessageSenderThread(self.client, request_data)
        self.message_sender_thread.message_sent.connect(self.on_message_sent)
        self.message_sender_thread.error_occurred.connect(self.on_message_error)
        self.message_sender_thread.start()

    def show_sending_state(self):
        self.send_progress.setVisible(True)
        self.message_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Đang gửi...")

    def hide_sending_state(self):
        self.send_progress.setVisible(False)
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Gửi")

    def on_message_sent(self, response):
        self.hide_sending_state()
        if not response:
            QMessageBox.critical(self, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            content = self.message_input.text().strip()
            self.message_input.clear()
            message_data = response.get("message_data", {})
            # Hiển thị thời gian gửi từ server
            if message_data.get("time_send"):
                try:
                    dt = datetime.fromisoformat(message_data["time_send"])
                    time_str = dt.strftime("%H:%M:%S")
                except Exception:
                    time_str = message_data["time_send"]
            else:
                time_str = "Now"
            self.messages_area.append(
                f'<div style="display:flex;justify-content:flex-end;margin:8px 0;">'
                f'<div style="max-width:60%;background:#e6f3ff;border-radius:16px 16px 4px 16px;padding:10px 16px;box-shadow:0 2px 8px rgba(59,130,246,0.08);">'
                f'<div style="font-size:13px;color:#3b82f6;text-align:right;">Tôi • {time_str}</div>'
                f'<div style="font-size:15px;color:#222;text-align:right;">{content}</div>'
                f'</div>'
                f'</div>'
            )
            self.messages_area.verticalScrollBar().setValue(self.messages_area.verticalScrollBar().maximum())
        else:
            QMessageBox.warning(self, "Lỗi", response.get("message", "Không thể gửi tin nhắn"))

    def on_message_error(self, error_message):
        self.hide_sending_state()
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
