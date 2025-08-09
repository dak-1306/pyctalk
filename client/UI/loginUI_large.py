# Large Login UI for PycTalk
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_LoginWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(500, 600)  # Kích thước lớn khớp với signup
        MainWindow.setMaximumSize(500, 600)
        MainWindow.resize(500, 600)
        MainWindow.setWindowTitle("PycTalk - Login")
        
        # Lưu reference để tính toán responsive
        self.MainWindow = MainWindow
        
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(25, 25, 450, 550))
        self.widget.setObjectName("widget")
        
        self.label = QtWidgets.QLabel(parent=self.widget)
        self.label.setGeometry(QtCore.QRect(0, 0, 450, 550))
        self.label.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #b2ebf2, stop:1 #e0f7fa);
            border-radius: 25px;
        """)
        self.label.setText("")
        self.label.setObjectName("label")
        
        # Title
        self.titleLabel = QtWidgets.QLabel(parent=self.widget)
        self.titleLabel.setGeometry(QtCore.QRect(50, 60, 350, 60))
        font = QtGui.QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setStyleSheet("""
            color: rgba(0, 0, 0, 180);
            font-weight: bold;
        """)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setText("Welcome Back")
        
        # Username field
        self.txtUsername = QtWidgets.QLineEdit(parent=self.widget)
        self.txtUsername.setGeometry(QtCore.QRect(60, 160, 330, 45))
        self.txtUsername.setStyleSheet("""
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
        self.txtUsername.setObjectName("txtUsername")
        
        # Password field
        self.txtPassword = QtWidgets.QLineEdit(parent=self.widget)
        self.txtPassword.setGeometry(QtCore.QRect(60, 230, 330, 45))
        self.txtPassword.setStyleSheet("""
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
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtPassword.setObjectName("txtPassword")
        
        # Login button
        self.btnLogin = QtWidgets.QPushButton(parent=self.widget)
        self.btnLogin.setGeometry(QtCore.QRect(60, 310, 330, 55))
        font2 = QtGui.QFont()
        font2.setBold(True)
        font2.setPointSize(18)
        self.btnLogin.setFont(font2)
        self.btnLogin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnLogin.setStyleSheet("""
            QPushButton#btnLogin{
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton#btnLogin:hover {
                background-color: #357ABD;
            }
            QPushButton#btnLogin:pressed {
                background-color: #2C5F9E;
            }
        """)
        self.btnLogin.setObjectName("btnLogin")
        
        # Create account link
        self.creatAccount = QtWidgets.QLabel(parent=self.widget)
        self.creatAccount.setGeometry(QtCore.QRect(60, 390, 330, 35))
        self.creatAccount.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.creatAccount.setStyleSheet("""
            color: rgba(0, 0, 0, 150);
            font-size: 16px;
            text-decoration: underline;
        """)
        self.creatAccount.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.creatAccount.setObjectName("creatAccount")
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        # Thêm event handler cho responsive
        MainWindow.resizeEvent = self.on_resize

    def on_resize(self, event):
        """Xử lý responsive khi thay đổi kích thước cửa sổ"""
        window_width = self.MainWindow.width()
        window_height = self.MainWindow.height()
        
        # Tính toán vị trí widget ở giữa
        widget_width = 450
        widget_height = 550
        
        # Căn giữa widget
        x = (window_width - widget_width) // 2
        y = (window_height - widget_height) // 2
        
        # Đảm bảo không ra ngoài biên
        x = max(25, x)
        y = max(25, y)
        
        # Cập nhật vị trí widget
        self.widget.setGeometry(QtCore.QRect(x, y, widget_width, widget_height))
        self.label.setGeometry(QtCore.QRect(0, 0, widget_width, widget_height))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PycTalk - Login"))
        self.txtUsername.setPlaceholderText(_translate("MainWindow", "Username"))
        self.txtPassword.setPlaceholderText(_translate("MainWindow", "Password"))
        self.btnLogin.setText(_translate("MainWindow", "LOGIN"))
        self.creatAccount.setText(_translate("MainWindow", "Create an Account?"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_LoginWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
