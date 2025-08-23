class Chat1v1Client:
    """Kết nối giữa UI, Logic và APIClient"""
    def __init__(self, chat_window, pyctalk_client, current_user_id, friend_id):
        from .chat1v1_api_client import Chat1v1APIClient
        from .chat1v1_logic import Chat1v1Logic

        self.api_client = Chat1v1APIClient(pyctalk_client)
        self.logic = Chat1v1Logic(chat_window, self.api_client, current_user_id, friend_id)
        import asyncio
        asyncio.create_task(self.logic.load_message_history())

    def handle_incoming_message(self, data):
        """nhận tin nhắn từ socket → đưa vào logic"""
        self.logic.on_receive_message(data)
