import asyncio
import json


class Chat1v1Client:
    """
    Async Client xử lý logic gửi/nhận tin nhắn 1-1 real-time qua socket
    """
    def __init__(self, pyctalk_client, on_receive_callback=None):
        self.client = pyctalk_client  # Instance của PycTalkClient (phải async)
        self.on_receive_callback = on_receive_callback  # Callback khi nhận tin nhắn mới

    async def send_message(self, to_username, message_text: str, callback=None):
        """Gửi tin nhắn 1-1 tới server, truyền callback nhận phản hồi"""
        if not self.client.is_logged_in():
            print("⚠️ Bạn cần đăng nhập để gửi tin nhắn.")
            return None

        request = {
            "action": "send_message",
            "data": {
                "from": await self.client.get_username(),
                "to": to_username,
                "message": message_text
            }
        }
        await self.client.send_json(request, callback)

    # Không còn listen_loop riêng, mọi nhận tin nhắn sẽ qua callback của AsyncPycTalkClient
