import threading
import json
import time

class Chat1v1Client:
    """
    Xử lý logic gửi/nhận tin nhắn 1-1 real-time qua socket cho client
    """
    def __init__(self, pyctalk_client, on_receive_callback=None):
        self.client = pyctalk_client  # Instance của PycTalkClient
        self.on_receive_callback = on_receive_callback  # Hàm callback khi nhận tin nhắn mới
        self.running = False
        self.listen_thread = None

    def send_message(self, to_username, message_text):
        """Gửi tin nhắn 1-1 tới server"""
        if not self.client.is_logged_in():
            print("Bạn cần đăng nhập để gửi tin nhắn.")
            return None
        request = {
            "action": "send_message",
            "data": {
                "from": self.client.get_username(),
                "to": to_username,
                "message": message_text
            }
        }
        return self.client.send_json(request)

    def start_listen(self):
        """Bắt đầu lắng nghe tin nhắn mới từ server"""
        if self.listen_thread and self.listen_thread.is_alive():
            return
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

    def stop_listen(self):
        """Dừng lắng nghe"""
        self.running = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)

    def _listen_loop(self):
        """Luồng lắng nghe socket để nhận tin nhắn mới"""
        sock = self.client.sock
        while self.running and sock:
            try:
                # Nhận length prefix
                length_prefix = sock.recv(4)
                if not length_prefix:
                    time.sleep(0.1)
                    continue
                message_length = int.from_bytes(length_prefix, 'big')
                if message_length <= 0 or message_length > 10 * 1024 * 1024:
                    continue
                message_data = b''
                bytes_received = 0
                while bytes_received < message_length:
                    chunk = sock.recv(message_length - bytes_received)
                    if not chunk:
                        break
                    message_data += chunk
                    bytes_received += len(chunk)
                if not message_data:
                    continue
                try:
                    response = json.loads(message_data.decode())
                    # Nếu là tin nhắn mới
                    if response.get("action") == "receive_message":
                        if self.on_receive_callback:
                            self.on_receive_callback(response.get("data"))
                except Exception as e:
                    print(f"Lỗi khi parse message: {e}")
            except Exception as e:
                time.sleep(0.1)
                continue
