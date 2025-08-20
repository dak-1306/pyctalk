import sys
from PyQt6 import QtWidgets, QtGui
from .ui_main_window import Ui_MainWindow
from .fake_client import FakeClient

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("PycTalk Enhanced")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PycTalk Team")
    icon = QtGui.QIcon()
    pixmap = QtGui.QPixmap(32, 32)
    pixmap.fill(QtGui.QColor('#3b82f6'))
    icon.addPixmap(pixmap)
    app.setWindowIcon(icon)
    main_window = QtWidgets.QMainWindow()
    client = FakeClient("DemoUser")
    ui = Ui_MainWindow(username="DemoUser", client=client, main_window=main_window)
    ui.setupUi(main_window)
    main_window.show()
    from .animation_helper import AnimationHelper
    AnimationHelper.fade_in(main_window, 500)
    def cleanup_and_exit():
        ui._cleanup_resources()
        app.quit()
    app.aboutToQuit.connect(cleanup_and_exit)
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        cleanup_and_exit()
    except Exception:
        cleanup_and_exit()

if __name__ == "__main__":
    main()
