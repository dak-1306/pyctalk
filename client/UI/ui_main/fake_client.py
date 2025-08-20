class FakeClient:
    """Fake client for testing purposes"""
    def __init__(self, username="TestUser"):
        self._username = username
        self._user_id = 12345
        self._logged_in = True
    def is_logged_in(self) -> bool:
        return self._logged_in
    def get_user_id(self) -> int:
        return self._user_id
    def get_username(self) -> str:
        return self._username
    def set_logged_in(self, status: bool):
        self._logged_in = status
