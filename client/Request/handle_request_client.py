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

            # Nhận phản hồi với timeout và buffer handling
            self.sock.settimeout(10.0)  # 10 second timeout
            
            # Nhận length prefix (4 bytes)
            length_prefix = b''
            while len(length_prefix) < 4:
                chunk = self.sock.recv(4 - len(length_prefix))
                if not chunk:
                    print("⚠️ Server đóng kết nối khi nhận length prefix.")
                    return None
                length_prefix += chunk

            response_length = int.from_bytes(length_prefix, 'big')
            
            # Validate response length
            if response_length <= 0 or response_length > 10 * 1024 * 1024:  # Max 10MB
                print(f"⚠️ Response length không hợp lệ: {response_length}")
                return None
            
            # Nhận data với buffer size cố định
            response_data = b''
            bytes_received = 0
            while bytes_received < response_length:
                remaining = response_length - bytes_received
                chunk_size = min(remaining, 8192)  # 8KB chunks
                chunk = self.sock.recv(chunk_size)
                if not chunk:
                    print(f"⚠️ Connection closed. Received {bytes_received}/{response_length} bytes")
                    break
                response_data += chunk
                bytes_received += len(chunk)

            if not response_data or len(response_data) != response_length:
                print(f"⚠️ Dữ liệu không đầy đủ. Nhận được {len(response_data)}/{response_length} bytes.")
                if response_data:
                    print(f"⚠️ Partial data: {response_data[:100]}...")
                return None
                
            try:
                response = json.loads(response_data.decode())
                print("📥 Phản hồi từ server:", response)
                return response
            except json.JSONDecodeError as e:
                print(f"⚠️ Lỗi parse JSON: {e}. Data: {response_data}")
                return None
                
        except socket.timeout:
            print("⚠️ Timeout khi giao tiếp với server.")
            return None
        except Exception as e:
            print(f"❌ Lỗi khi gửi/nhận dữ liệu: {e}")
            self.disconnect()
            return None

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
            print("✅ Đăng nhập thành công.")
            # Lưu thông tin user
            self.user_id = response.get("user_id")
            self.username = username
            self.start_ping()
            return response
        else:
            self.disconnect()
            return response

    def idle_mode(self):
        try:
            while self.running:
                cmd = input("Nhập lệnh (logout / exit): ").strip().lower()
                if cmd == "logout":
                    self.send_json({"action": "logout", "data": {"username": self.username}})
                    print("🚪 Đã đăng xuất.")
                    break
                elif cmd == "exit":
                    print("👋 Thoát client.")
                    break
                else:
                    print("❓ Lệnh không hợp lệ.")
        finally:
            self.disconnect()

    def start_ping(self):
        # Gửi ping đều đặn để giữ kết nối
        def ping_loop():
            while self.ping_running and self.running:
                try:
                    time.sleep(15)  # mỗi 15 giây
                    if self.ping_running and self.running and self.sock and self.username:
                        self.send_json({"action": "ping", "data": {"username": self.username}})
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
        if self.ping_thread and self.ping_thread.is_alive() and self.ping_thread != threading.current_thread():
            try:
                self.ping_thread.join(timeout=1.0)  # Tăng timeout
            except RuntimeError:
                pass  # Ignore nếu không thể join
            
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

