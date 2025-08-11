# Modern Signup UI for PycTalk
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_SignInWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(480, 650)  # Tăng kích thước to hơn
        MainWindow.setMaximumSize(480, 650)
        MainWindow.resize(480, 650)
        MainWindow.setWindowTitle("PycTalk - Create Account")
        
        self.MainWindow = MainWindow
        
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Main container - to hơn
        self.widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 20, 440, 610))
        self.widget.setObjectName("widget")
        
        # Background với gradient
        self.background = QtWidgets.QLabel(parent=self.widget)
        self.background.setGeometry(QtCore.QRect(0, 0, 440, 610))
        self.background.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #b2ebf2, stop:1 #e0f7fa);
            border-radius: 20px;
        """)
        self.background.setText("")
        self.background.setObjectName("background")
        
        # Title - compact
        self.titleLabel = QtWidgets.QLabel(parent=self.widget)
        self.titleLabel.setGeometry(QtCore.QRect(10, 15, 240, 30))
        font = QtGui.QFont()
        font.setPointSize(14)  # Smaller font
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setStyleSheet("""
            color: rgba(0, 0, 0, 180);
            font-weight: bold;
        """)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        
        # Username field - compact
        self.txtUsernameSignin = QtWidgets.QLineEdit(parent=self.widget)
        self.txtUsernameSignin.setGeometry(QtCore.QRect(20, 55, 220, 25))  # Smaller height
        self.txtUsernameSignin.setStyleSheet("""
            color: #2F4F4F;
            font-size: 12px;
            border-radius: 4px;
            padding: 3px;
            border: 1px solid #ddd;
            background-color: white;
        """)
        self.txtUsernameSignin.setObjectName("txtUsernameSignin")

        # Email field - compact
        self.txtEmail = QtWidgets.QLineEdit(parent=self.widget)
        self.txtEmail.setGeometry(QtCore.QRect(20, 90, 220, 25))
        self.txtEmail.setStyleSheet("""
            color: #2F4F4F;
            font-size: 12px;
            border-radius: 4px;
            padding: 3px;
            border: 1px solid #ddd;
            background-color: white;
        """)
        self.txtEmail.setObjectName("txtEmail")

        # Password field - compact
        self.txtPasswordSignin = QtWidgets.QLineEdit(parent=self.widget)
        self.txtPasswordSignin.setGeometry(QtCore.QRect(20, 125, 220, 25))
        self.txtPasswordSignin.setStyleSheet("""
            color: #2F4F4F;
            font-size: 12px;
            border-radius: 4px;
            padding: 3px;
            border: 1px solid #ddd;
            background-color: white;
        """)
        self.txtPasswordSignin.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPasswordSignin.setObjectName("txtPasswordSignin")
        
        # Confirm Password field - compact
        self.txtConfirmPassword = QtWidgets.QLineEdit(parent=self.widget)
        self.txtConfirmPassword.setGeometry(QtCore.QRect(20, 160, 220, 25))
        self.txtConfirmPassword.setStyleSheet("""
            color: #2F4F4F;
            font-size: 12px;
            border-radius: 4px;
            padding: 3px;
            border: 1px solid #ddd;
            background-color: white;
        """)
        self.txtConfirmPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtConfirmPassword.setObjectName("txtConfirmPassword")

        # Sign Up button - compact
        self.btnSignin = QtWidgets.QPushButton(parent=self.widget)
        self.btnSignin.setGeometry(QtCore.QRect(20, 200, 220, 32))  # Smaller button
        font3 = QtGui.QFont()
        font3.setBold(True)
        font3.setWeight(75)
        self.btnSignin.setFont(font3)
        self.btnSignin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnSignin.setStyleSheet("""
            QPushButton#btnSignin{
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#btnSignin:hover {
                background-color: #357ABD;
            }
            QPushButton#btnSignin:pressed {
                padding-right: 3px;
                padding-bottom: 3px;
                background-color: #2C5F9E;
            }
        """)
        self.btnSignin.setObjectName("btnSignin")

        # Back to login link - compact
        self.backToLogin = QtWidgets.QLabel(parent=self.widget)
        self.backToLogin.setGeometry(QtCore.QRect(20, 240, 220, 18))
        self.backToLogin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.backToLogin.setStyleSheet("""
            color: rgba(0, 0, 0, 180);
            font-size: 11px;
        """)
        self.backToLogin.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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
        self.btnSignin.setText(_translate("MainWindow", "S i g n  U p"))
        self.backToLogin.setText(_translate("MainWindow", "Back to Login"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_SignInWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
