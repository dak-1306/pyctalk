class GroupAPIClient:
    """API Client cho các chức năng chat nhóm"""

    def __init__(self, connection):
        self.connection = connection

    def get_user_groups(self, user_id):
        return self._send("get_user_groups", {"user_id": user_id})

    def create_group(self, group_name, user_id):
        return self._send("create_group", {"group_name": group_name, "user_id": user_id})

    def create_group_with_members(self, group_name, user_id, member_ids):
        return self._send("create_group_with_members", {
            "group_name": group_name,
            "user_id": user_id,
            "member_ids": member_ids
        })

    def add_member_to_group(self, group_id, user_id, admin_id):
        return self._send("add_member_to_group", {
            "group_id": group_id,
            "user_id": user_id,
            "admin_id": admin_id
        })

    def get_group_members(self, group_id, user_id):
        return self._send("get_group_members", {"group_id": group_id, "user_id": user_id})

    def get_group_messages(self, group_id, user_id, limit=50, offset=0):
        return self._send("get_group_messages", {
            "group_id": group_id,
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        })

    def send_group_message(self, sender_id, group_id, content):
        return self._send("send_group_message", {
            "sender_id": sender_id,
            "group_id": group_id,
            "content": content
        })

    def get_friends(self, user_id):
        return self._send("get_friends", {"user_id": user_id})

    def _send(self, action, data):
        try:
            return self.connection.send_json({"action": action, "data": data})
        except Exception as e:
            print(f"❌ GroupAPI Error: {e}")
            return None
