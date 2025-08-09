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
        
        # Main container - kích thước lớn
        self.widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(25, 25, 450, 650))
        self.widget.setObjectName("widget")
        
        # Background với gradient đẹp
        self.background = QtWidgets.QLabel(parent=self.widget)
        self.background.setGeometry(QtCore.QRect(0, 0, 450, 650))
        self.background.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #b2ebf2, stop:1 #e0f7fa);
            border-radius: 25px;
        """)
        self.background.setText("")
        self.background.setObjectName("background")
        
        # Title - font lớn
        self.titleLabel = QtWidgets.QLabel(parent=self.widget)
        self.titleLabel.setGeometry(QtCore.QRect(50, 50, 350, 60))
        font = QtGui.QFont()
        font.setPointSize(26)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setStyleSheet("""
            color: rgba(0, 0, 0, 180);
            font-weight: bold;
        """)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        
        # Username field - lớn hơn
        self.txtUsernameSignin = QtWidgets.QLineEdit(parent=self.widget)
        self.txtUsernameSignin.setGeometry(QtCore.QRect(60, 140, 330, 45))
        self.txtUsernameSignin.setStyleSheet("""
            QLineEdit {
                color: #2F4F4F;
                font-size: 18px;
                border-radius: 10px;
                padding: 12px 15px;
                border: 2px solid #ddd;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
                background-color: #f8f9ff;
            }
            QLineEdit::placeholder {
                color: #999;
            }
        """)
        self.txtUsernameSignin.setObjectName("txtUsernameSignin")

        # Email field
        self.txtEmail = QtWidgets.QLineEdit(parent=self.widget)
        self.txtEmail.setGeometry(QtCore.QRect(60, 210, 330, 45))
        self.txtEmail.setStyleSheet("""
            QLineEdit {
                color: #2F4F4F;
                font-size: 18px;
                border-radius: 10px;
                padding: 12px 15px;
                border: 2px solid #ddd;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
                background-color: #f8f9ff;
            }
            QLineEdit::placeholder {
                color: #999;
            }
        """)
        self.txtEmail.setObjectName("txtEmail")

        # Password field
        self.txtPasswordSignin = QtWidgets.QLineEdit(parent=self.widget)
        self.txtPasswordSignin.setGeometry(QtCore.QRect(60, 280, 330, 45))
        self.txtPasswordSignin.setStyleSheet("""
            QLineEdit {
                color: #2F4F4F;
                font-size: 18px;
                border-radius: 10px;
                padding: 12px 15px;
                border: 2px solid #ddd;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
                background-color: #f8f9ff;
            }
            QLineEdit::placeholder {
                color: #999;
            }
        """)
        self.txtPasswordSignin.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPasswordSignin.setObjectName("txtPasswordSignin")
        
        # Confirm Password field
        self.txtConfirmPassword = QtWidgets.QLineEdit(parent=self.widget)
        self.txtConfirmPassword.setGeometry(QtCore.QRect(60, 350, 330, 45))
        self.txtConfirmPassword.setStyleSheet("""
            QLineEdit {
                color: #2F4F4F;
                font-size: 18px;
                border-radius: 10px;
                padding: 12px 15px;
                border: 2px solid #ddd;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
                background-color: #f8f9ff;
            }
            QLineEdit::placeholder {
                color: #999;
            }
        """)
        self.txtConfirmPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtConfirmPassword.setObjectName("txtConfirmPassword")

        # Sign Up button - lớn và nổi bật
        self.btnSignin = QtWidgets.QPushButton(parent=self.widget)
        self.btnSignin.setGeometry(QtCore.QRect(60, 430, 330, 55))
        font3 = QtGui.QFont()
        font3.setBold(True)
        font3.setPointSize(18)
        self.btnSignin.setFont(font3)
        self.btnSignin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnSignin.setStyleSheet("""
            QPushButton#btnSignin{
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton#btnSignin:hover {
                background-color: #357ABD;
                transform: translateY(-2px);
            }
            QPushButton#btnSignin:pressed {
                background-color: #2C5F9E;
                transform: translateY(0px);
            }
        """)
        self.btnSignin.setObjectName("btnSignin")

        # Back to login button - chuyển từ label thành button
        self.backToLogin = QtWidgets.QPushButton(parent=self.widget)
        self.backToLogin.setGeometry(QtCore.QRect(60, 520, 330, 35))
        self.backToLogin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.backToLogin.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: rgba(0, 0, 0, 150);
                font-size: 16px;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: rgba(0, 0, 0, 200);
            }
            QPushButton:pressed {
                color: #4A90E2;
            }
        """)
        self.backToLogin.setObjectName("backToLogin")
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PycTalk - Create Account"))
        self.titleLabel.setText(_translate("MainWindow", "Create Account"))
        self.txtUsernameSignin.setPlaceholderText(_translate("MainWindow", "Username"))
        self.txtEmail.setPlaceholderText(_translate("MainWindow", "Email Address"))
        self.txtPasswordSignin.setPlaceholderText(_translate("MainWindow", "Password"))
        self.txtConfirmPassword.setPlaceholderText(_translate("MainWindow", "Confirm Password"))
        self.btnSignin.setText(_translate("MainWindow", "CREATE ACCOUNT"))
        self.backToLogin.setText(_translate("MainWindow", "Back to Login"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_SignInWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
