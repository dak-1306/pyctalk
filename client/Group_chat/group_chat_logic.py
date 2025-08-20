from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QInputDialog
import re

class GroupChatLogic:
    """Xử lý logic cho GroupChatWindow (tách riêng khỏi UI)"""

    def __init__(self, ui, api_client, user_id, username):
        self.ui = ui
        self.api_client = api_client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.message_offset = 0

    def load_user_groups(self):
        response = self.api_client.get_user_groups(self.user_id)
        if not response:
            QMessageBox.critical(self.ui, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            self.ui.groups_list.clear()
            for group in response.get("groups", []):
                item_text = f"{group['group_name']} (ID: {group['group_id']})"
                item = self.ui._make_group_item(item_text, group)
                self.ui.groups_list.addItem(item)
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải danh sách nhóm"))

    def select_group(self, group_data):
        self.current_group = group_data
        self.message_offset = 0
        self.ui.update_group_info(group_data)
        self.load_group_messages()

    def load_group_messages(self, offset=0, limit=50):
        if not self.current_group:
            return
        response = self.api_client.get_group_messages(
            self.current_group["group_id"], self.user_id, limit, offset
        )
        if not response:
            QMessageBox.critical(self.ui, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            self.ui.display_messages(response.get("messages", []), offset, self.username)
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải tin nhắn"))

    def create_new_group(self):
        group_name, ok = QInputDialog.getText(self.ui, "Tạo nhóm mới", "Tên nhóm:")
        if not ok or not group_name.strip():
            return
        response = self.api_client.create_group(group_name.strip(), self.user_id)
        if response and response.get("success"):
            QMessageBox.information(self.ui, "Thành công", f"Đã tạo nhóm '{group_name}' thành công!")
            self.load_user_groups()
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tạo nhóm"))

    def add_member(self):
        if not self.current_group:
            return
        response = self.api_client.get_friends(self.user_id)
        friends = response.get("friends", []) if response and response.get("success") else []
        if not friends:
            QMessageBox.warning(self.ui, "Lỗi", "Không có bạn bè để thêm")
            return
        friend_names = [f"{f['username']} (ID: {f['user_id']})" for f in friends]
        selected, ok = QInputDialog.getItem(self.ui, "Thêm thành viên", "Chọn bạn để thêm:", friend_names, 0, False)
        if not ok or not selected:
            return
        match = re.search(r'ID: (\d+)', selected)
        if not match:
            return
        add_user_id = int(match.group(1))
        response = self.api_client.add_member_to_group(
            self.current_group["group_id"], add_user_id, self.user_id
        )
        if response and response.get("success"):
            QMessageBox.information(self.ui, "Thành công", "Đã thêm thành viên thành công!")
            self.view_members()
        else:
            QMessageBox.critical(self.ui, "Lỗi", response.get("message", "Không thể thêm thành viên"))

    def view_members(self):
        if not self.current_group:
            return
        response = self.api_client.get_group_members(self.current_group["group_id"], self.user_id)
        if response and response.get("success"):
            members_text = "Thành viên nhóm:\n\n"
            for m in response.get("members", []):
                members_text += f"• {m['username']} (ID: {m['user_id']})\n"
            QMessageBox.information(self.ui, f"Thành viên nhóm {self.current_group['group_name']}", members_text)
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải danh sách thành viên"))

    