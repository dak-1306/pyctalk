# server/chat_1v1_handler.py
import json
import asyncio
from datetime import datetime


class Chat1v1Handler:
    def __init__(self):
        self.active_chats = {}       # {user1_user2: [client1, client2]}
        self.user_connections = {}   # {username: (reader, writer)}
        self.message_history = {}    # {chat_id: [messages]}

    async def handle_message_request(self, reader, writer, data: dict):
        """Handle different types of message requests"""
        action = data.get("action")

        if action == "send_message":
            return await self.handle_send_message(writer, data.get("data", {}))
        elif action == "get_chat_history":
            return await self.handle_get_history(writer, data.get("data", {}))
        elif action == "mark_as_read":
            return await self.handle_mark_read(writer, data.get("data", {}))
        else:
            return {"success": False, "message": "Unknown action"}

    async def handle_send_message(self, writer, message_data: dict):
        """Handle sending a message from one user to another, lưu vào database"""
        try:
            sender = message_data.get("from")
            recipient = message_data.get("to")
            message_text = message_data.get("message")
            message_type = message_data.get("type", "text")

            if not all([sender, recipient, message_text]):
                return {"success": False, "message": "Missing required fields"}

            # Create chat ID
            chat_id = "_".join(sorted([sender, recipient]))

            # Message object
            now_dt = datetime.now()
            timestamp_str = now_dt.strftime('%Y-%m-%d %H:%M:%S')
            message_obj = {
                "id": f"{chat_id}_{int(asyncio.get_event_loop().time() * 1000)}",
                "from": sender,
                "to": recipient,
                "message": message_text,
                "type": message_type,
                "timestamp": timestamp_str,
                "read": False,
            }

            # Save to history (RAM)
            self.message_history.setdefault(chat_id, []).append(message_obj)

            # Lưu vào database
            try:
                from database.db import db
                # Lấy user_id từ id (client gửi 'from' và 'to' là id)
                sender_row = await db.fetch_one("SELECT id FROM users WHERE id = %s", (sender,))
                recipient_row = await db.fetch_one("SELECT id FROM users WHERE id = %s", (recipient,))
                print(f"[DB] sender_row: {sender_row}, recipient_row: {recipient_row}")
                if sender_row and recipient_row:
                    print(f"[DB] Lưu tin nhắn: sender_id={sender_row['id']}, receiver_id={recipient_row['id']}, content={message_text}, time_send={timestamp_str}")
                    # Insert with message status (unread by default)
                    await db.execute(
                        "INSERT INTO private_messages (sender_id, receiver_id, content, time_send, is_read) VALUES (%s, %s, %s, %s, %s)",
                        (sender_row["id"], recipient_row["id"], message_text, timestamp_str, False)
                    )
                    print(f"[DB] Đã lưu tin nhắn vào DB với trạng thái chưa đọc.")
                else:
                    print(f"[DB] Không tìm thấy user_id cho sender hoặc recipient.")
            except Exception as db_exc:
                print(f"❌ Lỗi lưu tin nhắn vào DB: {db_exc}")

            # Send push message to recipient if online (not sender to avoid duplicate)
            recipient_conn = self.user_connections.get(recipient)
            if recipient_conn:
                _, recipient_writer = recipient_conn
                try:
                    push_message = {
                        "action": "new_message", 
                        "data": message_obj,
                    }
                    # Gửi với length prefix như client expect
                    message_json = json.dumps(push_message)
                    message_bytes = message_json.encode('utf-8')
                    length_prefix = len(message_bytes).to_bytes(4, 'big')
                    
                    recipient_writer.write(length_prefix + message_bytes)
                    await recipient_writer.drain()
                    print(f"[DEBUG] Pushed message to recipient {recipient}")
                except Exception as e:
                    print(f"⚠️ Failed to send message to {recipient}: {e}")

            return {
                "success": True,
                "message": "Message sent successfully",
                "message_id": message_obj["id"],
            }

        except Exception as e:
            return {"success": False, "message": f"Error sending message: {str(e)}"}

    async def handle_get_history(self, writer, request_data: dict):
        """Get chat history between two users"""
        try:
            user1 = request_data.get("user1")
            user2 = request_data.get("user2")
            limit = request_data.get("limit", 50)

            if not all([user1, user2]):
                return {"success": False, "message": "Missing user parameters"}

            # Truy vấn DB để lấy lịch sử tin nhắn giữa user1 và user2 với trạng thái đọc
            from database.db import db
            # Nếu user1/user2 là id, dùng trực tiếp, nếu là username thì cần truy vấn id
            # Ở đây giả sử là id
            query = (
                "SELECT sender_id, receiver_id, content, time_send, is_read, read_at "
                "FROM private_messages "
                "WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s) "
                "ORDER BY time_send DESC LIMIT %s"
            )
            params = (user1, user2, user2, user1, limit)
            rows = await db.fetch_all(query, params)
            messages = []
            for row in rows:
                messages.append({
                    "from": row["sender_id"],
                    "to": row["receiver_id"],
                    "message": row["content"],
                    "timestamp": str(row["time_send"]),
                    "is_read": row["is_read"],
                    "read_at": str(row["read_at"]) if row["read_at"] else None,
                })
            return {
                "success": True,
                "data": {
                    "chat_id": f"{user1}_{user2}",
                    "messages": list(reversed(messages)),  # đảo ngược để hiển thị từ cũ đến mới
                    "total_count": len(messages),
                },
            }
        except Exception as e:
            return {"success": False, "message": f"Error getting history: {str(e)}"}

    async def handle_mark_read(self, writer, request_data: dict):
        """Mark messages as read in database and notify sender"""
        try:
            user_id = request_data.get("user_id")  # Current user who is reading
            sender_id = request_data.get("sender_id")  # Person who sent the messages

            if not all([user_id, sender_id]):
                return {"success": False, "message": "Missing user_id or sender_id"}

            # Update database to mark messages as read
            from database.db import db
            from datetime import datetime
            
            read_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Mark all unread messages from sender_id to user_id as read
            result = await db.execute(
                """UPDATE private_messages 
                   SET is_read = TRUE, read_at = %s 
                   WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE""",
                (read_time, sender_id, user_id)
            )
            
            # Also update in-memory cache
            chat_id = "_".join(sorted([str(user_id), str(sender_id)]))
            if chat_id in self.message_history:
                for message in self.message_history[chat_id]:
                    if message["to"] == str(user_id) and message["from"] == str(sender_id):
                        message["read"] = True

            # Notify sender that their messages have been read
            sender_conn = self.user_connections.get(str(sender_id))
            if sender_conn:
                _, sender_writer = sender_conn
                try:
                    read_notification = {
                        "action": "messages_read",
                        "data": {
                            "reader_id": user_id,
                            "sender_id": sender_id,  # Add sender_id for proper filtering
                            "read_at": read_time
                        }
                    }
                    # Send with length prefix
                    message_json = json.dumps(read_notification)
                    message_bytes = message_json.encode('utf-8')
                    length_prefix = len(message_bytes).to_bytes(4, 'big')
                    
                    sender_writer.write(length_prefix + message_bytes)
                    await sender_writer.drain()
                    print(f"[DEBUG] Notified sender {sender_id} that messages were read by {user_id}")
                except Exception as e:
                    print(f"[ERROR] Failed to notify sender {sender_id}: {e}")

            return {"success": True, "message": "Messages marked as read", "affected_rows": result}

        except Exception as e:
            return {"success": False, "message": f"Error marking as read: {str(e)}"}

    def register_user_connection(self, username: str, user_id: str, writer):
        """Register user connection with session-specific tracking"""
        import time
        session_id = f"{username}_{user_id}_{int(time.time() * 1000)}"  # Add timestamp for uniqueness
        connection_data = (session_id, writer)
        
        # Store with session-specific key to avoid conflicts
        self.user_connections[session_id] = connection_data
        
        # Keep backward compatibility mappings (latest connection wins)
        self.user_connections[username] = connection_data
        self.user_connections[str(user_id)] = connection_data
        
        print(f"✅ User {username} (ID: {user_id}) connected for chat (session: {session_id})")
        print(f"[DEBUG] Total active connections: {len(self.user_connections)}")
        
        return session_id  # Return session ID for cleanup

    def unregister_user_connection(self, username: str, user_id: str = None, session_id: str = None):
        """Unregister user connection - use session_id for precise cleanup"""
        connections_to_remove = []
        
        # If session_id provided, remove that specific session
        if session_id and session_id in self.user_connections:
            connections_to_remove.append(session_id)
            print(f"[DEBUG] Removing specific session: {session_id}")
        else:
            # Fallback to old method - find connections to remove
            if user_id:
                connection_key = f"{username}_{user_id}"
                if connection_key in self.user_connections:
                    connections_to_remove.append(connection_key)
            
            # Remove old-style entries only if no specific session
            if username in self.user_connections:
                connections_to_remove.append(username)
            if user_id and str(user_id) in self.user_connections:
                connections_to_remove.append(str(user_id))
        
        # Clean up connections
        for key in connections_to_remove:
            if key in self.user_connections:
                try:
                    _, writer = self.user_connections[key]
                    if hasattr(writer, 'is_closing') and not writer.is_closing():
                        writer.close()
                        asyncio.create_task(writer.wait_closed())
                except Exception as e:
                    print(f"[WARNING] Error closing writer for {key}: {e}")
                
                del self.user_connections[key]
                print(f"❌ Connection {key} removed from chat")
        
        print(f"[DEBUG] Active connections after cleanup: {len(self.user_connections)} total")

    def get_online_users(self):
        """Get list of currently online users"""
        return list(self.user_connections.keys())

    def get_unread_count(self, username: str) -> int:
        """Get count of unread messages for a user"""
        unread_count = 0
        for chat_id, messages in self.message_history.items():
            for message in messages:
                if message["to"] == username and not message["read"]:
                    unread_count += 1
        return unread_count


# Global instance
chat_handler = Chat1v1Handler()
