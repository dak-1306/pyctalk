import json
from server.Login_server.RegisterHandle import register
from server.Login_server.LoginHandle import login

import json
import socket

class ClientSession:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.running = True

    def run(self):
        print(f"🟢 Client {self.client_address} session started.")
        try:
            while self.running:
                # Nhận 4 byte độ dài
                length_prefix = self.client_socket.recv(4)
                if not length_prefix:
                    self.handle_disconnect("Không nhận được độ dài thông điệp")
                    break

                message_length = int.from_bytes(length_prefix, 'big')
                message_data = b''
                while len(message_data) < message_length:
                    chunk = self.client_socket.recv(message_length - len(message_data))
                    if not chunk:
                        self.handle_disconnect("Không nhận đủ dữ liệu từ client")
                        break
                    message_data += chunk

                if not message_data:
                    self.handle_disconnect("Không nhận được dữ liệu nào")
                    break

                self.handle_message(message_data)

        except (ConnectionResetError, socket.error) as e:
            self.handle_disconnect(f"Lỗi kết nối: {e}")

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
            response_json = json.dumps(response_dict).encode()
            response_length = len(response_json).to_bytes(4, 'big')
            self.client_socket.sendall(response_length + response_json)
        except Exception as e:
            print(f"❌ Không gửi được phản hồi cho {self.client_address}: {e}")
            self.running = False  # Tự dừng nếu không gửi được

            
    def send_response(self, response_dict):
        response_json = json.dumps(response_dict).encode()
        response_length = len(response_json).to_bytes(4, 'big')
        self.client_socket.sendall(response_length + response_json)

    def handle_message(self, raw_data):
        try:
            data = json.loads(raw_data.decode())
            action = data.get("action")
            if action == "ping":
                print(f"💓 Ping từ {self.client_address}({data['data']['username']})")
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
            # ===== GROUP CHAT ACTIONS =====
            elif action == "create_group":
                group_name = data["data"]["group_name"]
                created_by = data["data"]["user_id"]
                result = group_handler.create_group(group_name, created_by)
                self.send_response(result)
                
            elif action == "add_member_to_group":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                admin_id = data["data"]["admin_id"]
                result = group_handler.add_member_to_group(group_id, user_id, admin_id)
                self.send_response(result)
                
            elif action == "send_group_message":
                sender_id = data["data"]["sender_id"]
                group_id = data["data"]["group_id"]
                content = data["data"]["content"]
                result = group_handler.send_group_message(sender_id, group_id, content)
                self.send_response(result)
                
            elif action == "get_group_messages":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                limit = data["data"].get("limit", 50)
                result = group_handler.get_group_messages(group_id, user_id, limit)
                self.send_response(result)
                
            elif action == "get_user_groups":
                user_id = data["data"]["user_id"]
                result = group_handler.get_user_groups(user_id)
                self.send_response(result)
                
            elif action == "get_group_members":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = group_handler.get_group_members(group_id, user_id)
                self.send_response(result)
                
            elif action == "send_message":
                pass  # handle_send_message(data)
            else:
                print(f"❓ Unknown action from {self.client_address}: {action}")


        except json.JSONDecodeError:
            print(f"❌ Invalid JSON from {self.client_address}")
