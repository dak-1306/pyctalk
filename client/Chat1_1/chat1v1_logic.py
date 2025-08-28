import asyncio
class Chat1v1Logic:
    """Logic xử lý tin nhắn, kết nối API với UI"""
    def __init__(self, ui_window, api_client, current_user_id, friend_id):
        self.ui = ui_window
        self.api_client = api_client
        self.current_user_id = current_user_id
        self.friend_id = friend_id
        self._signal_connected = False
        self._realtime_connected = False

        # kết nối signal UI → logic
        self._connect_signals()
        
        # Connect real-time message signals
        self._connect_realtime_signals()
        
    def _connect_signals(self):
        """Connect UI signals to logic"""
        if not self._signal_connected:
            self.ui.message_send_requested.connect(
                lambda msg: asyncio.create_task(self.send_message(msg))
            )
            self._signal_connected = True
            print(f"[DEBUG][Chat1v1Logic] Signal connected for friend_id={self.friend_id}")
            
    def _connect_realtime_signals(self):
        """Connect real-time message signals from server"""
        if not self._realtime_connected and hasattr(self.api_client, 'client'):
            try:
                # Connect to new message signal
                self.api_client.client.new_message_received.connect(self._on_realtime_message)
                self._realtime_connected = True
                print(f"[DEBUG][Chat1v1Logic] Real-time signals connected for friend_id={self.friend_id}")
            except Exception as e:
                print(f"[ERROR][Chat1v1Logic] Failed to connect real-time signals: {e}")
    
    def _on_realtime_message(self, message_data):
        """Handle real-time message from server"""
        try:
            print(f"[DEBUG][Chat1v1Logic] Real-time message received: {message_data}")
            
            # Check if message is for this chat
            from_user = str(message_data.get('from', ''))
            to_user = str(message_data.get('to', ''))
            current_user_str = str(self.current_user_id)
            friend_str = str(self.friend_id)
            
            # Message is relevant if it's between current user and this friend
            is_relevant = ((from_user == current_user_str and to_user == friend_str) or 
                          (from_user == friend_str and to_user == current_user_str))
            
            # Only add message from others, not own messages (to avoid duplicates)
            is_from_other = str(from_user) != str(self.current_user_id)
            
            if is_relevant and is_from_other:
                # Add message to UI immediately
                content = message_data.get('message', '')
                timestamp = message_data.get('timestamp', '')
                sender_id = message_data.get('from', '')
                
                print(f"[DEBUG][Chat1v1Logic] Adding real-time message from friend to UI: {content}")
                
                # Message is from friend
                sender_name = message_data.get('sender_name', 'Friend')
                
                # Correct parameter order: (message, is_sent, timestamp, sender_name)
                self.ui.add_message(content, False, timestamp, sender_name)
            elif is_relevant and not is_from_other:
                print(f"[DEBUG][Chat1v1Logic] Ignoring own message to avoid duplicate: {message_data.get('message', '')}")
            else:
                print(f"[DEBUG][Chat1v1Logic] Message not relevant for this chat: from={from_user}, to={to_user}")
                
        except Exception as e:
            print(f"[ERROR][Chat1v1Logic] Failed to handle real-time message: {e}")
            import traceback
            traceback.print_exc()
        
    def reconnect_ui_signals(self):
        """Reconnect UI signals when reusing cached chat window"""
        # Disconnect tất cả signal cũ
        try:
            self.ui.message_send_requested.disconnect()
            self._signal_connected = False
            print(f"[DEBUG][Chat1v1Logic] Disconnected old signals for friend_id={self.friend_id}")
        except:
            pass  # Không có connection cũ
            
        # Disconnect real-time signals
        try:
            if hasattr(self.api_client, 'client'):
                self.api_client.client.new_message_received.disconnect(self._on_realtime_message)
                self._realtime_connected = False
                print(f"[DEBUG][Chat1v1Logic] Disconnected old real-time signals for friend_id={self.friend_id}")
        except:
            pass
            
        # Reconnect both
        self._connect_signals()
        self._connect_realtime_signals()

    async def load_message_history(self):
        try:
            print(f"[DEBUG][Chat1v1Logic] Gọi get_chat_history với user_id={self.current_user_id}, friend_id={self.friend_id}")
            resp = await self.api_client.get_chat_history(self.current_user_id, self.friend_id)
            print(f"[DEBUG][Chat1v1Logic] Response lịch sử: {resp}")
            # Phản hồi server có thể là resp['data']['messages']
            messages = []
            if resp:
                if 'messages' in resp:
                    messages = resp['messages']
                elif 'data' in resp and 'messages' in resp['data']:
                    messages = resp['data']['messages']
            
            self.ui.clear_messages()
            
            # If no messages, show friendship message
            if not messages:
                self.ui.add_system_message("🎉 Các bạn đã là bạn bè với nhau! Hãy bắt đầu trò chuyện!")
            else:
                for m in messages:
                    sender_id = int(m.get("user_id") or m.get("from"))
                    content = m.get("message", "")
                    timestamp = m.get("timestamp", None)
                    print(f"[DEBUG][Chat1v1Logic] Thêm message: sender_id={sender_id}, content={content}, timestamp={timestamp}")
                    self.ui.add_message(content, sender_id == self.current_user_id, timestamp)
        except Exception as e:
            print("[ERROR] load_message_history:", e)

    async def send_message(self, text):
        try:
            print(f"[DEBUG][Chat1v1Logic] send_message called: text='{text}', friend_id={self.friend_id}, user_id={self.current_user_id}")
            print(f"[DEBUG][Chat1v1Logic] API client instance: {self.api_client}")
            print(f"[DEBUG][Chat1v1Logic] API client type: {type(self.api_client)}")
            
            # Đảm bảo gọi đúng hàm API client với trường user_id, friend_id, message
            resp = await asyncio.wait_for(
                self.api_client.send_message(self.current_user_id, self.friend_id, text),
                timeout=10.0  # 10 giây timeout
            )
            print(f"[DEBUG][Chat1v1Logic] send_message response: {resp}")
            if resp and resp.get("success"):
                timestamp = None
                if 'data' in resp and 'timestamp' in resp['data']:
                    timestamp = resp['data']['timestamp']
                self.ui.add_message(text, True, timestamp)
                print(f"[DEBUG][Chat1v1Logic] Message added to UI successfully")
            else:
                print(f"[ERROR][Chat1v1Logic] Send message failed: {resp}")
        except asyncio.TimeoutError:
            print(f"[ERROR][Chat1v1Logic] Send message timeout after 10 seconds")
        except Exception as e:
            print("[ERROR] send_message:", e)
            import traceback
            traceback.print_exc()

    def on_receive_message(self, data):
        """callback khi server push tin nhắn"""
        sender = int(data.get("user_id") or data.get("from"))
        message = data.get("message", "")
        timestamp = data.get("timestamp", None)
        if sender == self.friend_id:
            self.ui.add_message(message, False, timestamp)
