import json
import asyncio
import time
from Login_server.RegisterHandle import register
from Login_server.LoginHandle import login
from HandleGroupChat.group_handler import GroupHandler


class ClientSession:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_address):
        self.reader = reader
        self.writer = writer
        self.client_address = client_address
        self.running = True
        self.group_handler = GroupHandler()
        self.last_ping_time = time.time()        # Friend handler
        try:
            from Handle_AddFriend.friend_handle import friend_handler
            self.friend_handler = friend_handler
        except Exception as e:
            print(f"Không thể import friend_handler: {e}")
            self.friend_handler = None

        # Chat 1-1 handler
        try:
            from HandleChat1_1.chat_handler import chat_handler
            self.chat1v1_handler = chat_handler
        except Exception as e:
            print(f"Không thể import chat_handler: {e}")
            self.chat1v1_handler = None

    async def run(self):
        print(f"🟢 Client {self.client_address} session started.")
        try:
            while self.running:
                # timeout ping
                if time.time() - self.last_ping_time > 60:
                    await self.handle_disconnect("Timeout - Không có ping từ client")
                    break

                # đọc 4 byte length prefix
                length_prefix = await self.reader.readexactly(4)
                if not length_prefix:
                    await self.handle_disconnect("Không nhận được độ dài thông điệp")
                    break

                message_length = int.from_bytes(length_prefix, "big")

                if message_length > 1024 * 1024:  # 1MB
                    await self.handle_disconnect("Tin nhắn quá lớn")
                    break

                message_data = await self.reader.readexactly(message_length)
                if not message_data:
                    await self.handle_disconnect("Không nhận được dữ liệu nào")
                    break

                await self.handle_message(message_data)

        except asyncio.IncompleteReadError:
            await self.handle_disconnect("Client đóng kết nối")
        except Exception as e:
            await self.handle_disconnect(f"Lỗi: {e}")
        finally:
            await self.cleanup()

    async def handle_disconnect(self, reason):
        print(f"⛔ Client {self.client_address} disconnected. Lý do: {reason}")
        self.running = False

    async def cleanup(self):
        try:
            self.writer.close()
            await self.writer.wait_closed()
            print(f"🔌 Đã đóng kết nối với {self.client_address}")
        except Exception as e:
            print(f"⚠️ Lỗi khi đóng writer {self.client_address}: {e}")

    async def send_response(self, response_dict, request_id=None):
        try:
            # Thêm request_id vào response nếu có
            if request_id:
                response_dict["_request_id"] = request_id
            print(f"[DEBUG] Sending response to {self.client_address}: {response_dict}")
            response_json = json.dumps(response_dict, ensure_ascii=False).encode("utf-8")
            response_length = len(response_json).to_bytes(4, "big")
            self.writer.write(response_length + response_json)
            await self.writer.drain()
            print(f"[DEBUG] Response sent successfully to {self.client_address}")
        except Exception as e:
            print(f"❌ Không gửi được phản hồi cho {self.client_address}: {e}")
            self.running = False

    async def handle_message(self, raw_data):
        request_id = None  # Initialize request_id at top level
        try:
            data = json.loads(raw_data.decode())
            action = data.get("action")
            request_id = data.get("_request_id")  # Lấy request ID từ client
            print(f"[DEBUG] Handling action: {action}, request_id: {request_id}")

            if action == "ping":
                print(f"💓 Ping từ {self.client_address} ({data['data']['username']})")
                self.last_ping_time = time.time()
                return

            elif action == "login":
                username = data["data"]["username"]
                password = data["data"]["password"]
                result = await login.login_user(username, password)
                await self.send_response(result, request_id)

                if result and result.get("success") and self.chat1v1_handler:
                    try:
                        self.chat1v1_handler.register_user_connection(username, self.writer)
                        print(f"[Chat1v1] Registered real-time connection for {username}")
                    except Exception as e:
                        print(f"[Chat1v1] Failed to register connection for {username}: {e}")

            elif action == "register":
                username = data["data"]["username"]
                password = data["data"]["password"]
                email = data["data"]["email"]
                result = await register.register_user(username, password, email)
                await self.send_response(result, request_id)
                self.running = False

            elif action == "logout":
                if self.chat1v1_handler:
                    self.chat1v1_handler.unregister_user_connection(self.client_address)
                await self.send_response({"success": True, "message": "Đăng xuất thành công."}, request_id)
                self.running = False

            elif action == "get_friends":
                username = data["data"]["username"]
                result = await self.friend_handler.get_friends(username)
                await self.send_response(result, request_id)

            elif action == "send_friend_request":
                sender_username = data["data"]["sender_username"]
                receiver_username = data["data"]["receiver_username"]
                result = await self.friend_handler.add_friend(sender_username, receiver_username)
                await self.send_response(result, request_id)

            elif action == "get_friend_requests":
                username = data["data"]["username"]
                result = await self.friend_handler.get_friend_requests(username)
                await self.send_response(result, request_id)

            elif action == "get_sent_friend_requests":
                username = data["data"]["username"]
                print(f"[DEBUG] Server: get_sent_friend_requests for username={username}")
                result = await self.friend_handler.get_sent_friend_requests(username)
                print(f"[DEBUG] Server: get_sent_friend_requests result={result}")
                await self.send_response(result, request_id)

            elif action == "handle_friend_request":
                from_username = data["data"]["from_username"]
                to_username = data["data"]["to_username"]
                action_param = data["data"]["action"]
                result = await self.friend_handler.handle_friend_request(from_username, to_username, action_param)
                await self.send_response(result, request_id)

            elif action == "cancel_friend_request":
                sender_username = data["data"]["sender_username"]
                receiver_username = data["data"]["receiver_username"]
                result = await self.friend_handler.cancel_friend_request(sender_username, receiver_username)
                await self.send_response(result, request_id)

            elif action == "remove_friend":
                username = data["data"]["username"]
                friend_name = data["data"]["friend_name"]
                result = await self.friend_handler.remove_friend(username, friend_name)
                await self.send_response(result, request_id)

            elif action == "search_users":
                query = data["data"]["query"]
                result = await self.friend_handler.search_users(query)
                await self.send_response(result, request_id)

            elif action == "get_chat_history" and self.chat1v1_handler:
                result = await self.chat1v1_handler.handle_message_request(self.reader, self.writer, data)
                await self.send_response(result, request_id)

            elif action == "create_group":
                group_name = data["data"]["group_name"]
                user_id = data["data"]["user_id"]
                result = await self.group_handler.create_group(group_name, user_id)
                await self.send_response(result, request_id)

            elif action == "get_user_groups":
                user_id = data["data"]["user_id"]
                result = await self.group_handler.get_user_groups(user_id)
                await self.send_response(result, request_id)

            elif action == "add_user_to_group":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = await self.group_handler.add_user_to_group(group_id, user_id)
                await self.send_response(result, request_id)

            elif action == "get_group_messages":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = await self.group_handler.get_group_messages(group_id, user_id)
                await self.send_response(result, request_id)

            elif action == "send_group_message":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                message = data["data"]["message"]
                result = await self.group_handler.send_group_message(user_id, group_id, message)  # Fixed parameter order
                await self.send_response(result, request_id)

            elif action == "join_group":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = await self.group_handler.join_group(group_id, user_id)
                await self.send_response(result, request_id)

            elif action == "leave_group":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = await self.group_handler.leave_group(group_id, user_id)
                await self.send_response(result, request_id)

            elif action == "get_group_members":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = await self.group_handler.get_group_members(group_id, user_id)
                await self.send_response(result, request_id)

            elif action == "send_message" and self.chat1v1_handler:
                print(f"[DEBUG] Server received send_message: {data}")
                result = await self.chat1v1_handler.handle_message_request(self.reader, self.writer, data)
                await self.send_response(result, request_id)

            else:
                await self.send_response({"success": False, "message": f"Unknown action: {action}"}, request_id)

        except json.JSONDecodeError:
            await self.send_response({"success": False, "message": "Invalid JSON"}, request_id)
        except Exception as e:
            await self.send_response({"success": False, "message": f"Server error: {e}"}, request_id)

                   
         