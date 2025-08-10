from database.db import db
import hashlib

def hash_password_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class RegisterHandler:
    def register_user(self, username: str, password: str, email: str) -> dict:
        existing_user = db.fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        if existing_user:
            return {"success": False, "message": "Tên người dùng đã tồn tại."}

        existing_email = db.fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        if existing_email:
            return {"success": False, "message": "Email đã được sử dụng."}

        hashed_password = hash_password_sha256(password)

        try:
            db.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )
            return {"success": True, "message": "Đăng ký thành công."}
        except Exception as e:
            return {"success": False, "message": f"Lỗi đăng ký: {str(e)}"}

register = RegisterHandler()
