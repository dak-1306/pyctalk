from database.db import db
from datetime import datetime

class GroupHandler:
    def __init__(self):
        pass
    
    def create_group(self, group_name: str, created_by: int) -> dict:
        """Tạo nhóm chat mới"""
        try:
            # Tạo nhóm
            db.execute(
                "INSERT INTO group_chat (group_name, created_by) VALUES (%s, %s)",
                (group_name, created_by)
            )
            
            # Lấy ID nhóm vừa tạo
            result = db.fetch_one("SELECT LAST_INSERT_ID() as group_id")
            group_id = result["group_id"]
            
            # Thêm người tạo vào nhóm
            db.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, created_by)
            )
            
            return {
                "success": True, 
                "message": f"Tạo nhóm '{group_name}' thành công",
                "group_id": group_id
            }
            
        except Exception as e:
            return {"success": False, "message": f"Lỗi tạo nhóm: {str(e)}"}

    def add_member_to_group(self, group_id: int, user_id: int, added_by: int) -> dict:
        """Thêm thành viên vào nhóm"""
        try:
            # Kiểm tra người thêm có phải thành viên nhóm không
            check_member = db.fetch_one(
                "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, added_by)
            )
            if not check_member:
                return {"success": False, "message": "Bạn không phải thành viên của nhóm này"}
            
            # Kiểm tra user có tồn tại không
            user_exists = db.fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
            if not user_exists:
                return {"success": False, "message": "Người dùng không tồn tại"}
            
            # Kiểm tra đã là thành viên chưa
            already_member = db.fetch_one(
                "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, user_id)
            )
            if already_member:
                return {"success": False, "message": "Người dùng đã là thành viên của nhóm"}
            
            # Thêm thành viên
            db.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, user_id)
            )
            
            # Lấy thông tin người dùng vừa thêm
            user_info = db.fetch_one(
                "SELECT username FROM users WHERE id = %s", 
                (user_id,)
            )
            
            return {
                "success": True,
                "message": f"Đã thêm {user_info['username']} vào nhóm"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Lỗi thêm thành viên: {str(e)}"}

    def send_group_message(self, sender_id: int, group_id: int, content: str) -> dict:
        """Gửi tin nhắn nhóm"""
        try:
            # Kiểm tra thành viên nhóm
            member_check = db.fetch_one(
                "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, sender_id)
            )
            if not member_check:
                return {"success": False, "message": "Bạn không phải thành viên của nhóm này"}
            
            # Lưu tin nhắn vào database
            db.execute(
                "INSERT INTO group_messages (sender_id, group_id, content) VALUES (%s, %s, %s)",
                (sender_id, group_id, content)
            )
            
            # Lấy thông tin tin nhắn vừa gửi
            message = db.fetch_one(
                """SELECT gm.message_group_id, gm.sender_id, gm.group_id, gm.content, 
                          gm.time_send, u.username as sender_name
                   FROM group_messages gm 
                   JOIN users u ON gm.sender_id = u.id 
                   WHERE gm.sender_id = %s AND gm.group_id = %s 
                   ORDER BY gm.message_group_id DESC LIMIT 1""",
                (sender_id, group_id)
            )
            
            if not message:
                return {"success": False, "message": "Không thể lấy thông tin tin nhắn"}
            
            return {
                "success": True,
                "message": "Gửi tin nhắn thành công",
                "message_data": {
                    "message_id": message["message_group_id"],
                    "sender_id": message["sender_id"],
                    "group_id": message["group_id"],
                    "content": message["content"],
                    "time_send": message["time_send"].isoformat() if message["time_send"] else None,
                    "sender_name": message["sender_name"]
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Lỗi gửi tin nhắn: {str(e)}"}

    def get_group_messages(self, group_id: int, user_id: int, limit: int = 50) -> dict:
        """Lấy tin nhắn nhóm"""
        try:
            # Kiểm tra thành viên nhóm
            member_check = db.fetch_one(
                "SELECT * FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, user_id)
            )
            if not member_check:
                return {"success": False, "message": "Bạn không phải thành viên của nhóm này"}
            
            # Lấy tin nhắn
            messages = db.fetch_all(
                """SELECT gm.message_group_id, gm.sender_id, gm.group_id, gm.content, 
                          gm.time_send, u.username as sender_name
                   FROM group_messages gm 
                   JOIN users u ON gm.sender_id = u.id 
                   WHERE gm.group_id = %s 
                   ORDER BY gm.time_send DESC LIMIT %s""",
                (group_id, limit)
            )
            
            # Chuyển đổi datetime thành string
            message_list = []
            for msg in messages:
                message_list.append({
                    "message_id": msg["message_group_id"],
                    "sender_id": msg["sender_id"], 
                    "group_id": msg["group_id"],
                    "content": msg["content"],
                    "time_send": msg["time_send"].isoformat() if msg["time_send"] else None,
                    "sender_name": msg["sender_name"]
                })
            
            return {
                "success": True,
                "messages": message_list[::-1]  # Đảo ngược để tin nhắn cũ lên trước
            }
            
        except Exception as e:
            return {"success": False, "message": f"Lỗi lấy tin nhắn: {str(e)}"}

    def get_user_groups(self, user_id: int) -> dict:
        """Lấy danh sách nhóm của user"""
        try:
            # Kiểm tra user tồn tại
            user_exists = db.fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
            if not user_exists:
                return {"success": False, "message": "User không tồn tại"}
                
            groups = db.fetch_all(
                """SELECT gc.group_id, gc.group_name, gc.created_by, u.username as creator_name
                   FROM group_chat gc
                   JOIN group_members gm ON gc.group_id = gm.group_id
                   JOIN users u ON gc.created_by = u.id
                   WHERE gm.user_id = %s""",
                (user_id,)
            )
            
            # Đảm bảo groups không phải None
            if groups is None:
                groups = []
            
            return {
                "success": True,
                "groups": [
                    {
                        "group_id": group["group_id"],
                        "group_name": group["group_name"],
                        "created_by": group["created_by"],
                        "creator_name": group["creator_name"]
                    }
                    for group in groups
                ]
            }
            
        except Exception as e:
            return {"success": False, "message": f"Lỗi lấy danh sách nhóm: {str(e)}"}

    def get_group_members(self, group_id: int, user_id: int = None) -> dict:
        """Lấy danh sách thành viên nhóm"""
        try:
            # Kiểm tra user có quyền xem danh sách thành viên không (nếu user_id được cung cấp)
            if user_id:
                member_check = db.fetch_one(
                    "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                    (group_id, user_id)
                )
                if not member_check:
                    return {"success": False, "message": "Bạn không phải thành viên của nhóm này"}
            
            members = db.fetch_all(
                """SELECT u.id, u.username, u.email
                   FROM users u
                   JOIN group_members gm ON u.id = gm.user_id
                   WHERE gm.group_id = %s""",
                (group_id,)
            )
            
            return {
                "success": True,
                "members": [
                    {
                        "user_id": member["id"],
                        "username": member["username"],
                        "email": member["email"]
                    }
                    for member in members
                ]
            }
            
        except Exception as e:
            return {"success": False, "message": f"Lỗi lấy danh sách thành viên: {str(e)}"}