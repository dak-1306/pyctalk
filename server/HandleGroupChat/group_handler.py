# server/group_handler.py
from database.db import db
from datetime import datetime

class GroupHandler:
    def __init__(self):
        pass

    async def create_group_with_members(self, group_name: str, created_by: int, member_ids: list) -> dict:
        """Tạo nhóm mới và thêm nhiều thành viên"""
        try:
            # Tạo nhóm
            await db.execute(
                "INSERT INTO group_chat (group_name, created_by) VALUES (%s, %s)",
                (group_name, created_by)
            )

            # Lấy ID nhóm vừa tạo
            result = await db.fetch_one("SELECT LAST_INSERT_ID() as group_id")
            group_id = result["group_id"]

            # Thêm người tạo vào nhóm
            await db.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, created_by)
            )

            # Thêm các thành viên được chọn
            added_count = 0
            for uid in member_ids:
                if int(uid) == int(created_by):
                    continue

                # Kiểm tra user tồn tại
                user_exists = await db.fetch_one("SELECT id FROM users WHERE id = %s", (uid,))
                if not user_exists:
                    continue

                # Kiểm tra đã là thành viên chưa
                already_member = await db.fetch_one(
                    "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                    (group_id, uid)
                )
                if already_member:
                    continue

                await db.execute(
                    "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                    (group_id, uid)
                )
                added_count += 1

            return {
                "success": True,
                "message": f"Tạo nhóm '{group_name}' thành công, đã thêm {added_count} thành viên.",
                "group_id": group_id
            }
        except Exception as e:
            return {"success": False, "message": f"Lỗi tạo nhóm: {str(e)}"}

    async def create_group(self, group_name: str, created_by: int) -> dict:
        """Tạo nhóm chat mới"""
        try:
            await db.execute(
                "INSERT INTO group_chat (group_name, created_by) VALUES (%s, %s)",
                (group_name, created_by)
            )
            result = await db.fetch_one("SELECT LAST_INSERT_ID() as group_id")
            group_id = result["group_id"]

            await db.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, created_by)
            )
            return {"status": "ok", "message": f"Tạo nhóm '{group_name}' thành công", "group_id": group_id}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi tạo nhóm: {str(e)}"}

    async def add_member_to_group(self, group_id: int, user_id: int, added_by: int) -> dict:
        """Thêm thành viên vào nhóm"""
        try:
            group_info = await db.fetch_one("SELECT created_by FROM group_chat WHERE group_id = %s", (group_id,))
            if not group_info or group_info["created_by"] != added_by:
                return {"success": False, "message": "Chỉ admin mới được thêm thành viên"}

            user_exists = await db.fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
            if not user_exists:
                return {"success": False, "message": "Người dùng không tồn tại"}

            already_member = await db.fetch_one(
                "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, user_id)
            )
            if already_member:
                return {"success": False, "message": "Người dùng đã là thành viên của nhóm"}

            await db.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, user_id)
            )

            user_info = await db.fetch_one("SELECT username FROM users WHERE id = %s", (user_id,))
            return {"success": True, "message": f"Đã thêm {user_info['username']} vào nhóm"}
        except Exception as e:
            return {"success": False, "message": f"Lỗi thêm thành viên: {str(e)}"}

    async def send_group_message(self, sender_id: int, group_id: int, content: str) -> dict:
        """Gửi tin nhắn nhóm"""
        try:
            member_check = await db.fetch_one(
                "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, sender_id)
            )
            if not member_check:
                return {"success": False, "message": "Bạn không phải thành viên của nhóm này"}

            if not content or len(content.strip()) == 0:
                return {"success": False, "message": "Nội dung tin nhắn không được để trống"}
            if len(content) > 1000:
                return {"success": False, "message": "Nội dung tin nhắn quá dài (tối đa 1000 ký tự)"}

            await db.execute(
                "INSERT INTO group_messages (sender_id, group_id, content) VALUES (%s, %s, %s)",
                (sender_id, group_id, content)
            )

            message = await db.fetch_one(
                """SELECT gm.message_group_id, gm.sender_id, gm.group_id, gm.content, gm.time_send, u.username as sender_name
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
            import traceback
            print("[GroupHandler] Lỗi gửi tin nhắn:", traceback.format_exc())
            return {"success": False, "message": f"Lỗi gửi tin nhắn: {str(e)}"}

    async def get_group_messages(self, group_id: int, user_id: int, limit: int = 50, offset: int = 0) -> dict:
        """Lấy tin nhắn nhóm"""
        try:
            member_check = await db.fetch_one(
                "SELECT * FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, user_id)
            )
            if not member_check:
                return {"success": False, "message": "Bạn không phải thành viên của nhóm này"}

            messages = await db.fetch_all(
                """SELECT gm.message_group_id, gm.sender_id, gm.group_id, gm.content, gm.time_send, u.username as sender_name
                   FROM group_messages gm 
                   JOIN users u ON gm.sender_id = u.id 
                   WHERE gm.group_id = %s 
                   ORDER BY gm.time_send DESC LIMIT %s OFFSET %s""",
                (group_id, limit, offset)
            )
            message_list = [
                {
                    "message_id": msg["message_group_id"],
                    "sender_id": msg["sender_id"],
                    "group_id": msg["group_id"],
                    "content": msg["content"],
                    "time_send": msg["time_send"].isoformat() if msg["time_send"] else None,
                    "sender_name": msg["sender_name"]
                }
                for msg in messages
            ]
            return {"success": True, "messages": message_list[::-1]}
        except Exception as e:
            return {"success": False, "message": f"Lỗi lấy tin nhắn: {str(e)}"}

    async def get_user_groups(self, user_id: int) -> dict:
        """Lấy danh sách nhóm của user"""
        try:
            try:
                user_id = int(user_id)
            except Exception:
                return {"success": False, "message": "user_id không hợp lệ"}

            user_exists = await db.fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
            if not user_exists:
                return {"success": False, "message": "User không tồn tại"}

            groups = await db.fetch_all(
                """SELECT gc.group_id, gc.group_name, gc.created_by, u.username as creator_name
                   FROM group_chat gc
                   JOIN group_members gm ON gc.group_id = gm.group_id
                   JOIN users u ON gc.created_by = u.id
                   WHERE gm.user_id = %s""",
                (user_id,)
            )
            if groups is None:
                groups = []
            return {
                "success": True,
                "groups": [
                    {
                        "group_id": g["group_id"],
                        "group_name": g["group_name"],
                        "created_by": g["created_by"],
                        "creator_name": g["creator_name"]
                    }
                    for g in groups
                ]
            }
        except Exception as e:
            return {"success": False, "message": f"Lỗi lấy danh sách nhóm: {str(e)}"}

    async def get_group_members(self, group_id: int, user_id: int = None) -> dict:
        """Lấy danh sách thành viên nhóm"""
        try:
            if user_id:
                member_check = await db.fetch_one(
                    "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                    (group_id, user_id)
                )
                if not member_check:
                    return {"success": False, "message": "Bạn không phải thành viên của nhóm này"}

            members = await db.fetch_all(
                """SELECT u.id, u.username, u.email
                   FROM users u
                   JOIN group_members gm ON u.id = gm.user_id
                   WHERE gm.group_id = %s""",
                (group_id,)
            )
            return {
                "success": True,
                "members": [
                    {"user_id": m["id"], "username": m["username"], "email": m["email"]}
                    for m in members
                ]
            }
        except Exception as e:
            return {"success": False, "message": f"Lỗi lấy danh sách thành viên: {str(e)}"}

    async def add_user_to_group(self, group_id: int, user_id: int) -> dict:
        """Thêm người dùng vào nhóm (đơn giản, không kiểm tra admin)"""
        try:
            # Kiểm tra nhóm tồn tại
            group_exists = await db.fetch_one("SELECT group_id FROM group_chat WHERE group_id = %s", (group_id,))
            if not group_exists:
                return {"status": "error", "message": "Nhóm không tồn tại"}
            
            # Kiểm tra user tồn tại
            user_exists = await db.fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
            if not user_exists:
                return {"status": "error", "message": "Người dùng không tồn tại"}
            
            # Kiểm tra đã là thành viên chưa
            already_member = await db.fetch_one(
                "SELECT user_id FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, user_id)
            )
            if already_member:
                return {"status": "error", "message": "Người dùng đã là thành viên của nhóm"}
            
            # Thêm vào nhóm
            await db.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, user_id)
            )
            
            return {"status": "ok", "message": "Đã thêm thành viên vào nhóm"}
            
        except Exception as e:
            print(f"❌ Lỗi add_user_to_group: {e}")
            return {"status": "error", "message": str(e)}
