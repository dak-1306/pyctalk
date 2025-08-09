import json
import threading
import time
from datetime import datetime

class Chat1v1Handler:
    def __init__(self):
        self.active_chats = {}  # {user1_user2: [client1, client2]}
        self.user_connections = {}  # {username: client_socket}
        self.message_history = {}  # {chat_id: [messages]}
    
    def handle_message_request(self, client_socket, data):
        """Handle different types of message requests"""
        action = data.get("action")
        
        if action == "send_message":
            return self.handle_send_message(client_socket, data.get("data", {}))
        elif action == "get_chat_history":
            return self.handle_get_history(client_socket, data.get("data", {}))
        elif action == "mark_as_read":
            return self.handle_mark_read(client_socket, data.get("data", {}))
        else:
            return {"success": False, "message": "Unknown action"}
    
    def handle_send_message(self, client_socket, message_data):
        """Handle sending a message from one user to another"""
        try:
            sender = message_data.get("from")
            recipient = message_data.get("to") 
            message_text = message_data.get("message")
            message_type = message_data.get("type", "text")
            
            if not all([sender, recipient, message_text]):
                return {"success": False, "message": "Missing required fields"}
            
            # Create chat ID (sorted to ensure consistency)
            chat_id = "_".join(sorted([sender, recipient]))
            
            # Create message object
            message_obj = {
                "id": f"{chat_id}_{int(time.time()*1000)}",
                "from": sender,
                "to": recipient,
                "message": message_text,
                "type": message_type,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            # Store message in history
            if chat_id not in self.message_history:
                self.message_history[chat_id] = []
            self.message_history[chat_id].append(message_obj)
            
            # Send to recipient if online
            recipient_socket = self.user_connections.get(recipient)
            if recipient_socket:
                try:
                    response = {
                        "action": "receive_message",
                        "data": message_obj
                    }
                    recipient_socket.send(json.dumps(response).encode('utf-8'))
                except Exception as e:
                    print(f"Failed to send message to {recipient}: {e}")
            
            return {
                "success": True,
                "message": "Message sent successfully",
                "message_id": message_obj["id"]
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error sending message: {str(e)}"}
    
    def handle_get_history(self, client_socket, request_data):
        """Get chat history between two users"""
        try:
            user1 = request_data.get("user1")
            user2 = request_data.get("user2")
            limit = request_data.get("limit", 50)
            
            if not all([user1, user2]):
                return {"success": False, "message": "Missing user parameters"}
            
            # Create chat ID
            chat_id = "_".join(sorted([user1, user2]))
            
            # Get messages
            messages = self.message_history.get(chat_id, [])
            
            # Return last N messages
            recent_messages = messages[-limit:] if len(messages) > limit else messages
            
            return {
                "success": True,
                "data": {
                    "chat_id": chat_id,
                    "messages": recent_messages,
                    "total_count": len(messages)
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error getting history: {str(e)}"}
    
    def handle_mark_read(self, client_socket, request_data):
        """Mark messages as read"""
        try:
            user = request_data.get("user")
            chat_partner = request_data.get("chat_partner")
            
            if not all([user, chat_partner]):
                return {"success": False, "message": "Missing parameters"}
            
            chat_id = "_".join(sorted([user, chat_partner]))
            
            if chat_id in self.message_history:
                # Mark all messages from chat_partner as read
                for message in self.message_history[chat_id]:
                    if message["to"] == user and message["from"] == chat_partner:
                        message["read"] = True
            
            return {"success": True, "message": "Messages marked as read"}
            
        except Exception as e:
            return {"success": False, "message": f"Error marking as read: {str(e)}"}
    
    def register_user_connection(self, username, client_socket):
        """Register user connection for real-time messaging"""
        self.user_connections[username] = client_socket
        print(f"User {username} connected for chat")
    
    def unregister_user_connection(self, username):
        """Unregister user connection"""
        if username in self.user_connections:
            del self.user_connections[username]
            print(f"User {username} disconnected from chat")
    
    def get_online_users(self):
        """Get list of currently online users"""
        return list(self.user_connections.keys())
    
    def get_unread_count(self, username):
        """Get count of unread messages for a user"""
        unread_count = 0
        
        for chat_id, messages in self.message_history.items():
            for message in messages:
                if message["to"] == username and not message["read"]:
                    unread_count += 1
        
        return unread_count

# Global instance to be used by the server
chat_handler = Chat1v1Handler()
