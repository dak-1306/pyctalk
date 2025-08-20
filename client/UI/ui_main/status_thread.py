from PyQt6.QtCore import QThread, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class StatusUpdateThread(QThread):
    """Thread for handling status updates without blocking UI"""
    status_changed = pyqtSignal(bool, str)
    
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.running = True
        
    def run(self):
        while self.running:
            try:
                if self.client:
                    is_connected = self.client.is_logged_in()
                    status = "Đã kết nối" if is_connected else "Mất kết nối"
                    self.status_changed.emit(is_connected, status)
                self.msleep(5000)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Status update error: {e}")
                self.msleep(10000)  # Wait longer on error
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait()
