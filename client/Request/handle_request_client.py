import asyncio
import json
from PyQt6.QtCore import QObject, pyqtSignal


class AsyncPycTalkClient(QObject):
    # Signals for real-time events
    new_message_received = pyqtSignal(dict)  # Emit when new message received
    user_status_changed = pyqtSignal(str, str)  # Emit when user status changes
    async def send_request(self, action, data):
        """
        Chuẩn hóa API cho chat 1-1: get_chat_history, send_message
        action: tên hành động ("get_chat_history", "send_message", ...)
        data: dict chứa tham số
        """
        # Map action sang format request
        if action == "get_chat_history":
            request = {
                "action": "get_chat_history",
                "data": {
                    "user1": data.get("user_id") or data.get("user1"),
                    "user2": data.get("friend_id") or data.get("user2"),
                    "limit": data.get("limit", 50)
                }
            }
        elif action == "send_message":
            # Chat 1-1: gửi from/to cho server
            request = {
                "action": "send_message",
                "data": {
                    "from": str(data.get("from") or data.get("user_id")),
                    "to": str(data.get("to") or data.get("friend_id")),
                    "message": str(data.get("message"))
                }
            }
        else:
            # Các action khác giữ nguyên
            request = {
                "action": action,
                "data": data
            }
        return await self.send_json(request)
    def __init__(self, server_host='127.0.0.1', server_port=9000):
        super().__init__()  # Initialize QObject
        self._io_lock = asyncio.Lock()
        self.server_host = server_host
        self.server_port = server_port
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.running = False

        # Ping task
        self.ping_task: asyncio.Task | None = None

        # Thông tin user
        self.user_id = None
        self.username = None

        # Queue ghép request với callback - sử dụng dict để match theo ID
        self._pending_requests = {}  # {request_id: callback}
        self._request_counter = 0
        self._listen_task = None

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server_host, self.server_port
            )
            self.running = True
            print("🔗 Đã kết nối đến server.")
            # Chỉ khởi động listen_loop một lần duy nhất
            if not self._listen_task or self._listen_task.done():
                self._listen_task = asyncio.create_task(self.listen_loop())
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False

    async def disconnect(self):
        self.stop_ping()

        self.user_id = None
        self.username = None
        self.running = False

        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
                print("🔌 Đã ngắt kết nối với server.")
            except Exception:
                pass
            finally:
                self.reader, self.writer = None, None

    async def send_json(self, data: dict, callback=None):
        print(f"[DEBUG] send_json called with data: {data}")
        try:
            # Thêm timeout cho lock để tránh deadlock
            async def acquire_lock_and_send():
                async with self._io_lock:
                    print(f"[DEBUG] Acquired io_lock for data: {data}")
                    try:
                        if not self.writer or not self.running:
                            print("⚠️ Chưa có kết nối hoặc kết nối đã bị đóng.")
                            return None

                        # Tạo unique request ID
                        self._request_counter += 1
                        request_id = f"req_{self._request_counter}"
                        
                        # Tạo future để nhận response
                        loop = asyncio.get_running_loop()
                        future = loop.create_future()
                        print(f"[DEBUG] Created future for data: {data} with ID: {request_id}")

                        def _response_callback(response):
                            if callback:
                                # Nếu là coroutine thì await, nếu là function thì gọi trực tiếp
                                if asyncio.iscoroutinefunction(callback):
                                    loop.create_task(callback(response))
                                else:
                                    callback(response)
                            if not future.done():
                                future.set_result(response)

                        # Gửi request với ID
                        request_with_id = {**data, "_request_id": request_id}
                        json_request = json.dumps(request_with_id).encode()
                        prefix = len(json_request).to_bytes(4, 'big')
                        print(f"[DEBUG] Sending request: {request_with_id}")
                        self.writer.write(prefix + json_request)
                        await self.writer.drain()
                        
                        # Lưu callback theo ID
                        self._pending_requests[request_id] = _response_callback
                        print(f"[DEBUG] Callback stored with ID: {request_id}, pending count: {len(self._pending_requests)}")
                        
                        # Chờ response
                        response = await future
                        print(f"[DEBUG] Received response for request ID {request_id}: {response}")
                        return response
                    except Exception as e:
                        print(f"❌ Lỗi khi gửi dữ liệu: {e}")
                        await self.disconnect()
                        return None
            
            # Sử dụng wait_for cho Python 3.8 compatibility
            return await asyncio.wait_for(acquire_lock_and_send(), timeout=5.0)
        except asyncio.TimeoutError:
            print(f"[ERROR] Lock timeout for data: {data} - possible deadlock!")
            return None
        except Exception as e:
            print(f"[ERROR] send_json error: {e}")
            return None
    async def listen_loop(self):
        """Lắng nghe phản hồi từ server và gọi callback theo request ID"""
        while self.running and self.reader:
            try:
                length_prefix = await self.reader.readexactly(4)
                response_length = int.from_bytes(length_prefix, 'big')
                if response_length <= 0 or response_length > 10 * 1024 * 1024:
                    print(f"⚠️ Response length không hợp lệ: {response_length}")
                    continue
                response_data = await self.reader.readexactly(response_length)
                try:
                    response = json.loads(response_data.decode())
                    print("📥 Phản hồi từ server:", response)
                    
                    # Lấy request ID từ response
                    request_id = response.get("_request_id")
                    if request_id and request_id in self._pending_requests:
                        # Đây là response cho một request đã gửi
                        print(f"[DEBUG] Found callback for request ID: {request_id}")
                        callback = self._pending_requests.pop(request_id)
                        print(f"[DEBUG] Remaining pending requests: {len(self._pending_requests)}")
                        if callback:
                            # Nếu là coroutine thì await, nếu là function thì gọi trực tiếp
                            if asyncio.iscoroutinefunction(callback):
                                await callback(response)
                            else:
                                callback(response)
                            print(f"[DEBUG] Callback executed successfully for ID: {request_id}")
                    elif not request_id:
                        # Đây là message được server push (không phải response cho request)
                        print(f"[DEBUG] Received pushed message from server: {response}")
                        await self._handle_pushed_message(response)
                    else:
                        print(f"[WARNING] No callback found for request ID: {request_id}")
                        print(f"[DEBUG] Pending request IDs: {list(self._pending_requests.keys())}")
                except json.JSONDecodeError as e:
                    print(f"⚠️ Lỗi parse JSON: {e}. Data: {response_data}")
            except asyncio.IncompleteReadError:
                print("⚠️ Server đóng kết nối.")
                await self.disconnect()
                break
            except Exception as e:
                print(f"❌ Lỗi khi nhận dữ liệu: {e}")
                await self.disconnect()
                break

    async def register(self, username, password, email):
        if not await self.connect():
            return
        request = {
            "action": "register",
            "data": {
                "username": username,
                "password": password,
                "email": email
            }
        }
        response = await self.send_json(request)
        if response and response.get("success"):
            print("✅ Đăng kí thành công.")
            self.start_ping()
        else:
            await self.disconnect()

    async def login(self, username, password):
        if not await self.connect():
            return
        request = {
            "action": "login",
            "data": {
                "username": username,
                "password": password
            }
        }
        response = await self.send_json(request)
        if response and response.get("success"):
            print("✅ Đăng nhập thành công.")
            self.user_id = response.get("user_id")
            self.username = username
            self.start_ping()
            return response
        else:
            await self.disconnect()
            return response

    def start_ping(self):
        # Tạm disable ping để test send_message
        print("[DEBUG] Ping disabled for testing")
        return
        
        async def ping_loop():
            while self.running:
                try:
                    await asyncio.sleep(15)
                    if self.running and self.username:
                        await self.send_json({"action": "ping", "data": {"username": self.username}})
                except Exception as e:
                    print(f"⚠️ Lỗi ping: {e}")
                    break

        if self.ping_task and not self.ping_task.done():
            self.stop_ping()
        self.ping_task = asyncio.create_task(ping_loop())

    def stop_ping(self):
        if self.ping_task and not self.ping_task.done():
            self.ping_task.cancel()
        self.ping_task = None

    def get_user_id(self):
        return self.user_id

    async def get_username(self):
        return self.username

    def is_logged_in(self):
        return self.user_id is not None and self.username is not None

    async def _handle_pushed_message(self, data):
        """Handle server-pushed messages for real-time events"""
        try:
            if not isinstance(data, dict):
                print(f"[DEBUG] Invalid pushed message format: {data}")
                return
                
            action = data.get('action')
            message_data = data.get('data', {})
            
            if action == 'new_message':
                # Real-time message received
                print(f"[DEBUG] New message pushed from server: {message_data}")
                self.new_message_received.emit(message_data)
                
            elif action == 'user_status_change':
                # User online/offline status change
                user_id = message_data.get('user_id')
                status = message_data.get('status')
                if user_id and status:
                    self.user_status_changed.emit(user_id, status)
                    
            else:
                print(f"[DEBUG] Unknown pushed message action: {action}")
                
        except Exception as e:
            print(f"[ERROR] Failed to handle pushed message: {e}")
            print(f"[ERROR] Data: {data}")
