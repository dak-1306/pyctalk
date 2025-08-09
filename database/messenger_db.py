import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db import MySQLDatabase
from datetime import datetime
import hashlib

class MessengerDatabase:
    def __init__(self):
        self.db = MySQLDatabase()
    
    def get_user_conversations(self, user_id):
        """Lấy danh sách cuộc trò chuyện của user (giống Messenger)"""
        try:
            # Lấy các cuộc trò chuyện 1-1 gần nhất
            query = """
            SELECT DISTINCT
                CASE 
                    WHEN pm.sender_id = %s THEN pm.receiver_id
                    ELSE pm.sender_id 
                END as friend_id,
                u.Username as friend_name,
                u.Email as friend_email,
                pm.content as last_message,
                pm.time_send as last_time,
                -- Đếm tin nhắn chưa đọc (giả sử tin nhắn gửi đến user_id chưa đọc)
                (SELECT COUNT(*) FROM private_messages pm2 
                 WHERE pm2.receiver_id = %s 
                 AND CASE WHEN pm.sender_id = %s THEN pm2.sender_id = pm.receiver_id
                         ELSE pm2.sender_id = pm.sender_id END
                 AND pm2.time_send > COALESCE(
                    (SELECT MAX(time_send) FROM private_messages pm3 
                     WHERE pm3.sender_id = %s 
                     AND pm3.receiver_id = CASE WHEN pm.sender_id = %s THEN pm.receiver_id ELSE pm.sender_id END), 
                    '1970-01-01'
                 )) as unread_count
            FROM private_messages pm
            JOIN users u ON u.User_id = CASE 
                WHEN pm.sender_id = %s THEN pm.receiver_id
                ELSE pm.sender_id 
            END
            WHERE pm.sender_id = %s OR pm.receiver_id = %s
            AND pm.message_private_id IN (
                SELECT MAX(pm2.message_private_id)
                FROM private_messages pm2
                WHERE (pm2.sender_id = %s AND pm2.receiver_id = u.User_id)
                   OR (pm2.receiver_id = %s AND pm2.sender_id = u.User_id)
                GROUP BY LEAST(pm2.sender_id, pm2.receiver_id), GREATEST(pm2.sender_id, pm2.receiver_id)
            )
            ORDER BY pm.time_send DESC
            """
            
            self.db.cursor.execute(query, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
            conversations = self.db.cursor.fetchall()
            
            # Format dữ liệu cho UI
            formatted_conversations = []
            for conv in conversations:
                # Tính thời gian hiển thị
                time_display = self.format_time_display(conv['last_time'])
                
                formatted_conversations.append({
                    'name': conv['friend_name'],
                    'last_message': conv['last_message'][:50] + '...' if len(conv['last_message']) > 50 else conv['last_message'],
                    'time': time_display,
                    'unread': int(conv['unread_count']) if conv['unread_count'] else 0,
                    'avatar_color': self.get_avatar_color(conv['friend_name']),
                    'user_id': conv['friend_id']
                })
            
            return formatted_conversations
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def get_chat_history(self, user_id, friend_id, limit=50):
        """Lấy lịch sử chat giữa 2 user"""
        try:
            query = """
            SELECT 
                sender_id,
                receiver_id,
                content,
                time_send
            FROM private_messages 
            WHERE (sender_id = %s AND receiver_id = %s) 
               OR (sender_id = %s AND receiver_id = %s)
            ORDER BY time_send DESC 
            LIMIT %s
            """
            
            self.db.cursor.execute(query, (user_id, friend_id, friend_id, user_id, limit))
            messages = self.db.cursor.fetchall()
            
            # Reverse để hiển thị từ cũ đến mới
            messages.reverse()
            
            # Format cho UI
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    'content': msg['content'],
                    'is_sent': msg['sender_id'] == user_id,
                    'timestamp': msg['time_send'],
                    'time_display': self.format_time_display(msg['time_send'])
                })
            
            return formatted_messages
            
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
            
            current_time = datetime.now()
            self.db.cursor.execute(query, (sender_id, receiver_id, content, current_time))
            self.db.connection.commit()
            
            return {
                'success': True,
                'message_id': self.db.cursor.lastrowid,
                'timestamp': current_time
            }
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_friends(self, user_id):
        """Lấy danh sách bạn bè đã kết bạn"""
        try:
            query = """
            SELECT 
                u.User_id,
                u.Username,
                u.Email
            FROM friends f
            JOIN users u ON (u.User_id = IF(f.user1_id = %s, f.user2_id, f.user1_id))
            WHERE (f.user1_id = %s OR f.user2_id = %s) 
            AND f.status = 'accepted'
            ORDER BY u.Username
            """
            
            self.db.cursor.execute(query, (user_id, user_id, user_id))
            friends = self.db.cursor.fetchall()
            
            return friends
            
        except Exception as e:
            print(f"Error getting friends: {e}")
            return []
    
    def search_users(self, search_term, exclude_user_id=None):
        """Tìm kiếm người dùng theo tên hoặc email"""
        try:
            query = """
            SELECT User_id, Username, Email 
            FROM users 
            WHERE (Username LIKE %s OR Email LIKE %s)
            """
            
            params = [f"%{search_term}%", f"%{search_term}%"]
            
            if exclude_user_id:
                query += " AND User_id != %s"
                params.append(exclude_user_id)
            
            query += " LIMIT 20"
            
            self.db.cursor.execute(query, params)
            users = self.db.cursor.fetchall()
            
            return users
            
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    def get_user_by_id(self, user_id):
        """Lấy thông tin user theo ID"""
        try:
            query = "SELECT User_id, Username, Email FROM users WHERE User_id = %s"
            self.db.cursor.execute(query, (user_id,))
            user = self.db.cursor.fetchone()
            return user
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_username(self, username):
        """Lấy thông tin user theo username"""
        try:
            query = "SELECT User_id, Username, Email FROM users WHERE Username = %s"
            self.db.cursor.execute(query, (username,))
            user = self.db.cursor.fetchone()
            return user
            
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def format_time_display(self, timestamp):
        """Format thời gian hiển thị giống Messenger"""
        if not timestamp:
            return ""
        
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days == 0:
            # Hôm nay
            if diff.seconds < 60:
                return "vừa xong"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} phút"
            else:
                hours = diff.seconds // 3600
                return f"{hours} giờ"
        elif diff.days == 1:
            return "Hôm qua"
        elif diff.days < 7:
            return f"{diff.days} ngày"
        else:
            return timestamp.strftime("%d/%m")
    
    def get_avatar_color(self, name):
        """Tạo màu avatar dựa trên tên"""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD',
            '#00D2D3', '#FF9F43', '#10AC84', '#EE5A52'
        ]
        
        # Hash tên để chọn màu consistent
        hash_value = hash(name) % len(colors)
        return colors[hash_value]
    
    def create_sample_messages(self, user_id=1):
        """Tạo dữ liệu tin nhắn mẫu cho test"""
        try:
            # Tạo tin nhắn mẫu với các user khác
            sample_messages = [
                (user_id, 2, "Chào bạn! Hôm nay thế nào?"),
                (2, user_id, "Mình khỏe, cảm ơn bạn!"),
                (user_id, 2, "Có dự định gì cuối tuần không?"),
                
                (3, user_id, "Ok, mai mình gặp nhau nhé"),
                (user_id, 3, "Được rồi, hẹn gặp lại!"),
                
                (user_id, 4, "Cảm ơn bạn nhiều! 👍"),
                (4, user_id, "Không có gì, luôn sẵn sàng giúp đỡ"),
                
                (5, user_id, "Bạn đã xem tin nhắn chưa?"),
                (6, user_id, "Meeting lúc 3h chiều nhé"),
                (user_id, 6, "OK, mình sẽ có mặt đúng giờ"),
                
                (user_id, 7, "Chúc bạn ngủ ngon! 😴"),
            ]
            
            for sender, receiver, content in sample_messages:
                query = """
                INSERT INTO private_messages (sender_id, receiver_id, content, time_send)
                VALUES (%s, %s, %s, %s)
                """
                # Tạo thời gian random trong vài ngày qua
                import random
                from datetime import timedelta
                time_offset = timedelta(
                    days=random.randint(0, 3),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                timestamp = datetime.now() - time_offset
                
                self.db.cursor.execute(query, (sender, receiver, content, timestamp))
            
            self.db.connection.commit()
            print("✅ Đã tạo dữ liệu tin nhắn mẫu")
            
        except Exception as e:
            print(f"Error creating sample messages: {e}")
    
    def close(self):
        """Đóng kết nối database"""
        if self.db.connection:
            self.db.connection.close()

# Test function
if __name__ == "__main__":
    messenger_db = MessengerDatabase()
    
    # Tạo dữ liệu mẫu
    messenger_db.create_sample_messages()
    
    # Test lấy conversations
    conversations = messenger_db.get_user_conversations(1)
    print("Conversations:", conversations)
    
    # Test lấy chat history
    history = messenger_db.get_chat_history(1, 2)
    print("Chat history:", history)
