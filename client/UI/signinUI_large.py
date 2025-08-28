# Modern Signup UI for PycTalk - Larger Size
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_SignInWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(500, 700)  # Kích thước lớn hơn
        MainWindow.setMaximumSize(500, 700)
        MainWindow.resize(500, 700)
        MainWindow.setWindowTitle("PycTalk - Create Account")
        
        self.MainWindow = MainWindow
        
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # Main background - match login UI
        self.centralwidget.setStyleSheet("""
            background: #1e2a38;
        """)

        # Main layout - center form like login UI
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(350)
        self.formLayout = QtWidgets.QVBoxLayout(self.widget)
        self.formLayout.setContentsMargins(30, 30, 30, 30)
        self.formLayout.setSpacing(18)

        # Title
        self.titleLabel = QtWidgets.QLabel("Create Account")
        font = QtGui.QFont("Fredoka One", 26, QtGui.QFont.Weight.Bold)
        self.titleLabel.setFont(font)
        self.titleLabel.setStyleSheet("color: #a05a00; letter-spacing: 1px;")
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.formLayout.addWidget(self.titleLabel)

        # Username field
        self.txtUsernameSignin = QtWidgets.QLineEdit()
        self.txtUsernameSignin.setPlaceholderText("Username")
        self.txtUsernameSignin.setStyleSheet("""
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
        self.txtUsernameSignin.setObjectName("txtUsernameSignin")
        self.formLayout.addWidget(self.txtUsernameSignin)

        # Email field
        self.txtEmail = QtWidgets.QLineEdit()
        self.txtEmail.setPlaceholderText("Email Address")
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
        self.txtEmail.setObjectName("txtEmail")
        self.formLayout.addWidget(self.txtEmail)

        # Password field
        self.txtPasswordSignin = QtWidgets.QLineEdit()
        self.txtPasswordSignin.setPlaceholderText("Password")
        self.txtPasswordSignin.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPasswordSignin.setStyleSheet("""
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
        self.txtPasswordSignin.setObjectName("txtPasswordSignin")
        self.formLayout.addWidget(self.txtPasswordSignin)

        # Confirm Password field
        self.txtConfirmPassword = QtWidgets.QLineEdit()
        self.txtConfirmPassword.setPlaceholderText("Confirm Password")
        self.txtConfirmPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtConfirmPassword.setStyleSheet("""
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
        self.txtConfirmPassword.setObjectName("txtConfirmPassword")
        self.formLayout.addWidget(self.txtConfirmPassword)

        # Sign Up button - match login UI
        self.btnSignin = QtWidgets.QPushButton("CREATE ACCOUNT")
        btnFont = QtGui.QFont("Fredoka One", 16, QtGui.QFont.Weight.Bold)
        self.btnSignin.setFont(btnFont)
        self.btnSignin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnSignin.setStyleSheet("""
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
        self.btnSignin.setObjectName("btnSignin")
        self.formLayout.addWidget(self.btnSignin)

        # Back to login link (like login UI register link)
        self.backToLoginLayout = QtWidgets.QHBoxLayout()
        self.backToLoginLayout.setContentsMargins(0, 0, 0, 0)
        self.backToLoginLayout.setSpacing(4)
        self.lblHaveAccount = QtWidgets.QLabel("Đã có tài khoản?")
        self.lblHaveAccount.setStyleSheet("font-size: 15px; color: #7a5a1e;")
        self.lblBackToLogin = QtWidgets.QLabel('<a href="#" style="color:#ff9800; font-weight:bold; text-decoration:none;">Đăng nhập ngay</a>')
        self.lblBackToLogin.setStyleSheet("font-size: 15px; color:#3fc1c9; font-weight:bold; text-decoration:none;")
        self.lblBackToLogin.setOpenExternalLinks(False)
        self.backToLoginLayout.addWidget(self.lblHaveAccount)
        self.backToLoginLayout.addWidget(self.lblBackToLogin)
        self.formLayout.addLayout(self.backToLoginLayout)
        self.mainLayout.addWidget(self.widget, 0, QtCore.Qt.AlignmentFlag.AlignCenter)

        # Connect the login link to a callback if set
        self.lblBackToLogin.linkActivated.connect(self.on_login_clicked)

    def on_login_clicked(self, link):
        # Call a callback if set (to be set by the main window logic)
        if hasattr(self, 'login_callback') and callable(self.login_callback):
            self.login_callback()
        
    # Remove all old geometry-based widgets and duplicate fields/buttons

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PycTalk - Create Account"))
        self.titleLabel.setText(_translate("MainWindow", "Create Account"))
        self.txtUsernameSignin.setPlaceholderText(_translate("MainWindow", "Username"))
        self.txtEmail.setPlaceholderText(_translate("MainWindow", "Email Address"))
        self.txtPasswordSignin.setPlaceholderText(_translate("MainWindow", "Password"))
        self.txtConfirmPassword.setPlaceholderText(_translate("MainWindow", "Confirm Password"))
        self.btnSignin.setText(_translate("MainWindow", "CREATE ACCOUNT"))
        self.lblHaveAccount.setText(_translate("MainWindow", "Đã có tài khoản?"))
        self.lblBackToLogin.setText(_translate("MainWindow", '<a href="#" style="color:#ff9800; font-weight:bold; text-decoration:none;">Đăng nhập ngay</a>'))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_SignInWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
