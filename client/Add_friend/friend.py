import json
from Request.handle_request_client import AsyncPycTalkClient


class FriendClient:
    """
    Async Client logic for friend operations: 
    send request, accept, reject, get suggestions, get requests, remove friend
    """
    def __init__(self, pyctalk_client: AsyncPycTalkClient):
        self.client = pyctalk_client

    async def _send_action(self, action: str, data: dict, callback=None, require_login: bool = True):
        """Helper async để gửi request đến server, truyền callback"""
        if require_login and not self.client.is_logged_in():
            print("⚠️ Bạn cần đăng nhập để thực hiện hành động này.")
            return None
        request = {
            "action": action,
            "data": data
        }
        await self.client.send_json(request, callback)

    async def get_friends(self, callback):
        """Lấy danh sách bạn bè, truyền callback"""
        await self._send_action("get_friends", {"username": await self.client.get_username()}, callback)

    async def send_friend_request(self, to_username: str, callback):
        """Gửi yêu cầu kết bạn, truyền callback"""
        await self._send_action("add_friend", {
            "from_user": await self.client.get_username(),
            "to_user": to_username
        }, callback)

    async def get_friend_suggestions(self, callback):
        """Lấy danh sách gợi ý kết bạn, truyền callback"""
        await self._send_action("get_suggestions", {
            "username": await self.client.get_username()
        }, callback)

    async def get_friend_requests(self, callback):
        """Lấy danh sách lời mời kết bạn, truyền callback"""
        await self._send_action("get_friend_requests", {
            "username": await self.client.get_username()
        }, callback)

    async def accept_friend(self, from_username: str, callback):
        """Chấp nhận lời mời kết bạn, truyền callback"""
        await self._send_action("accept_friend", {
            "username": await self.client.get_username(),
            "from_user": from_username
        }, callback)

    async def reject_friend(self, from_username: str, callback):
        """Từ chối lời mời kết bạn, truyền callback"""
        await self._send_action("reject_friend", {
            "username": await self.client.get_username(),
            "from_user": from_username
        }, callback)

    async def remove_friend(self, friend_username: str, callback):
        """Xóa bạn khỏi danh sách, truyền callback"""
        await self._send_action("remove_friend", {
            "username": await self.client.get_username(),
            "friend_name": friend_username
        }, callback)
