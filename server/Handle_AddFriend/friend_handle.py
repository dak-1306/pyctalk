import json
import os
from database.db import db

class FriendHandler:
    def __init__(self):
        self.db = db
        
    def get_suggestions(self, username):
        """Lấy danh sách gợi ý kết bạn"""
        try:
            # Lấy user_id từ username
            user_query = "SELECT id FROM users WHERE username = %s"
            user_result = self.db.fetch_one(user_query, (username,))
            
            if not user_result:
                return {"status": "error", "message": "User not found"}
            
            user_id = user_result['id']
            
            # Lấy danh sách user khác (không phải bạn bè hiện tại)
            suggestions_query = """
                SELECT u.username 
                FROM users u 
                WHERE u.id != %s 
                AND u.id NOT IN (
                    SELECT CASE 
                        WHEN user1_id = %s THEN user2_id 
                        ELSE user1_id 
                    END 
                    FROM friends 
                    WHERE (user1_id = %s OR user2_id = %s) 
                    AND status = 'accepted'
                )
                AND u.id NOT IN (
                    SELECT CASE 
                        WHEN from_user_id = %s THEN to_user_id 
                        ELSE from_user_id 
                    END 
                    FROM friend_requests 
                    WHERE (from_user_id = %s OR to_user_id = %s) 
                    AND status = 'pending'
                )
                LIMIT 10
            """
            
            suggestions = self.db.fetch_all(suggestions_query, (
                user_id, user_id, user_id, user_id, user_id, user_id, user_id
            ))
            
            suggestion_list = [s['username'] for s in suggestions]
            
            return {"status": "ok", "data": suggestion_list}
            
        except Exception as e:
            print(f"❌ Lỗi get_suggestions: {e}")
            return {"status": "error", "message": str(e)}
    
    def add_friend(self, from_user, to_user):
        """Gửi lời mời kết bạn"""
        try:
            # Lấy user_id
            from_user_query = "SELECT id FROM users WHERE username = %s"
            to_user_query = "SELECT id FROM users WHERE username = %s"
            
            from_result = self.db.fetch_one(from_user_query, (from_user,))
            to_result = self.db.fetch_one(to_user_query, (to_user,))
            
            if not from_result or not to_result:
                return {"status": "error", "message": "User not found"}
            
            from_user_id = from_result['id']
            to_user_id = to_result['id']
            
            # Kiểm tra xem đã là bạn bè chưa
            friend_check_query = """
                SELECT * FROM friends 
                WHERE ((user1_id = %s AND user2_id = %s) OR (user1_id = %s AND user2_id = %s))
                AND status = 'accepted'
            """
            existing_friend = self.db.fetch_one(friend_check_query, (from_user_id, to_user_id, to_user_id, from_user_id))
            
            if existing_friend:
                return {"status": "error", "message": "Already friends"}
            
            # Kiểm tra xem đã gửi lời mời chưa
            request_check_query = """
                SELECT * FROM friend_requests 
                WHERE ((from_user_id = %s AND to_user_id = %s) OR (from_user_id = %s AND to_user_id = %s))
                AND status = 'pending'
            """
            existing_request = self.db.fetch_one(request_check_query, (from_user_id, to_user_id, to_user_id, from_user_id))
            
            if existing_request:
                return {"status": "error", "message": "Request already sent"}
            
            # Tạo lời mời kết bạn
            insert_query = """
                INSERT INTO friend_requests (from_user_id, to_user_id, status, created_at)
                VALUES (%s, %s, 'pending', NOW())
            """
            self.db.execute(insert_query, (from_user_id, to_user_id))
            
            return {"status": "ok", "message": f"Friend request sent from {from_user} to {to_user}"}
            
        except Exception as e:
            print(f"❌ Lỗi add_friend: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_friends(self, username):
        """Lấy danh sách bạn bè"""
        try:
            # Lấy user_id
            user_query = "SELECT id FROM users WHERE username = %s"
            user_result = self.db.fetch_one(user_query, (username,))
            
            if not user_result:
                return {"status": "error", "message": "User not found"}
            
            user_id = user_result['id']
            
            # Lấy danh sách bạn bè
            friends_query = """
                SELECT u.username 
                FROM users u
                JOIN friends f ON (
                    (f.user1_id = %s AND f.user2_id = u.id) OR 
                    (f.user2_id = %s AND f.user1_id = u.id)
                )
                WHERE f.status = 'accepted' AND u.id != %s
            """
            
            friends = self.db.fetch_all(friends_query, (user_id, user_id, user_id))
            friend_list = [f['username'] for f in friends]
            
            return {"status": "ok", "data": friend_list}
            
        except Exception as e:
            print(f"❌ Lỗi get_friends: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_friend_requests(self, username):
        """Lấy lời mời kết bạn"""
        try:
            # Lấy user_id
            user_query = "SELECT id FROM users WHERE username = %s"
            user_result = self.db.fetch_one(user_query, (username,))
            
            if not user_result:
                return {"status": "error", "message": "User not found"}
            
            user_id = user_result['id']
            
            # Lấy lời mời kết bạn
            requests_query = """
                SELECT u.username as from_username
                FROM friend_requests fr
                JOIN users u ON fr.from_user_id = u.id
                WHERE fr.to_user_id = %s AND fr.status = 'pending'
            """
            
            requests = self.db.fetch_all(requests_query, (user_id,))
            request_list = [r['from_username'] for r in requests]
            
            return {"status": "ok", "data": request_list}
            
        except Exception as e:
            print(f"❌ Lỗi get_friend_requests: {e}")
            return {"status": "error", "message": str(e)}
    
    def accept_friend(self, username, from_user):
        """Chấp nhận lời mời kết bạn"""
        try:
            # Lấy user_id
            user_query = "SELECT id FROM users WHERE username = %s"
            from_query = "SELECT id FROM users WHERE username = %s"
            
            user_result = self.db.fetch_one(user_query, (username,))
            from_result = self.db.fetch_one(from_query, (from_user,))
            
            if not user_result or not from_result:
                return {"status": "error", "message": "User not found"}
            
            user_id = user_result['id']
            from_user_id = from_result['id']
            
            # Cập nhật status của friend_request thành accepted
            update_request_query = """
                UPDATE friend_requests 
                SET status = 'accepted' 
                WHERE from_user_id = %s AND to_user_id = %s AND status = 'pending'
            """
            self.db.execute(update_request_query, (from_user_id, user_id))
            
            # Thêm vào bảng friends
            insert_friend_query = """
                INSERT INTO friends (user1_id, user2_id, status, created_at)
                VALUES (%s, %s, 'accepted', NOW())
            """
            self.db.execute(insert_friend_query, (min(from_user_id, user_id), max(from_user_id, user_id)))
            
            return {"status": "ok", "message": f"Friend request accepted"}
            
        except Exception as e:
            print(f"❌ Lỗi accept_friend: {e}")
            return {"status": "error", "message": str(e)}
    
    def reject_friend(self, username, from_user):
        """Từ chối lời mời kết bạn"""
        try:
            # Lấy user_id
            user_query = "SELECT id FROM users WHERE username = %s"
            from_query = "SELECT id FROM users WHERE username = %s"
            
            user_result = self.db.fetch_one(user_query, (username,))
            from_result = self.db.fetch_one(from_query, (from_user,))
            
            if not user_result or not from_result:
                return {"status": "error", "message": "User not found"}
            
            user_id = user_result['id']
            from_user_id = from_result['id']
            
            # Cập nhật status của friend_request thành rejected
            update_request_query = """
                UPDATE friend_requests 
                SET status = 'rejected' 
                WHERE from_user_id = %s AND to_user_id = %s AND status = 'pending'
            """
            self.db.execute(update_request_query, (from_user_id, user_id))
            
            return {"status": "ok", "message": f"Friend request rejected"}
            
        except Exception as e:
            print(f"❌ Lỗi reject_friend: {e}")
            return {"status": "error", "message": str(e)}
    
    def remove_friend(self, username, friend_name):
        """Xóa bạn bè"""
        try:
            # Lấy user_id
            user_query = "SELECT id FROM users WHERE username = %s"
            friend_query = "SELECT id FROM users WHERE username = %s"
            
            user_result = self.db.fetch_one(user_query, (username,))
            friend_result = self.db.fetch_one(friend_query, (friend_name,))
            
            if not user_result or not friend_result:
                return {"status": "error", "message": "User not found"}
            
            user_id = user_result['id']
            friend_id = friend_result['id']
            
            # Xóa từ bảng friends
            delete_friend_query = """
                DELETE FROM friends 
                WHERE ((user1_id = %s AND user2_id = %s) OR (user1_id = %s AND user2_id = %s))
                AND status = 'accepted'
            """
            self.db.execute(delete_friend_query, (user_id, friend_id, friend_id, user_id))
            
            return {"status": "ok", "message": f"Friend removed"}
            
        except Exception as e:
            print(f"❌ Lỗi remove_friend: {e}")
            return {"status": "error", "message": str(e)}

# Tạo instance để sử dụng
friend_handler = FriendHandler()
