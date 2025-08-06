import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from UI.mainClient import Ui_MainWindow  # Đổi 'main_client' thành file .py giao diện bạn tạo từ .ui
from UI.loginUI import Ui_LoginWindow  # Đổi 'login_ui' thành file .py giao diện bạn tạo từ .ui
from UI.signinUI import Ui_SignInWindow  # File giao diện đăng ký
from Request.handle_request_client import PycTalkClient


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.client = PycTalkClient()

        # Kết nối nút login
        self.ui.btnLogin.clicked.connect(self.handle_login)

        # Cho nhãn "Create an Account?" thành clickable
        self.ui.creatAccount.setText('<a href="#">Create an Account?</a>')
        self.ui.creatAccount.setOpenExternalLinks(False)
        self.ui.creatAccount.linkActivated.connect(self.open_register_window)
    
    def handle_login(self):
        username = self.ui.txtUsername.text()
        password = self.ui.txtPassword.text()

        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ username và password")
            return

        # Đảm bảo disconnect trước khi kết nối mới
        if self.client.running:
            self.client.disconnect()
            
        # xử lý login qua hàm connect + send_json
        if not self.client.connect():
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến server")
            return

        request = {
            "action": "login",
            "data": {"username": username, "password": password}
        }

        response = self.client.send_json(request)

        if response and response.get("success"):
            print("✅ Đăng nhập thành công.")
            # Lưu thông tin user
            self.client.user_id = response.get("user_id")
            self.client.username = username
            # Client đã tự động lưu user_id và username
            self.client.start_ping(username)
            self.goto_main_window()
        else:
            self.client.disconnect()
            QMessageBox.warning(self, "Thất bại", "Tên đăng nhập hoặc mật khẩu không đúng")

    def goto_main_window(self):
        self.main_window = MainClientWindow(self.client)
        self.main_window.show()
        self.hide()

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()  # Tùy chọn: đóng cửa sổ đăng nhập
        
class RegisterWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SignInWindow()
        self.ui.setupUi(self)
        self.client = PycTalkClient()

        self.ui.btnSignin.clicked.connect(self.handle_register)
        
        self.ui.backToLogin.setText('<a href="#">Back to Login</a>')
        self.ui.backToLogin.setOpenExternalLinks(False)
        self.ui.backToLogin.linkActivated.connect(self.open_login_window)

    def handle_register(self):
        username = self.ui.txtUsernameSignin.text()
        password = self.ui.txtPasswordSignin.text()
        email = self.ui.txtEmail.text()

        if not username or not password or not email:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        if not self.client.connect():
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

        response = self.client.send_json(request)

        if response and response.get("success"):
            print("✅ Đăng ký thành công.")
            self.login_window = LoginWindow()  # Giữ tham chiếu để không bị huỷ
            self.login_window.show()
            self.close()
        else:
            self.client.disconnect()
            error_message = response.get("message", "Đăng ký thất bại") if response else "Không nhận được phản hồi từ server"
            QMessageBox.warning(self, "Thất bại", error_message)
            
    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

        
        
class MainClientWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.ui = Ui_MainWindow(client.get_username(), client, self)
        self.ui.setupUi(self)