import sys
import asyncio
import qasync
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from UI.ui_main.ui_main_window import Ui_MainWindow
from UI.loginUI_large import Ui_LoginWindow
from UI.signinUI_large import Ui_SignInWindow
from Request.handle_request_client import AsyncPycTalkClient


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.client = AsyncPycTalkClient()

        # Kết nối nút login (async)
        self.ui.btnLogin.clicked.connect(lambda: asyncio.create_task(self.handle_login()))

        # Cho nhãn "Create an Account?" thành clickable
        self.ui.creatAccount.setText('<a href="#">Create an Account?</a>')
        self.ui.creatAccount.setOpenExternalLinks(False)
        self.ui.creatAccount.linkActivated.connect(self.open_register_window)
    
    async def handle_login(self):
        username = self.ui.txtUsername.text()
        password = self.ui.txtPassword.text()

        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ username và password")
            return

        if self.client.running:
            await self.client.disconnect()

        if not await self.client.connect():
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến server")
            return

        request = {
            "action": "login",
            "data": {"username": username, "password": password}
        }

        async def login_callback(response):
            if response and response.get("success"):
                print("✅ Đăng nhập thành công.")
                self.client.user_id = response.get("user_id")
                self.client.username = username
                self.client.start_ping()
                self.goto_main_window()
            else:
                await self.client.disconnect()
                QMessageBox.warning(self, "Thất bại", "Tên đăng nhập hoặc mật khẩu không đúng")

        await self.client.send_json(request, login_callback)

    def goto_main_window(self):
        self.main_window = MainClientWindow(self.client)
        self.main_window.show()
        self.hide()

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
