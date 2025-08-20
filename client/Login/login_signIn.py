import sys
sys.path.append('./client')
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from UI.ui_main.ui_main_window import Ui_MainWindow  # Đổi 'main_client' thành file .py giao diện bạn tạo từ .ui
from UI.loginUI_large import Ui_LoginWindow  # File giao diện đăng nhập lớn
from UI.signinUI_large import Ui_SignInWindow  # File giao diện đăng ký lớn
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
        
        # Xử lý nút "Back to Login" - bây giờ là QPushButton
        self.ui.backToLogin.clicked.connect(self.back_to_login_clicked)

    def handle_register(self):
        username = self.ui.txtUsernameSignin.text()
        password = self.ui.txtPasswordSignin.text()
        confirm_password = self.ui.txtConfirmPassword.text()
        email = self.ui.txtEmail.text()

        # Validation
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
        
        # Simple email validation
        if "@" not in email or "." not in email:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Email không hợp lệ.")
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
            QtWidgets.QMessageBox.information(self, "Thành công", "Đăng ký tài khoản thành công!")
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
        else:
            self.client.disconnect()
            error_message = response.get("message", "Đăng ký thất bại") if response else "Không nhận được phản hồi từ server"
            QMessageBox.warning(self, "Thất bại", error_message)
            
    def back_to_login_clicked(self):
        """Xử lý khi click vào Back to Login"""
        self.open_login_window()
            
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())