from PyQt6.QtWidgets import QMessageBox


class LogoutHandler:
    def __init__(self, client, main_window):
        self.client = client  # Đối tượng client socket
        self.main_window = main_window  # Tham chiếu tới cửa sổ chính để chuyển màn hình

    def logout(self, username):
        try:
            self.client.stop_ping()
            request = {
                "action": "logout",
                "data": {"username": username}
            }
            response = self.client.send_json(request)
            self.client.disconnect()
            self.main_window.close()
            from main import LoginWindow
            self.main_window = LoginWindow()
            self.main_window.show()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi đăng xuất: {e}")

