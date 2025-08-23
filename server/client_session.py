import json
import asyncio
import time
from server.Login_server.RegisterHandle import register
from server.Login_server.LoginHandle import login
from server.HandleGroupChat.group_handler import GroupHandler


class ClientSession:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_address):
        self.reader = reader
        self.writer = writer
        self.client_address = client_address
        self.running = True
        self.group_handler = GroupHandler()
        self.last_ping_time = time.time()

        # Friend handler
        try:
            from server.Handle_AddFriend.friend_handle import friend_handler
            self.friend_handler = friend_handler
        except Exception as e:
            print(f"Không thể import friend_handler: {e}")
            self.friend_handler = None

        # Chat 1-1 handler
        try:
            from server.HandleChat1_1.chat_handler import chat_handler
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

    async def send_response(self, response_dict):
        try:
            response_json = json.dumps(response_dict, ensure_ascii=False).encode("utf-8")
            response_length = len(response_json).to_bytes(4, "big")
            self.writer.write(response_length + response_json)
            await self.writer.drain()
        except Exception as e:
            print(f"❌ Không gửi được phản hồi cho {self.client_address}: {e}")
            self.running = False

    async def handle_message(self, raw_data):
        try:
            data = json.loads(raw_data.decode())
            action = data.get("action")

            if action == "ping":
                print(f"💓 Ping từ {self.client_address} ({data['data']['username']})")
                self.last_ping_time = time.time()
                return

            elif action == "login":
                username = data["data"]["username"]
                password = data["data"]["password"]
                result = await login.login_user(username, password)
                await self.send_response(result)

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
                await self.send_response(result)
                self.running = False

            elif action == "logout":
                print(f"🔒 {self.client_address} yêu cầu đăng xuất.")
                await self.send_response({"success": True, "message": "Đã đăng xuất."})
                self.running = False

            # ===== FRIEND ACTIONS =====
            elif action == "get_suggestions" and self.friend_handler:
                username = data["data"].get("username")
                result = await self.friend_handler.get_suggestions(username)
                await self.send_response({"success": result.get("status") == "ok", **result})

            elif action == "add_friend" and self.friend_handler:
                from_user = data["data"].get("from_user")
                to_user = data["data"].get("to_user")
                result = await self.friend_handler.add_friend(from_user, to_user)
                await self.send_response({"success": result.get("status") == "ok", **result})

            elif action == "get_friends" and self.friend_handler:
                username = data["data"].get("username")
                result = await self.friend_handler.get_friends(username)
                await self.send_response({"success": result.get("status") == "ok", **result})

            elif action == "get_friend_requests" and self.friend_handler:
                username = data["data"].get("username")
                result = await self.friend_handler.get_friend_requests(username)
                await self.send_response({"success": result.get("status") == "ok", **result})

            elif action == "accept_friend" and self.friend_handler:
                username = data["data"].get("username")
                from_user = data["data"].get("from_user")
                result = await self.friend_handler.accept_friend(username, from_user)
                await self.send_response({"success": result.get("status") == "ok", **result})

            elif action == "reject_friend" and self.friend_handler:
                username = data["data"].get("username")
                from_user = data["data"].get("from_user")
                result = await self.friend_handler.reject_friend(username, from_user)
                await self.send_response({"success": result.get("status") == "ok", **result})

            elif action == "remove_friend" and self.friend_handler:
                username = data["data"].get("username")
                friend_name = data["data"].get("friend_name")
                result = await self.friend_handler.remove_friend(username, friend_name)
                await self.send_response({"success": result.get("status") == "ok", **result})

            # ===== CHAT 1-1 =====
            elif action == "get_chat_history" and self.chat1v1_handler:
                user_id = data["data"].get("user_id")
                friend_id = data["data"].get("friend_id")
                limit = data["data"].get("limit", 50)
                result = await self.chat1v1_handler.handle_get_history(self.writer, {
                    "user1": user_id,
                    "user2": friend_id,
                    "limit": limit
                })
                # Trả về đúng định dạng: success, data (chứa messages), message
                await self.send_response({
                    "success": result.get("success", False),
                    "data": result.get("data", {}),
                    "message": result.get("message", "")
                })
            elif action == "create_group_with_members":
                group_name = data["data"].get("group_name")
                created_by = data["data"].get("user_id")
                member_ids = data["data"].get("member_ids", [])
                result = await self.group_handler.create_group_with_members(group_name, created_by, member_ids)
                await self.send_response(result)

            elif action == "create_group":
                group_name = data["data"]["group_name"]
                created_by = data["data"]["user_id"]
                result = await self.group_handler.create_group(group_name, created_by)
                await self.send_response(result)

            elif action == "add_member_to_group":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                admin_id = data["data"]["admin_id"]
                result = await self.group_handler.add_member_to_group(group_id, user_id, admin_id)
                await self.send_response(result)

            elif action == "send_group_message":
                sender_id = data["data"]["sender_id"]
                group_id = data["data"]["group_id"]
                content = data["data"]["content"]
                result = await self.group_handler.send_group_message(sender_id, group_id, content)
                await self.send_response(result)

            elif action == "get_group_messages":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                limit = data["data"].get("limit", 50)
                offset = data["data"].get("offset", 0)
                result = await self.group_handler.get_group_messages(group_id, user_id, limit, offset)
                await self.send_response(result)

            elif action == "get_user_groups":
                user_id = data["data"]["user_id"]
                result = await self.group_handler.get_user_groups(user_id)
                await self.send_response(result)

            elif action == "get_group_members":
                group_id = data["data"]["group_id"]
                user_id = data["data"]["user_id"]
                result = await self.group_handler.get_group_members(group_id, user_id)
                await self.send_response(result)

            elif action == "send_message" and self.chat1v1_handler:
                print(f"[DEBUG] Server received send_message: {data}")
                result = await self.chat1v1_handler.handle_message_request(self.reader, self.writer, data)
                await self.send_response(result)

            else:
                await self.send_response({"success": False, "message": f"Unknown action: {action}"})

        except json.JSONDecodeError:
            await self.send_response({"success": False, "message": "Invalid JSON"})
        except Exception as e:
            await self.send_response({"success": False, "message": f"Server error: {e}"})
