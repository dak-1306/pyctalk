# Fixed Messenger Database Integration
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
    """Class xử lý database cho chức năng Messenger"""
    
    def __init__(self):
        if not MySQLDatabase:
            raise Exception("MySQLDatabase module not available")
        
        self.db = MySQLDatabase()
        print("✅ MessengerDatabase initialized successfully")
    
    def get_user_conversations(self, user_id):
        """Lấy danh sách cuộc trò chuyện của user"""
        try:
            # Query đơn giản để lấy conversations
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
                pm.timestamp as last_message_time
            FROM private_messages pm
            JOIN users sender ON pm.sender_id = sender.id
            JOIN users receiver ON pm.receiver_id = receiver.id
            WHERE pm.sender_id = %s OR pm.receiver_id = %s
            ORDER BY pm.timestamp DESC
            LIMIT 20
            """
            
            result = self.db.execute_query(query, (user_id, user_id, user_id, user_id))
            
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
                id,
                sender_id,
                receiver_id,
                content,
                timestamp
            FROM private_messages
            WHERE (sender_id = %s AND receiver_id = %s)
               OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
            LIMIT %s
            """
            
            result = self.db.execute_query(query, (user_id, friend_id, friend_id, user_id, limit))
            
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
            INSERT INTO private_messages (sender_id, receiver_id, content, timestamp)
            VALUES (%s, %s, %s, %s)
            """
            
            timestamp = datetime.now()
            
            result = self.db.execute_query(query, (sender_id, receiver_id, content, timestamp))
            
            if result is not None:  # Query thành công
                print(f"✅ Message sent from {sender_id} to {receiver_id}: {content[:30]}...")
                return {
                    'success': True,
                    'timestamp': timestamp,
                    'message_id': self.db.cursor.lastrowid if hasattr(self.db.cursor, 'lastrowid') else None
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to insert message'
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
            
            result = self.db.execute_query(query, (user_id, user_id, user_id, user_id))
            
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
    
    def create_sample_data(self):
        """Tạo dữ liệu mẫu để test"""
        try:
            print("🔧 Creating sample data...")
            
            # Tạo users mẫu
            users = [
                ('nguyenvana', 'hashed_password_1', 'a@example.com'),
                ('tranthib', 'hashed_password_2', 'b@example.com'),
                ('levanc', 'hashed_password_3', 'c@example.com'),
                ('phamthid', 'hashed_password_4', 'd@example.com'),
                ('hoangvane', 'hashed_password_5', 'e@example.com')
            ]
            
            for username, password, email in users:
                query = "INSERT IGNORE INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
                self.db.execute_query(query, (username, password, email))
            
            print("✅ Sample users created")
            
            # Tạo friendships
            friendships = [
                (1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)
            ]
            
            for user1, user2 in friendships:
                # Đảm bảo user1 < user2
                if user1 > user2:
                    user1, user2 = user2, user1
                
                query = "INSERT IGNORE INTO friends (user1_id, user2_id) VALUES (%s, %s)"
                self.db.execute_query(query, (user1, user2))
            
            print("✅ Sample friendships created")
            
            # Tạo tin nhắn mẫu
            sample_messages = [
                (1, 2, "Chào bạn! Bạn có khỏe không?"),
                (2, 1, "Chào! Mình khỏe, cảm ơn bạn. Còn bạn thì sao?"),
                (1, 2, "Mình cũng ổn. Project PycTalk tiến triển như thế nào rồi?"),
                (2, 1, "Đang làm giao diện chat giống Messenger đây! 😊"),
                (1, 2, "Wow nghe hay đấy! Khi nào demo được?"),
                (1, 3, "Hôm nay có họp không?"),
                (3, 1, "Có, 2h chiều nhé!"),
                (1, 4, "Cảm ơn bạn về tài liệu!"),
                (4, 1, "Không có gì, chúc bạn học tốt!"),
                (2, 5, "Cuối tuần đi chơi không?"),
                (5, 2, "OK, chúng ta đi đâu?"),
            ]
            
            for sender, receiver, content in sample_messages:
                query = """
                INSERT INTO private_messages (sender_id, receiver_id, content, timestamp)
                VALUES (%s, %s, %s, NOW())
                """
                self.db.execute_query(query, (sender, receiver, content))
            
            print("✅ Sample messages created")
            print("🎉 Sample data creation completed!")
            
            return True
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            return False
    
    def close(self):
        """Đóng kết nối database"""
        if hasattr(self.db, 'close'):
            self.db.close()

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
