import sys
import os
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QLoggingCategory
from Login.login_signIn import LoginWindow

# Suppress Qt font warnings
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.fonts.warning=false'
QLoggingCategory.setFilterRules("qt.qpa.fonts.warning=false")
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())