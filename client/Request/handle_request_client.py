import socket
import json
import threading
import time
import random

class PycTalkClient:
    def __init__(self, server_host='127.0.0.1', server_port=9000):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.running = False
        
        # === Biến để điều khiển ping thread ===
        self.ping_running = False
        self.ping_thread = None
        
        # === Lưu thông tin user đã đăng nhập ===
        self.user_id = None
        self.username = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            self.running = True
            print("🔗 Đã kết nối đến server.")
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False

    def disconnect(self):
        # Ngắt ping trước
        self.stop_ping()
        
        # Reset user info
        self.user_id = None
        self.username = None
        
        self.running = False
        if self.sock:
            try:
                self.sock.close()
                print("🔌 Đã ngắt kết nối với server.")
            except:
                pass
            finally:
                self.sock = None

    def send_json(self, data: dict):
        try:
            if not self.sock or not self.running:
                print("⚠️ Chưa có kết nối hoặc kết nối đã bị đóng.")
                return None

            json_request = json.dumps(data).encode()
            prefix = len(json_request).to_bytes(4, 'big')
            self.sock.sendall(prefix + json_request)

            # Nhận phản hồi
            length_prefix = self.sock.recv(4)
            if not length_prefix:
                print("⚠️ Server không phản hồi.")
                return

            response_length = int.from_bytes(length_prefix, 'big')
            response_data = b''
            while len(response_data) < response_length:
                chunk = self.sock.recv(response_length - len(response_data))
                if not chunk:
                    break
                response_data += chunk

            response = json.loads(response_data.decode())
            print("📥 Phản hồi từ server:", response)
            return response
        except Exception as e:
            print(f"❌ Lỗi khi gửi/nhận dữ liệu: {e}")
            self.disconnect()

    def register(self, username, password, email):
        if not self.connect():
            return
        request = {
            "action": "register",
            "data": {
                "username": username,
                "password": password,
                "email": email
            }
        }
        response = self.send_json(request)
        if response and response.get("success"):
            print("✅ Đăng kí thành công, giữ kết nối chờ các lệnh khác...")
            self.start_ping()
            self.idle_mode()
        else:
            self.disconnect()

    def login(self, username, password):
        if not self.connect():
            return
        request = {
            "action": "login",
            "data": {
                "username": username,
                "password": password
            }
        }
        response = self.send_json(request)
        if response and response.get("success"):
            print("✅ Đăng nhập thành công, giữ kết nối chờ các lệnh khác...")
            self.start_ping(username)
            self.idle_mode()
        else:
            self.disconnect()

    def idle_mode(self):
        try:
            while self.running:
                cmd = input("Nhập lệnh (logout / exit): ").strip().lower()
                if cmd == "logout":
                    self.send_json({"action": "logout", "data": {"username": username}})
                    print("🚪 Đã đăng xuất.")
                    break
                elif cmd == "exit":
                    print("👋 Thoát client.")
                    break
                else:
                    print("❓ Lệnh không hợp lệ.")
        finally:
            self.disconnect()

    def start_ping(self, username):
        # Gửi ping đều đặn để giữ kết nối
        def ping_loop():
            while self.ping_running and self.running:
                try:
                    time.sleep(15)  # mỗi 15–30s
                    if self.ping_running and self.running and self.sock:
                        self.send_json({"action": "ping", "data": {"username": username}})
                except Exception as e:
                    print(f"⚠️ Lỗi ping: {e}")
                    break
            
        # Nếu đã có thread ping đang chạy thì dừng nó trước
        if self.ping_running:
            self.stop_ping()
        
        self.ping_running = True
        self.ping_thread = threading.Thread(target=ping_loop, daemon=True)
        self.ping_thread.start()
        
    def stop_ping(self):
        """
        Dừng gửi ping
        """
        self.ping_running = False
        if self.ping_thread and self.ping_thread.is_alive():
            self.ping_thread.join(timeout=0.1)
            
    def get_user_id(self):
        """
        Lấy user_id của user đã đăng nhập
        """
        return self.user_id
    
    def get_username(self):
        """
        Lấy username của user đã đăng nhập
        """
        return self.username
    
    def is_logged_in(self):
        """
        Kiểm tra user đã đăng nhập chưa
        """
        return self.user_id is not None and self.username is not None

