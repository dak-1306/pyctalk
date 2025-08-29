import asyncio
from PyQt6.QtCore import QObject, pyqtSignal

class Chat1v1Logic(QObject):
    """Logic xử lý tin nhắn, kết nối API với UI"""
    
    # Signal for when messages are marked as read
    messages_read = pyqtSignal(dict)
    
    def __init__(self, ui_window, api_client, current_user_id, friend_id):
        super().__init__()
        self.ui = ui_window
        self.api_client = api_client
        self.current_user_id = current_user_id
        self.friend_id = friend_id
        self._signal_connected = False
        self._realtime_connected = False

        # Lazy loading settings
        self.messages_per_load = 15  # Load 15 messages at a time
        self.total_messages_loaded = 0
        self.has_more_messages = True
        self.is_loading_more = False
        self.loading_lock = asyncio.Lock()

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
                # Connect to messages read signal
                self.api_client.client.messages_read.connect(self._on_messages_read)
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
                
                # Mark this new message as read since user has chat window open
                # Use asyncio to run the async function
                import asyncio
                asyncio.create_task(self.api_client.mark_message_as_read(self.friend_id, self.current_user_id))
                print(f"[DEBUG][Chat1v1Logic] Scheduled mark as read for friend {self.friend_id}")
                
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
                self.api_client.client.messages_read.disconnect(self._on_messages_read)
                self._realtime_connected = False
                print(f"[DEBUG][Chat1v1Logic] Disconnected old real-time signals for friend_id={self.friend_id}")
        except:
            pass
            
        # Reconnect both
        self._connect_signals()
        self._connect_realtime_signals()

    async def load_message_history(self):
        """Load initial messages with lazy loading and spinner"""
        try:
            # Show loading spinner
            if hasattr(self.ui, 'show_loading_spinner'):
                self.ui.show_loading_spinner("Đang tải tin nhắn...")
            
            print(f"[DEBUG][Chat1v1Logic] Loading initial {self.messages_per_load} messages...")
            
            # Load with limit for lazy loading
            resp = await self.api_client.get_chat_history(
                self.current_user_id, 
                self.friend_id, 
                limit=self.messages_per_load
            )
            
            print(f"[DEBUG][Chat1v1Logic] Response lịch sử: {resp}")
            
            # Parse messages
            messages = []
            total_count = 0
            if resp:
                if 'messages' in resp:
                    messages = resp['messages']
                    total_count = resp.get('total_count', len(messages))
                elif 'data' in resp and 'messages' in resp['data']:
                    messages = resp['data']['messages']
                    total_count = resp['data'].get('total_count', len(messages))
            
            # Update lazy loading state
            self.total_messages_loaded = len(messages)
            
            # Determine if there are more messages
            # If we got fewer messages than requested, there are no more
            # If total_count is available and accurate, use it
            if len(messages) < self.messages_per_load:
                self.has_more_messages = False
            elif total_count > 0:
                self.has_more_messages = self.total_messages_loaded < total_count
            else:
                # Fallback: assume there might be more if we got exactly the requested amount
                self.has_more_messages = len(messages) == self.messages_per_load
            
            print(f"[DEBUG][Chat1v1Logic] Initial load: loaded={len(messages)}, total_loaded={self.total_messages_loaded}, total_count={total_count}, has_more={self.has_more_messages}")
            
            # Clear UI and show messages with batch animation
            self.ui.clear_messages()
            
            # Hide loading spinner
            if hasattr(self.ui, 'hide_loading_spinner'):
                self.ui.hide_loading_spinner()
            
            # If no messages, show friendship message
            if not messages:
                self.ui.add_system_message("🎉 Các bạn đã là bạn bè với nhau! Hãy bắt đầu trò chuyện!")
            else:
                # Add messages with batch animation (reverse order for chat history)
                await self._animate_initial_messages(messages)
            
            # Set up scroll detection for lazy loading
            if hasattr(self.ui, 'setup_scroll_loading'):
                self.ui.setup_scroll_loading(self._load_more_messages)
            
            # Only mark messages as read if there are unread messages from friend
            has_unread_from_friend = any(
                not m.get("is_read", False) and int(m.get("user_id") or m.get("from")) == self.friend_id 
                for m in messages
            )
            if has_unread_from_friend:
                await self.api_client.mark_message_as_read(self.friend_id, self.current_user_id)
                print(f"[DEBUG][Chat1v1Logic] Marked unread messages from friend {self.friend_id} as read")
                    
        except Exception as e:
            # Hide loading spinner on error
            if hasattr(self.ui, 'hide_loading_spinner'):
                self.ui.hide_loading_spinner()
            print("[ERROR] load_message_history:", e)

    async def _animate_initial_messages(self, messages):
        """Animate loading of initial messages"""
        batch_size = 3  # Load 3 messages at a time
        delay_between_batches = 100  # 100ms delay
        
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            
            for m in batch:
                sender_id = int(m.get("user_id") or m.get("from"))
                content = m.get("message", "")
                timestamp = m.get("timestamp", None)
                is_read = m.get("is_read", None)
                
                # For sent messages, pass read status; for received messages, don't show status
                message_is_read = is_read if sender_id == self.current_user_id else None
                self.ui.add_message(content, sender_id == self.current_user_id, timestamp, None, message_is_read)
            
            # Small delay between batches for smooth effect
            if i + batch_size < len(messages):
                await asyncio.sleep(delay_between_batches / 1000.0)

    async def _load_more_messages(self):
        """Load more older messages when scrolling to top"""
        async with self.loading_lock:
            if self.is_loading_more or not self.has_more_messages:
                print(f"[DEBUG][Chat1v1Logic] Skipping load more: is_loading={self.is_loading_more}, has_more={self.has_more_messages}")
                return
                
            self.is_loading_more = True
            print(f"[DEBUG][Chat1v1Logic] Loading more messages, offset={self.total_messages_loaded}")
            
            try:
                # Show loading indicator
                if hasattr(self.ui, 'show_loading_bar'):
                    self.ui.show_loading_bar()
                
                print(f"[DEBUG][Chat1v1Logic] Calling get_chat_history with user1={self.current_user_id}, user2={self.friend_id}, limit={self.messages_per_load}, offset={self.total_messages_loaded}")
                
                # Load more messages with offset
                resp = await self.api_client.get_chat_history(
                    self.current_user_id,
                    self.friend_id,
                    limit=self.messages_per_load,
                    offset=self.total_messages_loaded
                )
                
                print(f"[DEBUG][Chat1v1Logic] Server response: {resp}")
                
                if resp:
                    messages = []
                    total_count = 0
                    if 'messages' in resp:
                        messages = resp['messages']
                        total_count = resp.get('total_count', 0)
                    elif 'data' in resp and 'messages' in resp['data']:
                        messages = resp['data']['messages']
                        total_count = resp['data'].get('total_count', 0)
                    
                    print(f"[DEBUG][Chat1v1Logic] Extracted {len(messages)} messages from response, total_count={total_count}")
                    
                    if messages:
                        # Prepend older messages to UI
                        if hasattr(self.ui, 'prepend_messages'):
                            print(f"[DEBUG][Chat1v1Logic] Calling prepend_messages with {len(messages)} messages")
                            self.ui.prepend_messages(messages)
                        
                        self.total_messages_loaded += len(messages)
                        
                        # Determine if there are more messages
                        if len(messages) < self.messages_per_load:
                            self.has_more_messages = False
                        elif total_count > 0:
                            self.has_more_messages = self.total_messages_loaded < total_count
                        else:
                            # Fallback: assume there might be more if we got exactly the requested amount
                            self.has_more_messages = len(messages) == self.messages_per_load
                        
                        print(f"[DEBUG][Chat1v1Logic] Loaded {len(messages)} more messages, total={self.total_messages_loaded}, total_count={total_count}, has_more={self.has_more_messages}")
                    else:
                        self.has_more_messages = False
                        print(f"[DEBUG][Chat1v1Logic] No more messages to load")
                else:
                    print(f"[DEBUG][Chat1v1Logic] No response from server")
                        
            except Exception as e:
                print(f"[ERROR][Chat1v1Logic] Failed to load more messages: {e}")
                import traceback
                traceback.print_exc()
            finally:
                self.is_loading_more = False
                # Hide loading indicator
                if hasattr(self.ui, 'hide_loading_bar'):
                    self.ui.hide_loading_bar()

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
                # Add message with "sent" status (False = sent but not read)
                self.ui.add_message(text, True, timestamp, None, False)
                print(f"[DEBUG][Chat1v1Logic] Message added to UI successfully with 'sent' status")
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

    def _on_messages_read(self, read_data):
        """Handle when messages are marked as read"""
        try:
            print(f"[DEBUG][Chat1v1Logic] Received messages read notification: {read_data}")
            
            # Check if read notification is for this chat
            reader_id = read_data.get('reader_id')
            sender_id = read_data.get('sender_id') 
            
            # If friend read our messages, update UI to show "Đã xem"
            if (reader_id == self.friend_id and sender_id == self.current_user_id):
                print(f"[DEBUG][Chat1v1Logic] Friend {self.friend_id} read our messages")
                # Update all unread messages from us to show as read
                self.ui.update_messages_read_status()
                
        except Exception as e:
            print(f"[ERROR][Chat1v1Logic] Error handling messages read: {e}")
