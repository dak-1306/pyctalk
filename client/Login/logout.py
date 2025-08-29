from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer
import asyncio


class LogoutHandler:
    def __init__(self, client, main_window):
        self.client = client  # Đối tượng client socket (hỗ trợ async)
        self.main_window = main_window  # Tham chiếu tới cửa sổ chính để chuyển màn hình
        self.login_window = None  # Keep reference to prevent garbage collection

    async def logout(self, username: str):
        try:
            print(f"[DEBUG][LogoutHandler] Starting logout for user: {username}")
            
            # Ngừng ping
            if hasattr(self.client, "stop_ping"):
                try:
                    self.client.stop_ping()
                    print(f"[DEBUG][LogoutHandler] Stopped ping")
                except Exception as e:
                    print(f"[DEBUG][LogoutHandler] Error stopping ping: {e}")

            # Clear client session data locally
            if hasattr(self.client, 'user_id'):
                self.client.user_id = None
            if hasattr(self.client, 'username'):
                self.client.username = None
            print(f"[DEBUG][LogoutHandler] Cleared local session data")

            # Gửi switch_user request để logout nhưng giữ connection
            try:
                request = {
                    "action": "switch_user",  # Use switch_user instead of logout
                    "data": {"username": username}
                }
                
                async def switch_user_callback(response):
                    print(f"[DEBUG] Switch user response: {response}")
                
                # Đợi response từ server với timeout dài hơn
                await asyncio.wait_for(
                    self.client.send_json(request, switch_user_callback),
                    timeout=10.0
                )
                print(f"[DEBUG][LogoutHandler] Switch user request sent and response received")
            except asyncio.TimeoutError:
                print(f"[DEBUG][LogoutHandler] Switch user request timeout - server may not be responding")
            except Exception as e:
                print(f"[DEBUG][LogoutHandler] Error sending switch user request: {e}")

            # Chuyển về màn hình đăng nhập - giữ connection alive
            print(f"[DEBUG][LogoutHandler] Switching to login window with connection preserved")
            self._show_login_window()

            return {"success": True, "message": "Đăng xuất thành công"}
        except Exception as e:
            print(f"[ERROR][LogoutHandler] Lỗi khi đăng xuất: {e}")
            # Vẫn chuyển về login window
            self._show_login_window()
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi đăng xuất: {e}")
            return {"success": False, "message": str(e)}
    
    def _show_login_window(self):
        """Chuyển về trang đăng nhập trong cùng ứng dụng"""
        try:
            print(f"[DEBUG][LogoutHandler] Switching to login window...")
            
            # Import ở đây để tránh circular import
            import sys
            import os
            from PyQt6.QtWidgets import QApplication
            
            # Get current QApplication instance
            app = QApplication.instance()
            if not app:
                print(f"[ERROR][LogoutHandler] No QApplication instance found")
                return
            
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from Login.login_signIn import LoginWindow
            
            # Đóng main window trước
            if self.main_window:
                self.main_window.hide()  # Hide instead of close to keep app running
                print(f"[DEBUG][LogoutHandler] Main window hidden")
            
            # Use QTimer to delay the window creation slightly
            def create_login_window():
                try:
                    # Tạo login window mới và hiển thị, pass existing client
                    self.login_window = LoginWindow(existing_client=self.client)
                    self.login_window.show()
                    print(f"[DEBUG][LogoutHandler] Login window created and shown with existing client")
                except Exception as e:
                    print(f"[ERROR][LogoutHandler] Error creating login window: {e}")
            
            # Delay creating new window slightly
            QTimer.singleShot(100, create_login_window)
            
        except Exception as e:
            print(f"[ERROR][LogoutHandler] Không thể chuyển về trang đăng nhập: {e}")
            QMessageBox.critical(None, "Lỗi", f"Không thể chuyển về trang đăng nhập: {e}")
