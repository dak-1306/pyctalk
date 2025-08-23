import asyncio
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class GroupMessageSender(QObject):
    """Async gửi tin nhắn nhóm (không block UI)"""
    message_sent = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client

    @pyqtSlot(dict)
    async def send_message(self, request_data: dict):
        try:
            # Gửi request async (client cần hỗ trợ asyncio)
            response = await self.client.send_json(request_data)
            if response:
                self.message_sent.emit(response)
            else:
                self.error_occurred.emit("Không nhận được phản hồi từ server")
        except Exception as e:
            self.error_occurred.emit(f"Lỗi kết nối: {str(e)}")
