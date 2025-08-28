from PyQt6.QtWidgets import QMessageBox


class LogoutHandler:
    def __init__(self, client, main_window):
        self.client = client  # Đối tượng client socket (hỗ trợ async)
        self.main_window = main_window  # Tham chiếu tới cửa sổ chính để chuyển màn hình

    async def logout(self, username: str):
        try:
            # Ngừng ping (method này là sync, không cần await)
            if hasattr(self.client, "stop_ping"):
                self.client.stop_ping()

            request = {
                "action": "logout",
                "data": {"username": username}
            }

            # Gửi yêu cầu logout với callback
            async def logout_callback(response):
                print(f"[DEBUG] Logout response: {response}")
                # Callback sẽ được gọi khi có response, nhưng chúng ta không cần đợi
                pass

            try:
                await self.client.send_json(request, logout_callback)
            except Exception as e:
                print(f"[DEBUG] Lỗi khi gửi logout request: {e}")

            # Ngắt kết nối
            if hasattr(self.client, "disconnect"):
                await self.client.disconnect()

            # Chuyển về màn hình đăng nhập
            self._show_login_window()

            return {"success": True, "message": "Đăng xuất thành công"}
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi đăng xuất: {e}")
            return {"success": False, "message": str(e)}
    
    def _show_login_window(self):
        """Chuyển về trang đăng nhập"""
        try:
            # Import ở đây để tránh circular import
            from client.Login.login_signIn import LoginWindow
            
            # Đóng cửa sổ chính
            self.main_window.close()
            
            # Tạo và hiện trang đăng nhập
            login_window = LoginWindow()
            login_window.show()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Không thể chuyển về trang đăng nhập: {e}")
