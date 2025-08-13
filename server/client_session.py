import json
import socket
from server.Login_server.RegisterHandle import register
from server.Login_server.LoginHandle import login
from server.HandleGroupChat.group_handler import GroupHandler
import time

class ClientSession:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.running = True
        self.group_handler = GroupHandler()
        # Thiết lập timeout cho socket để tránh treo
        self.client_socket.settimeout(30.0)  # 30 giây timeout

    def run(self):
        print(f"🟢 Client {self.client_address} session started.")
        self.last_ping_time = time.time()
        
        try:
            while self.running:
                # Kiểm tra timeout ping
                if time.time() - self.last_ping_time > 60:  # 60 giây không ping
                    self.handle_disconnect("Timeout - Không có ping từ client")
                    break
                    
                # Nhận 4 byte độ dài
                length_prefix = self.client_socket.recv(4)
                if not length_prefix:
                    self.handle_disconnect("Không nhận được độ dài thông điệp")
                    break

                message_length = int.from_bytes(length_prefix, 'big')
                
                # Giới hạn kích thước tin nhắn để tránh DoS
                if message_length > 1024 * 1024:  # 1MB max
                    self.handle_disconnect("Tin nhắn quá lớn")
                    break
                    
                message_data = b''
                bytes_received = 0
                while bytes_received < message_length:
                    remaining = message_length - bytes_received
                    chunk_size = min(remaining, 4096)  # Nhận tối đa 4KB mỗi lần
                    chunk = self.client_socket.recv(chunk_size)
                    if not chunk:
                        self.handle_disconnect("Kết nối bị đóng khi đang nhận dữ liệu")
                        break
                    message_data += chunk
                    bytes_received += len(chunk)

                if not message_data:
                    self.handle_disconnect("Không nhận được dữ liệu nào")
                    break

                self.handle_message(message_data)

        except (ConnectionResetError, socket.error) as e:
            self.handle_disconnect(f"Lỗi kết nối: {e}")
        except socket.timeout:
            self.handle_disconnect("Timeout - Không có hoạt động trong 30 giây")
        except Exception as e:
            self.handle_disconnect(f"Lỗi không mong muốn: {e}")

        finally:
            self.cleanup()

    def handle_disconnect(self, reason):
        print(f"⛔ Client {self.client_address} disconnected. Lý do: {reason}")
        self.running = False  # Gửi tín hiệu dừng vòng lặp

    def cleanup(self):
        try:
            self.client_socket.close()
            print(f"🔌 Đã đóng kết nối với {self.client_address}")
        except Exception as e:
            print(f"⚠️ Lỗi khi đóng socket {self.client_address}: {e}")

    def send_response(self, response_dict):
        try:
            response_json = json.dumps(response_dict, ensure_ascii=False).encode('utf-8')
            response_length = len(response_json).to_bytes(4, 'big')
            
            # Gửi length prefix
            self.client_socket.sendall(response_length)
            # Gửi data theo chunks để tránh buffer overflow
            bytes_sent = 0
            while bytes_sent < len(response_json):
                chunk = response_json[bytes_sent:bytes_sent + 8192]  # 8KB chunks
                self.client_socket.sendall(chunk)
                bytes_sent += len(chunk)
                
        except Exception as e:
            print(f"❌ Không gửi được phản hồi cho {self.client_address}: {e}")
            self.running = False  # Tự dừng nếu không gửi được

    def handle_message(self, raw_data):
        try:
            data = json.loads(raw_data.decode())
            action = data.get("action")
            if action == "ping":
                print(f"💓 Ping từ {self.client_address}({data['data']['username']})")
                # Cập nhật last_ping_time nếu có
                if hasattr(self, 'last_ping_time'):
                    self.last_ping_time = time.time()
                return
            elif action == "login":
                username = data["data"]["username"]
                password = data["data"]["password"]
                result = login.login_user(username, password)
                self.send_response(result)
                 
            elif action == "register":
                username = data["data"]["username"]
                password = data["data"]["password"]
                email = data["data"]["email"]
                result = register.register_user(username, password, email)
                self.send_response(result)
                self.running = False # Dừng phiên sau khi đăng ký thành công
                
            elif action == "logout":
                print(f"🔒 {self.client_address}({data['data']['username']}) yêu cầu đăng xuất.")
                self.send_response({"success": True, "message": "Đã đăng xuất."})
                self.running = False
                
            # ===== FRIEND ACTIONS (Not implemented yet) =====
            elif action == "get_suggestions":
                self.send_response({"success": False, "message": "Friend feature chưa được implement"})
                
            elif action == "add_friend":
                self.send_response({"success": False, "message": "Friend feature chưa được implement"})
                
            elif action == "get_friends":
                user_id = data["data"].get("user_id")
                # TODO: Lấy danh sách bạn bè từ DB, hiện trả về mẫu
                friends = [
                    {"user_id": 2, "username": "alice"},
                    {"user_id": 3, "username": "bob"}
                ]
                self.send_response({"success": True, "friends": friends})
                
            elif action == "get_friend_requests":
                self.send_response({"success": False, "message": "Friend feature chưa được implement"})
                
            elif action == "accept_friend":
                self.send_response({"success": False, "message": "Friend feature chưa được implement"})
                
            elif action == "reject_friend":
                self.send_response({"success": False, "message": "Friend feature chưa được implement"})
                
            elif action == "remove_friend":
                self.send_response({"success": False, "message": "Friend feature chưa được implement"})
                
            # ===== GROUP CHAT ACTIONS =====
            elif action == "create_group":
                group_name = data["data"]["group_name"]
                created_by = data["data"]["user_id"]
                result = self.group_handler.create_group(group_name, created_by)
                self.send_response(result)
                
            elif action == "add_member_to_group":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                admin_id = data["data"]["admin_id"]
                print(f"🔧 Adding member: group_id={group_id}, user_id={user_id}, admin_id={admin_id}")
                result = self.group_handler.add_member_to_group(group_id, user_id, admin_id)
                print(f"🔧 Add member result: {result}")
                self.send_response(result)
                
            elif action == "send_group_message":
                sender_id = data["data"]["sender_id"]
                group_id = data["data"]["group_id"]
                content = data["data"]["content"]
                result = self.group_handler.send_group_message(sender_id, group_id, content)
                self.send_response(result)
                
            elif action == "get_group_messages":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                limit = data["data"].get("limit", 50)
                offset = data["data"].get("offset", 0)
                result = self.group_handler.get_group_messages(group_id, user_id, limit, offset)
                self.send_response(result)
                
            elif action == "get_user_groups":
                user_id = data["data"]["user_id"]
                result = self.group_handler.get_user_groups(user_id)
                self.send_response(result)
                
            elif action == "get_group_members":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = self.group_handler.get_group_members(group_id, user_id)
                self.send_response(result)
                
            elif action == "send_message":
                pass  # handle_send_message(data)
            else:
                print(f"❓ Unknown action from {self.client_address}: {action}")
                self.send_response({"success": False, "message": f"Unknown action: {action}"})


        except json.JSONDecodeError:
            print(f"❌ Invalid JSON from {self.client_address}")
            self.send_response({"success": False, "message": "Invalid JSON"})
        except Exception as e:
            print(f"❌ Lỗi xử lý message từ {self.client_address}: {e}")
            self.send_response({"success": False, "message": f"Server error: {e}"})
