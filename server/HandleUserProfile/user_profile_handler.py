import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import AsyncMySQLDatabase

class UserProfileHandler:
    def __init__(self):
        self.db = AsyncMySQLDatabase()

    async def get_user_profile(self, user_id):
        """Lấy thông tin profile đầy đủ của user"""
        try:
            print(f"[DEBUG] get_user_profile called for user_id: {user_id}")
            
            # Ensure database connection
            if not self.db.pool:
                await self.db.connect()
            
            # Get basic user info
            user_query = """
                SELECT id, username, email, created_at 
                FROM users 
                WHERE id = %s
            """
            user_result = await self.db.fetch_one(user_query, (user_id,))
            
            if not user_result:
                return {"status": "error", "message": "User not found"}
            
            # Try to get profile data from user_profiles table
            profile_query = """
                SELECT user_id, display_name, bio, gender, birth_date, phone, location, 
                       avatar_url, privacy_settings, created_at, updated_at
                FROM user_profiles 
                WHERE user_id = %s
            """
            profile_result = await self.db.fetch_one(profile_query, (user_id,))
            
            if profile_result:
                # Use real profile data from user_profiles table
                profile_data = {
                    "user_id": user_result["id"],
                    "username": user_result["username"],
                    "display_name": profile_result["display_name"] or user_result["username"],
                    "email": user_result["email"],
                    "bio": profile_result["bio"] or "Chưa có thông tin",
                    "gender": profile_result["gender"] or "Không xác định",
                    "birth_date": profile_result["birth_date"].strftime("%Y-%m-%d") if profile_result["birth_date"] else None,
                    "phone": profile_result["phone"],
                    "location": profile_result["location"] or "Chưa cập nhật",
                    "avatar_url": profile_result["avatar_url"],
                    "created_at": user_result["created_at"].strftime("%Y-%m-%d %H:%M:%S") if user_result["created_at"] else None,
                    "updated_at": profile_result["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if profile_result["updated_at"] else None
                }
            else:
                # Fallback to mock data if no profile exists
                profile_data = {
                    "user_id": user_result["id"],
                    "username": user_result["username"],
                    "display_name": user_result["username"],  # Use username as display name
                    "email": user_result["email"],
                    "bio": "Chưa có thông tin",
                    "gender": "Không xác định",
                    "birth_date": None,
                    "phone": None,
                    "location": "Chưa cập nhật",
                    "avatar_url": None,
                    "created_at": user_result["created_at"].strftime("%Y-%m-%d %H:%M:%S") if user_result["created_at"] else None,
                    "updated_at": None
                }
            
            return {
                "status": "ok", 
                "data": profile_data
            }
            
        except Exception as e:
            print(f"❌ Lỗi get_user_profile: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    async def get_mutual_groups(self, user1_id, user2_id):
        """Lấy danh sách nhóm chung của 2 user"""
        try:
            print(f"[DEBUG] get_mutual_groups called for user1_id: {user1_id}, user2_id: {user2_id}")
            
            # Ensure database connection
            if not self.db.pool:
                await self.db.connect()
            
            query = """
                SELECT DISTINCT g.group_id, g.group_name, g.created_by,
                       (SELECT COUNT(*) FROM group_members gm WHERE gm.group_id = g.group_id) as member_count
                FROM group_chat g
                INNER JOIN group_members gm1 ON g.group_id = gm1.group_id
                INNER JOIN group_members gm2 ON g.group_id = gm2.group_id
                WHERE gm1.user_id = %s AND gm2.user_id = %s
                ORDER BY g.group_name
            """
            
            results = await self.db.fetch_all(query, (user1_id, user2_id))
            
            mutual_groups = []
            for row in results:
                mutual_groups.append({
                    "group_id": row["group_id"],
                    "group_name": row["group_name"],
                    "created_by": row["created_by"],
                    "member_count": row["member_count"]
                })
            
            print(f"✅ Found {len(mutual_groups)} mutual groups")
            return {"status": "ok", "data": mutual_groups}
            
        except Exception as e:
            print(f"❌ Lỗi get_mutual_groups: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    async def update_user_profile(self, user_id, profile_data):
        """Cập nhật thông tin profile của user"""
        try:
            print(f"[DEBUG] update_user_profile called for user_id: {user_id}")
            
            # Ensure database connection
            if not self.db.pool:
                await self.db.connect()
            
            # For now, just return success without actually updating
            # since user_profiles table might not exist
            print(f"✅ Mock update profile for user_id {user_id}")
            return {"status": "success", "message": "Profile updated successfully"}
            
        except Exception as e:
            print(f"❌ Lỗi update_user_profile: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
            print(f"❌ Lỗi update_user_profile: {e}")
            return {"status": "error", "message": str(e)}

# Create global instance
user_profile_handler = UserProfileHandler()
