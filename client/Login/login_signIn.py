import sys
import asyncio
import qasync
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from client.UI.ui_main.ui_main_window import Ui_MainWindow
from client.UI.loginUI_large import Ui_LoginWindow
from client.UI.signinUI_large import Ui_SignInWindow
from client.Request.handle_request_client import AsyncPycTalkClient


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.client = AsyncPycTalkClient()

        # Kết nối nút login (async)
        self.ui.btnLogin.clicked.connect(lambda: asyncio.create_task(self.handle_login()))

    # Không cần creatAccount nữa, đã có link đăng ký ở giao diện mới
    
    async def handle_login(self):
        username = self.ui.txtUsername.text()
        password = self.ui.txtPassword.text()

        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ username và password")
            return



        if not await self.client.connect():
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến server")
            return

        request = {
            "action": "login",
            "data": {"username": username, "password": password}
        }

        async def login_callback(response):
            print(f"[DEBUG] Callback đăng nhập được gọi với response: {response}")
            if response and response.get("success"):
                print("✅ Đăng nhập thành công.")
                self.client.user_id = response.get("user_id")
                self.client.username = username
                self.client.start_ping()
                print("[DEBUG] Gọi goto_main_window()")
                self.goto_main_window()
            else:
                print("[DEBUG] Đăng nhập thất bại hoặc không có response thành công")
                await self.client.disconnect()
                QMessageBox.warning(self, "Thất bại", "Tên đăng nhập hoặc mật khẩu không đúng")

        await self.client.send_json(request, login_callback)

    def goto_main_window(self):
        print("[DEBUG] Bắt đầu chuyển sang MainClientWindow")
        try:
            self.main_window = MainClientWindow(self.client)
            print("[DEBUG] MainClientWindow khởi tạo thành công")
            self.main_window.show()
            self.hide()
        except Exception as e:
            print(f"[ERROR] Lỗi khi chuyển sang MainClientWindow: {e}")
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Không thể vào giao diện chính: {e}")

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()
        

class RegisterWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SignInWindow()
        self.ui.setupUi(self)
        self.client = AsyncPycTalkClient()

        self.ui.btnSignin.clicked.connect(lambda: asyncio.create_task(self.handle_register()))
        self.ui.backToLogin.clicked.connect(self.back_to_login_clicked)

    async def handle_register(self):
        username = self.ui.txtUsernameSignin.text()
        password = self.ui.txtPasswordSignin.text()
        confirm_password = self.ui.txtConfirmPassword.text()
        email = self.ui.txtEmail.text()

        if not username or not password or not confirm_password or not email:
            QtWidgets.QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ tất cả thông tin.")
            return
        
        if len(username) < 3:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Username phải có ít nhất 3 ký tự.")
            return
        
        if len(password) < 6:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự.")
            return
        
        if password != confirm_password:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp.")
            return
        
        if "@" not in email or "." not in email:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Email không hợp lệ.")
            return

        if not await self.client.connect():
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến server")
            return

        request = {
            "action": "register",
            "data": {
                "username": username,
                "password": password,
                "email": email
            }
        }
        await self.client.send_json(request)

        async def register_callback(response):
            if response and response.get("success"):
                print("✅ Đăng ký thành công.")
                QtWidgets.QMessageBox.information(self, "Thành công", "Đăng ký tài khoản thành công!")
                self.login_window = LoginWindow()
                self.login_window.show()
                self.close()
            else:
                await self.client.disconnect()
                error_message = response.get("message", "Đăng ký thất bại") if response else "Không nhận được phản hồi từ server"
                QMessageBox.warning(self, "Thất bại", error_message)

        asyncio.create_task(self.client.listen_loop(register_callback))
            
    def back_to_login_clicked(self):
        self.open_login_window()
            
    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


class MainClientWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.ui = Ui_MainWindow(client.username, client, self)
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    login_window = LoginWindow()
    login_window.show()

    with loop:
        loop.run_forever()
