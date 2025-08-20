from PyQt6 import QtCore

class SettingsManager:
    """Simple settings manager for user preferences"""
    def __init__(self):
        self.settings = QtCore.QSettings("PycTalk", "MainClient")
    
    def get(self, key: str, default=None):
        return self.settings.value(key, default)
    
    def set(self, key: str, value):
        self.settings.setValue(key, value)
        self.settings.sync()
