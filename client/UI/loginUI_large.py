

# Login UI theo mẫu ảnh
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_LoginWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(700, 450)
        MainWindow.setWindowTitle("Đăng nhập")

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # Main background
        self.centralwidget.setStyleSheet("""
            background: #1e2a38;
        """)

        # Main layout chỉ có form login căn giữa
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Form login
        self.formWidget = QtWidgets.QWidget()
        self.formWidget.setFixedWidth(350)
        self.formLayout = QtWidgets.QVBoxLayout(self.formWidget)
        self.formLayout.setContentsMargins(30, 30, 30, 30)
        self.formLayout.setSpacing(18)

        # Title
        self.titleLabel = QtWidgets.QLabel("Đăng nhập")
        font = QtGui.QFont("Fredoka One", 26, QtGui.QFont.Weight.Bold)
        self.titleLabel.setFont(font)
        self.titleLabel.setStyleSheet("color: #a05a00; letter-spacing: 1px;")
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.formLayout.addWidget(self.titleLabel)

        # Email input (đồng thời gán cho txtUsername để tương thích với code cũ)
        self.txtEmail = QtWidgets.QLineEdit()
        self.txtEmail.setPlaceholderText("Nhập userName...")
        self.txtEmail.setStyleSheet("""
            QLineEdit {
                font-size: 17px;
                border: 2px solid #3fc1c9;
                border-radius: 24px;
                padding: 12px 18px;
                background: #fafdff;
            }
            QLineEdit:focus {
                border: 2.5px solid #364f6b;
            }
        """)
        self.formLayout.addWidget(self.txtEmail)
        self.txtUsername = self.txtEmail  # Thêm dòng này để tương thích với code truy cập txtUsername

        # Password input
        self.txtPassword = QtWidgets.QLineEdit()
        self.txtPassword.setPlaceholderText("Mật khẩu")
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPassword.setStyleSheet("""
            QLineEdit {
                font-size: 17px;
                border: 2px solid #3fc1c9;
                border-radius: 24px;
                padding: 12px 18px;
                background: #fafdff;
            }
            QLineEdit:focus {
                border: 2.5px solid #364f6b;
            }
        """)
        self.formLayout.addWidget(self.txtPassword)

        # Remember me checkbox
        self.chkRemember = QtWidgets.QCheckBox("Ghi nhớ đăng nhập")
        self.chkRemember.setStyleSheet("font-size: 15px; color: #7a5a1e;")
        self.formLayout.addWidget(self.chkRemember)

        # Login button
        self.btnLogin = QtWidgets.QPushButton("Đăng nhập")
        btnFont = QtGui.QFont("Fredoka One", 16, QtGui.QFont.Weight.Bold)
        self.btnLogin.setFont(btnFont)
        self.btnLogin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnLogin.setStyleSheet("""
            QPushButton {
                background: #3fc1c9;
                color: #fff;
                border: none;
                border-radius: 24px;
                padding: 14px 0;
                font-weight: bold;
                font-size: 16px;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: #364f6b;
            }
        """)
        self.formLayout.addWidget(self.btnLogin)

        # Register link
        self.registerLayout = QtWidgets.QHBoxLayout()
        self.registerLayout.setContentsMargins(0, 0, 0, 0)
        self.registerLayout.setSpacing(4)
        self.lblNoAccount = QtWidgets.QLabel("Bạn chưa có tài khoản?")
        self.lblNoAccount.setStyleSheet("font-size: 15px; color: #7a5a1e;")
        self.lblRegister = QtWidgets.QLabel('<a href="#" style="color:#ff9800; font-weight:bold; text-decoration:none;">Đăng kí ngay</a>')
        self.lblRegister.setStyleSheet("font-size: 15px; color:#3fc1c9; font-weight:bold; text-decoration:none;")
        self.lblRegister.setOpenExternalLinks(False)
        # Kết nối sự kiện click cho link đăng ký
        self.lblRegister.linkActivated.connect(self.on_register_clicked)
        self.registerLayout.addWidget(self.lblNoAccount)
        self.registerLayout.addWidget(self.lblRegister)
        self.formLayout.addLayout(self.registerLayout)
        self.mainLayout.addWidget(self.formWidget, 0, QtCore.Qt.AlignmentFlag.AlignCenter)

    def on_register_clicked(self, link):
        # Gọi callback nếu có, hoặc emit signal
        if hasattr(self, 'register_callback') and callable(self.register_callback):
            self.register_callback()

    def retranslateUi(self, MainWindow):
        pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_LoginWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
