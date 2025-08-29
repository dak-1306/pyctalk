class Chat1v1APIClient:
    """API client cho chat 1-1 (gọi server qua pyctalk_client)"""
    def __init__(self, pyctalk_client):
        self.client = pyctalk_client

    async def get_chat_history(self, user_id, friend_id, limit=50, offset=0):
        return await self.client.send_request("get_chat_history", {
            "user1": user_id,
            "user2": friend_id,
            "limit": limit,
            "offset": offset
        })

    async def send_message(self, user_id, friend_id, content):
        print(f"[DEBUG][Chat1v1APIClient] send_message called: user_id={user_id}, friend_id={friend_id}, content='{content}'")
        try:
            response = await self.client.send_request("send_message", {
                "from": user_id,
                "to": friend_id,
                "message": content
            })
            print(f"[DEBUG][Chat1v1APIClient] send_message response: {response}")
            return response
        except Exception as e:
            print(f"[ERROR][Chat1v1APIClient] send_message error: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    async def send_file_message(self, user_id, friend_id, file_metadata, caption=""):
        """Send file message with metadata"""
        print(f"[DEBUG][Chat1v1APIClient] send_file_message called: user_id={user_id}, friend_id={friend_id}")
        try:
            # Prepare message data
            message_data = {
                "from": user_id,
                "to": friend_id,
                "message_type": file_metadata['message_type'],
                "content": caption,
                "file_path": file_metadata['file_path'],
                "file_name": file_metadata['file_name'],
                "file_size": file_metadata['file_size'],
                "mime_type": file_metadata['mime_type'],
                "thumbnail_path": file_metadata.get('thumbnail_path')
            }
            
            response = await self.client.send_request("send_file_message", message_data)
            print(f"[DEBUG][Chat1v1APIClient] send_file_message response: {response}")
            return response
        except Exception as e:
            print(f"[ERROR][Chat1v1APIClient] send_file_message error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def mark_message_as_read(self, friend_id, current_user_id=None):
        """Mark messages from friend as read"""
        try:
            # Use provided current_user_id or try to get from client
            user_id = current_user_id or getattr(self.client, 'current_user_id', None)
            if not user_id:
                print(f"[ERROR][Chat1v1APIClient] Current user ID not found")
                return None
                
            response = await self.client.send_request("mark_as_read", {
                "user_id": user_id,      # Who is reading the messages
                "sender_id": friend_id   # Who sent the messages
            })
            print(f"[DEBUG][Chat1v1APIClient] mark_message_as_read response: {response}")
            return response
        except Exception as e:
            print(f"[ERROR][Chat1v1APIClient] mark_message_as_read error: {e}")
            return None
