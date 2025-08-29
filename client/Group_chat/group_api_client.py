class GroupAPIClient:
    """Async API Client cho các chức năng chat nhóm"""

    def __init__(self, connection):
        self.connection = connection  # connection phải hỗ trợ async send_json

    async def get_user_groups(self, user_id: str):
        return await self._send("get_user_groups", {"user_id": user_id})

    async def create_group(self, group_name: str, user_id: str):
        return await self._send("create_group", {
            "group_name": group_name,
            "user_id": user_id
        })

    async def create_group_with_members(self, group_name: str, user_id: str, member_ids: list):
        return await self._send("create_group_with_members", {
            "group_name": group_name,
            "user_id": user_id,
            "member_ids": member_ids
        })

    async def add_member_to_group(self, group_id: str, user_id: str, admin_id: str):
        return await self._send("add_member_to_group", {
            "group_id": group_id,
            "user_id": user_id,
            "admin_id": admin_id
        })

    async def get_group_members(self, group_id: str, user_id: str):
        return await self._send("get_group_members", {
            "group_id": group_id,
            "user_id": user_id
        })

    async def get_group_messages(self, group_id: str, user_id: str, limit: int = 50, offset: int = 0):
        return await self._send("get_group_messages", {
            "group_id": group_id,
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        })

    async def send_group_message(self, sender_id: str, group_id: str, content: str):
        return await self._send("send_group_message", {
            "sender_id": sender_id,  # Server expects sender_id
            "group_id": group_id,
            "content": content  # Server expects content
        })

    async def send_group_file_message(self, sender_id: str, group_id: str, file_metadata: dict, caption: str = ""):
        """Send file message to group"""
        return await self._send("send_group_file_message", {
            "sender_id": sender_id,
            "group_id": group_id,
            "file_metadata": file_metadata,
            "caption": caption
        })

    async def get_friends(self, user_id: str):
        return await self._send("get_friends", {"user_id": user_id})

    # === Group Management Methods ===
    async def leave_group(self, group_id: str, user_id: str):
        """Rời khỏi nhóm"""
        return await self._send("leave_group", {
            "group_id": group_id,
            "user_id": user_id
        })

    async def transfer_leadership(self, group_id: str, current_admin_id: str, new_admin_id: str):
        """Chuyển quyền trưởng nhóm"""
        return await self._send("transfer_leadership", {
            "group_id": group_id,
            "current_admin_id": current_admin_id,
            "new_admin_id": new_admin_id
        })

    async def remove_member(self, group_id: str, admin_id: str, member_id: str):
        """Admin kick thành viên khỏi nhóm"""
        return await self._send("remove_member", {
            "group_id": group_id,
            "admin_id": admin_id,
            "member_id": member_id
        })

    async def add_friend_to_group(self, group_id: str, friend_id: str, added_by: str):
        """Thêm bạn bè vào nhóm"""
        return await self._send("add_friend_to_group", {
            "group_id": group_id,
            "friend_id": friend_id,
            "added_by": added_by
        })

    async def get_user_friends(self, user_id: str):
        """Lấy danh sách bạn bè của user"""
        return await self._send("get_user_friends", {
            "user_id": user_id
        })

    async def _send(self, action: str, data: dict):
        """Helper async để gửi request"""
        try:
            return await self.connection.send_json({"action": action, "data": data})
        except Exception as e:
            print(f"❌ GroupAPI Error: {e}")
            return None
