import json
from Request.handle_request_client import PycTalkClient

class FriendClient:
    def get_friends(self):
        """Lấy danh sách bạn bè từ server"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để xem danh sách bạn bè.")
            return None
        request = {
            "action": "get_friends",
            "data": {
                "username": self.client.get_username()
            }
        }
        return self.client.send_json(request)
    """
    Client logic for friend operations: send request, accept, reject, get suggestions, get requests
    """
    def __init__(self, pyctalk_client: PycTalkClient):
        self.client = pyctalk_client

    def send_friend_request(self, to_username):
        """Gửi yêu cầu kết bạn tới user khác"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để gửi kết bạn.")
            return None
        request = {
            "action": "add_friend",
            "data": {
                "from_user": self.client.get_username(),
                "to_user": to_username
            }
        }
        return self.client.send_json(request)

    def get_friend_suggestions(self):
        """Lấy danh sách gợi ý kết bạn từ server"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để xem gợi ý kết bạn.")
            return None
        request = {
            "action": "get_suggestions",
            "data": {
                "username": self.client.get_username()
            }
        }
        return self.client.send_json(request)

    def get_friend_requests(self):
        """Lấy danh sách lời mời kết bạn đang chờ"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để xem lời mời kết bạn.")
            return None
        request = {
            "action": "get_friend_requests",
            "data": {
                "username": self.client.get_username()
            }
        }
        return self.client.send_json(request)

    def accept_friend(self, from_username):
        """Chấp nhận lời mời kết bạn từ user khác"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để chấp nhận kết bạn.")
            return None
        request = {
            "action": "accept_friend",
            "data": {
                "username": self.client.get_username(),
                "from_user": from_username
            }
        }
        return self.client.send_json(request)

    def reject_friend(self, from_username):
        """Từ chối lời mời kết bạn từ user khác"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để từ chối kết bạn.")
            return None
        request = {
            "action": "reject_friend",
            "data": {
                "username": self.client.get_username(),
                "from_user": from_username
            }
        }
        return self.client.send_json(request)

    def remove_friend(self, friend_username):
        """Xóa bạn khỏi danh sách bạn bè"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để xóa bạn.")
            return None
        request = {
            "action": "remove_friend",
            "data": {
                "username": self.client.get_username(),
                "friend_name": friend_username
            }
        }
        return self.client.send_json(request)
