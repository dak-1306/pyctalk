from database.db import db
import hashlib

def hash_password_sha256(password: str) -> str:
    """Mã hóa mật khẩu bằng SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

class RegisterHandler:
    async def register_user(self, username: str, password: str, email: str) -> dict:
        # Kiểm tra username đã tồn tại chưa
        existing_user = await db.fetch_one(
            "SELECT * FROM users WHERE Username = %s", (username,)
        )
        if existing_user:
            return {"success": False, "message": "Tên người dùng đã tồn tại."}

        # Kiểm tra email đã tồn tại chưa
        existing_email = await db.fetch_one(
            "SELECT * FROM users WHERE Email = %s", (email,)
        )
        if existing_email:
            return {"success": False, "message": "Email đã được sử dụng."}

        # Mã hóa mật khẩu
        hashed_password = hash_password_sha256(password)

        try:
            await db.execute(
                "INSERT INTO users (Username, Password_hash, Email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )
            return {"success": True, "message": "Đăng ký thành công."}
        except Exception as e:
            return {"success": False, "message": f"Lỗi đăng ký: {str(e)}"}

# Khởi tạo đối tượng để dùng
register = RegisterHandler()
