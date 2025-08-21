# Correct Messenger Database Integration - Fixed Column Names
import sys
import os
from datetime import datetime

# Add path for database module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from db import MySQLDatabase
except ImportError as e:
    print(f"Warning: Could not import MySQLDatabase: {e}")
    MySQLDatabase = None

class MessengerDatabase:
    """Class xử lý database cho chức năng Messenger với column names đúng"""
    
    def __init__(self):
        if not MySQLDatabase:
            raise Exception("MySQLDatabase module not available")
        
        self.db = MySQLDatabase()
        print("✅ MessengerDatabase initialized successfully")
    
    def get_user_conversations(self, user_id):
        """Lấy danh sách cuộc trò chuyện của user"""
        try:
            # Query với column names đúng từ schema
            query = """
            SELECT DISTINCT
                CASE 
                    WHEN pm.sender_id = %s THEN pm.receiver_id
                    ELSE pm.sender_id
                END as friend_id,
                CASE 
                    WHEN pm.sender_id = %s THEN receiver.username
                    ELSE sender.username
                END as friend_name,
                pm.content as last_message,
                pm.time_send as last_message_time
            FROM private_messages pm
            JOIN users sender ON pm.sender_id = sender.id
            JOIN users receiver ON pm.receiver_id = receiver.id
            WHERE pm.sender_id = %s OR pm.receiver_id = %s
            ORDER BY pm.time_send DESC
            LIMIT 20
            """
            
            result = self.db.fetch_all(query, (user_id, user_id, user_id, user_id))
            
            # Loại bỏ duplicate conversations
            seen_friends = set()
            unique_conversations = []
            
            for row in result:
                friend_id = row['friend_id']
                if friend_id not in seen_friends:
                    seen_friends.add(friend_id)
                    unique_conversations.append({
                        'friend_id': friend_id,
                        'friend_name': row['friend_name'],
                        'last_message': row['last_message'],
                        'last_message_time': row['last_message_time']
                    })
            
            print(f"✅ Found {len(unique_conversations)} conversations for user {user_id}")
            return unique_conversations
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def get_chat_history(self, user_id, friend_id, limit=50):
        """Lấy lịch sử chat giữa 2 user"""
        try:
            query = """
            SELECT 
                message_private_id as id,
                sender_id,
                receiver_id,
                content,
                time_send as timestamp
            FROM private_messages
            WHERE (sender_id = %s AND receiver_id = %s)
               OR (sender_id = %s AND receiver_id = %s)
            ORDER BY time_send ASC
            LIMIT %s
            """
            
            result = self.db.fetch_all(query, (user_id, friend_id, friend_id, user_id, limit))
            
            messages = []
            for msg in result:
                messages.append({
                    'id': msg['id'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp'],
                    'is_sent': msg['sender_id'] == user_id,
                    'sender_id': msg['sender_id'],
                    'receiver_id': msg['receiver_id']
                })
            
            print(f"✅ Retrieved {len(messages)} messages between user {user_id} and {friend_id}")
            return messages
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def send_message(self, sender_id, receiver_id, content):
        """Gửi tin nhắn mới"""
        try:
            query = """
            INSERT INTO private_messages (sender_id, receiver_id, content, time_send)
            VALUES (%s, %s, %s, %s)
            """
            
            timestamp = datetime.now()
            
            # Sử dụng execute cho INSERT
            self.db.execute(query, (sender_id, receiver_id, content, timestamp))
            
            print(f"✅ Message sent from {sender_id} to {receiver_id}: {content[:30]}...")
            return {
                'success': True,
                'timestamp': timestamp,
                'message_id': self.db.cursor.lastrowid if hasattr(self.db.cursor, 'lastrowid') else None
            }
                
        except Exception as e:
            print(f"Error sending message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_friends(self, user_id):
        """Lấy danh sách bạn bè của user"""
        try:
            query = """
            SELECT 
                CASE 
                    WHEN f.user1_id = %s THEN f.user2_id
                    ELSE f.user1_id
                END as friend_id,
                CASE 
                    WHEN f.user1_id = %s THEN u2.username
                    ELSE u1.username
                END as friend_name
            FROM friends f
            JOIN users u1 ON f.user1_id = u1.id
            JOIN users u2 ON f.user2_id = u2.id
            WHERE f.user1_id = %s OR f.user2_id = %s
            ORDER BY friend_name
            """
            
            result = self.db.fetch_all(query, (user_id, user_id, user_id, user_id))
            
            friends = []
            for friend in result:
                friends.append({
                    'friend_id': friend['friend_id'],
                    'friend_name': friend['friend_name']
                })
            
            print(f"✅ Found {len(friends)} friends for user {user_id}")
            return friends
            
        except Exception as e:
            print(f"Error getting friends: {e}")
            return []
    
    # Đã loại bỏ hoàn toàn mock data, chỉ dùng dữ liệu thật từ database
    
    def close(self):
        """Đóng kết nối database"""
        if hasattr(self.db, 'disconnect'):
            self.db.disconnect()

# Test function
def test_messenger_db():
    """Test messenger database functions"""
    try:
        # Khởi tạo
        messenger_db = MessengerDatabase()
        
        print("🧪 Testing Messenger Database...")
        
        # Tạo sample data
        messenger_db.create_sample_data()
        
        # Test get conversations
        print("\n📋 Testing get_user_conversations...")
        conversations = messenger_db.get_user_conversations(1)
        for conv in conversations:
            print(f"  - {conv['friend_name']}: {conv['last_message']}")
        
        # Test get chat history
        print("\n💬 Testing get_chat_history...")
        messages = messenger_db.get_chat_history(1, 2, limit=5)
        for msg in messages:
            sender = "You" if msg['is_sent'] else "Friend"
            print(f"  {sender}: {msg['content']}")
        
        # Test send message
        print("\n📤 Testing send_message...")
        result = messenger_db.send_message(1, 2, "Test message from Python!")
        print(f"  Send result: {result}")
        
        # Test lại conversations sau khi gửi tin nhắn
        print("\n📋 Re-testing get_user_conversations after sending message...")
        conversations = messenger_db.get_user_conversations(1)
        for conv in conversations:
            print(f"  - {conv['friend_name']}: {conv['last_message']}")
        
        # Test get friends
        print("\n👥 Testing get_user_friends...")
        friends = messenger_db.get_user_friends(1)
        for friend in friends:
            print(f"  - {friend['friend_name']} (ID: {friend['friend_id']})")
        
        print("\n🎉 All tests completed successfully!")
        
        # Close connection
        messenger_db.close()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_messenger_db()
