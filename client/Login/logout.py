from PyQt6.QtWidgets import QMessageBox


class LogoutHandler:
    def __init__(self, client, main_window):
        self.client = client  # Đối tượng client socket (hỗ trợ async)
        self.main_window = main_window  # Tham chiếu tới cửa sổ chính để chuyển màn hình

    async def logout(self, username: str):
        try:
            # Ngừng ping (nếu client hỗ trợ async)
            if hasattr(self.client, "stop_ping"):
                await self.client.stop_ping()

            request = {
                "action": "logout",
                "data": {"username": username}
            }

            # Gửi yêu cầu logout (giả định client.send_json là async)
            response = await self.client.send_json(request)

            # Ngắt kết nối
            if hasattr(self.client, "disconnect"):
                await self.client.disconnect()

            # Đóng cửa sổ chính
            self.main_window.close()

            # Chuyển về màn hình đăng nhập
            from main import LoginWindow
            self.main_window = LoginWindow()
            self.main_window.show()

            return response
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi đăng xuất: {e}")
            return {"success": False, "message": str(e)}
