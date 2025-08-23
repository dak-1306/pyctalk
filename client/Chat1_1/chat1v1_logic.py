import asyncio

class Chat1v1Logic:
    """Async logic cho ChatWindow 1-1, tách khỏi UI giống group chat"""
    def __init__(self, ui, api_client, user_id, friend_id):
        self.ui = ui
        self.api_client = api_client
        self.user_id = user_id
        self.friend_id = friend_id

    async def load_message_history(self, limit=50):
        response = await self.api_client.get_chat_history(self.user_id, self.friend_id, limit)
        if not response:
            self.ui.load_message_history([])
            return
        if response.get("success"):
            messages = response.get("data", {}).get("messages", [])
            self.ui.load_message_history(messages)
        else:
            self.ui.load_message_history([])

    async def send_message(self, content):
        response = await self.api_client.send_message(self.user_id, self.friend_id, content)
        return response
