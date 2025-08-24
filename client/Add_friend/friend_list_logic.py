from Add_friend.friend import FriendClient

class FriendListLogic:
    """
    Logic tách biệt cho FriendListWindow: gọi API, xử lý dữ liệu bạn bè, truyền về UI
    """
    def __init__(self, client, username, user_id):
        self.client = client
        self.username = username
        self.user_id = user_id
        self.friend_client = FriendClient(self.client)

    async def get_conversations(self):
        """Lấy danh sách bạn bè từ server, trả về list dict cho UI (chuẩn async, không bị trả về rỗng do callback)"""
        import asyncio
        future = asyncio.get_event_loop().create_future()

        async def friends_callback(response):
            conversations = []
            friends = response.get("data", []) if response and isinstance(response, dict) and response.get("success") else []
            for friend in friends:
                if isinstance(friend, dict):
                    friend_id = friend.get('id') or friend.get('friend_id')
                    friend_display_name = friend.get('name') or friend.get('friend_name') or str(friend_id)
                else:
                    continue
                if not friend_id:
                    continue
                conversations.append({
                    'friend_id': friend_id,
                    'friend_name': friend_display_name,
                    'last_message': '',
                    'last_message_time': '',
                    'unread_count': 0
                })
            future.set_result(conversations)

        await self.friend_client.get_friends(friends_callback)
        conversations = await future
        return conversations
