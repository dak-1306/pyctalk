import sys
import os
import logging
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QLoggingCategory

# Add parent directory to path so we can import client modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Login.login_signIn import LoginWindow

# Cấu hình logging để log debug hiện ra console
logging.basicConfig(level=logging.DEBUG)

# Suppress Qt font warnings
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.fonts.warning=false'
QLoggingCategory.setFilterRules("qt.qpa.fonts.warning=false")
        
if __name__ == "__main__":
    from qasync import QEventLoop
    import asyncio
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = LoginWindow()
    window.show()
    with loop:
        loop.run_forever()