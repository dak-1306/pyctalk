from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QListWidgetItem
from PyQt6 import QtCore
import re
import asyncio


class GroupChatLogic:
    """Async logic cho GroupChatWindow (toàn bộ xử lý đã gom về đây)"""

    def __init__(self, ui, api_client, user_id, username):
        self.ui = ui
        self.api_client = api_client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.message_offset = 0

        # Kết nối tín hiệu từ UI
        self.ui.group_selected.connect(self.handle_group_selected)
        self.ui.message_send_requested.connect(self.send_message)

    # ---------------------------
    # Load danh sách nhóm
    # ---------------------------
    async def load_user_groups(self):
        print("[GroupChatLogic] Đang tải danh sách nhóm...")
        response = await self.api_client.get_user_groups(self.user_id)
        if not response:
            QMessageBox.critical(self.ui, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            self.ui.groups_list.clear()
            for idx, group in enumerate(response.get("groups", [])):
                try:
                    item_text = f"{group['group_name']} (ID: {group['group_id']})"
                    item = QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, group)
                    self.ui.groups_list.addItem(item)
                except Exception as e:
                    print(f"[GroupChatLogic][ERROR] Lỗi khi tạo item cho group #{idx}: {e}")
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải danh sách nhóm"))

    # ---------------------------
    # Chọn nhóm
    # ---------------------------
    async def handle_group_selected(self, item):
        """Xử lý khi UI chọn 1 nhóm"""
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        print(f"[GroupChatLogic] Chuyển sang nhóm: {group_data.get('group_name')} (ID: {group_data.get('group_id')})")
        await self.select_group(group_data)

    async def select_group(self, group_data):
        self.current_group = group_data
        self.message_offset = 0
        self.ui.update_group_info(group_data)
        await self.load_group_messages()

    # ---------------------------
    # Tải tin nhắn nhóm
    # ---------------------------
    async def load_group_messages(self, offset=0, limit=50):
        if not self.current_group:
            print("[GroupChatLogic] current_group is None, abort load_group_messages")
            return
        response = await self.api_client.get_group_messages(
            self.current_group["group_id"], self.user_id, limit, offset
        )
        if not response:
            QMessageBox.critical(self.ui, "Lỗi", "Không nhận được phản hồi từ server!")
            return
        if response.get("success"):
            messages = response.get("messages", [])
            self.display_messages(messages, offset, self.username)
        else:
            print(f"[GroupChatLogic][ERROR] Không thể tải tin nhắn: {response.get('message')}")
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải tin nhắn"))

    # ---------------------------
    # Hiển thị tin nhắn
    # ---------------------------
    def display_messages(self, messages, offset, username):
        if offset == 0:
            self.ui.clear_messages()
        for msg in messages:
            sender = msg.get('sender_name', 'Unknown')
            time_str = msg.get("time_send", "Unknown")
            content = msg.get('content', '')
            is_sent = sender == username
            self.ui.add_message(content, is_sent, time_str)

    # ---------------------------
    # Gửi tin nhắn
    # ---------------------------
    async def send_message(self, content: str):
        if not self.current_group:
            QMessageBox.warning(self.ui, "Lỗi", "Vui lòng chọn nhóm trước")
            return
        if not content.strip():
            return

        response = await self.api_client.send_group_message(
            self.user_id, self.current_group["group_id"], content.strip()
        )
        if response and response.get("success"):
            await self.load_group_messages(offset=0)
        else:
            QMessageBox.warning(self.ui, "Lỗi", "Không thể gửi tin nhắn")

    # ---------------------------
    # Quản lý nhóm
    # ---------------------------
    async def create_new_group(self):
        group_name, ok = QInputDialog.getText(self.ui, "Tạo nhóm mới", "Tên nhóm:")
        if not ok or not group_name.strip():
            return
        response = await self.api_client.create_group(group_name.strip(), self.user_id)
        if response and response.get("success"):
            QMessageBox.information(self.ui, "Thành công", f"Đã tạo nhóm '{group_name}' thành công!")
            await self.load_user_groups()
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tạo nhóm"))

    async def add_member(self):
        if not self.current_group:
            return
        response = await self.api_client.get_friends(self.user_id)
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

        response = await self.api_client.add_member_to_group(
            self.current_group["group_id"], add_user_id, self.user_id
        )
        if response and response.get("success"):
            QMessageBox.information(self.ui, "Thành công", "Đã thêm thành viên thành công!")
            await self.view_members()
        else:
            QMessageBox.critical(self.ui, "Lỗi", response.get("message", "Không thể thêm thành viên"))

    async def view_members(self):
        if not self.current_group:
            return
        response = await self.api_client.get_group_members(self.current_group["group_id"], self.user_id)
        if response and response.get("success"):
            members_text = "Thành viên nhóm:\n\n"
            for m in response.get("members", []):
                members_text += f"• {m['username']} (ID: {m['user_id']})\n"
            QMessageBox.information(self.ui, f"Thành viên nhóm {self.current_group['group_name']}", members_text)
        else:
            QMessageBox.warning(self.ui, "Lỗi", response.get("message", "Không thể tải danh sách thành viên"))
