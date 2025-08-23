import asyncio
class Chat1v1Logic:
    """Logic xử lý tin nhắn, kết nối API với UI"""
    def __init__(self, ui_window, api_client, current_user_id, friend_id):
        self.ui = ui_window
        self.api = api_client
        self.current_user_id = current_user_id
        self.friend_id = friend_id

        # kết nối signal UI → logic
        self.ui.message_send_requested.connect(
            lambda msg: asyncio.create_task(self.send_message(msg))
        )

    async def load_message_history(self):
        try:
            print(f"[DEBUG][Chat1v1Logic] Gọi get_chat_history với user_id={self.current_user_id}, friend_id={self.friend_id}")
            resp = await self.api.get_chat_history(self.current_user_id, self.friend_id)
            print(f"[DEBUG][Chat1v1Logic] Response lịch sử: {resp}")
            # Phản hồi server có thể là resp['data']['messages']
            messages = []
            if resp:
                if 'messages' in resp:
                    messages = resp['messages']
                elif 'data' in resp and 'messages' in resp['data']:
                    messages = resp['data']['messages']
            self.ui.clear_messages()
            for m in messages:
                sender_id = int(m.get("from"))
                content = m.get("message", "")
                timestamp = m.get("timestamp", None)
                print(f"[DEBUG][Chat1v1Logic] Thêm message: sender_id={sender_id}, content={content}, timestamp={timestamp}")
                self.ui.add_message(content, sender_id == self.current_user_id, timestamp)
        except Exception as e:
            print("[ERROR] load_message_history:", e)

    async def send_message(self, text):
        try:
            resp = await self.api.send_message(self.current_user_id, self.friend_id, text)
            if resp and resp.get("success"):
                # Nếu server trả về timestamp thì lấy, không thì None
                timestamp = None
                if 'data' in resp and 'timestamp' in resp['data']:
                    timestamp = resp['data']['timestamp']
                self.ui.add_message(text, True, timestamp)
        except Exception as e:
            print("[ERROR] send_message:", e)

    def on_receive_message(self, data):
        """callback khi server push tin nhắn"""
        sender = int(data.get("from"))
        message = data.get("message", "")
        timestamp = data.get("timestamp", None)
        if sender == self.friend_id:
            self.ui.add_message(message, False, timestamp)
