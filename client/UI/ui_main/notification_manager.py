from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

class NotificationManager:
    """Handle system notifications"""
    def __init__(self, parent):
        self.parent = parent
        self.tray_icon = None
        self.setup_tray_icon()
    
    def setup_tray_icon(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self.parent)
            icon = QtGui.QIcon()
            pixmap = QtGui.QPixmap(32, 32)
            pixmap.fill(QtGui.QColor('#3b82f6'))
            icon.addPixmap(pixmap)
            self.tray_icon.setIcon(icon)
            tray_menu = QMenu()
            show_action = QAction("Hiện cửa sổ", self.parent)
            show_action.triggered.connect(self.parent.show)
            quit_action = QAction("Thoát", self.parent)
            quit_action.triggered.connect(self.parent.close)
            tray_menu.addAction(show_action)
            tray_menu.addSeparator()
            tray_menu.addAction(quit_action)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self._on_tray_activated)
            self.tray_icon.show()
    
    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.parent.show()
            self.parent.raise_()
            self.parent.activateWindow()
    
    def show_notification(self, title: str, message: str):
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)
