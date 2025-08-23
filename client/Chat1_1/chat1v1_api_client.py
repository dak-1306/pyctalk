class Chat1v1APIClient:
    """API client cho chat 1-1 (gọi server qua pyctalk_client)"""
    def __init__(self, pyctalk_client):
        self.client = pyctalk_client

    async def get_chat_history(self, user_id, friend_id, limit=50):
        return await self.client.send_request("get_chat_history", {
            "user_id": user_id,
            "friend_id": friend_id,
            "limit": limit
        })

    async def send_message(self, user_id, friend_id, content):
        return await self.client.send_request("send_message", {
            "from": user_id,
            "to": friend_id,
            "message": content
        })
