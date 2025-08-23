class Chat1v1APIClient:
    """API Client cho chat 1-1, gửi request tới server để lấy/gửi dữ liệu"""
    def __init__(self, connection):
        self.connection = connection  # connection phải hỗ trợ async send_json

    async def get_chat_history(self, user_id, friend_id, limit=50):
        return await self.connection.send_json({
            "action": "get_chat_history",
            "data": {
                "user_id": user_id,
                "friend_id": friend_id,
                "limit": limit
            }
        })

    async def send_message(self, sender_id, receiver_id, content):
        return await self.connection.send_json({
            "action": "send_message",
            "data": {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": content
            }
        })

    # Có thể bổ sung thêm các hàm khác như lấy danh sách bạn bè, xóa tin nhắn, ...
