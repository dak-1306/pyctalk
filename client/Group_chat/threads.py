from PyQt6.QtCore import QThread, pyqtSignal

class MessageSenderThread(QThread):
    """Thread để gửi tin nhắn async, không block UI"""
    message_sent = pyqtSignal(dict)  # Signal khi gửi thành công
    error_occurred = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, client, request_data):
        super().__init__()
        self.client = client
        self.request_data = request_data

    def run(self):
        try:
            response = self.client.send_json(self.request_data)
            if response:
                self.message_sent.emit(response)
            else:
                self.error_occurred.emit("Không nhận được phản hồi từ server")
        except Exception as e:
            self.error_occurred.emit(f"Lỗi kết nối: {str(e)}")
