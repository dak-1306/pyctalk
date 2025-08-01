from database.db import db
import hashlib

def hash_password_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class RegisterHandler:
    def register_user(self, username: str, password: str, email: str) -> dict:
        existing_user = db.fetch_one("SELECT * FROM users WHERE Username = %s", (username,))
        if existing_user:
            return {"success": False, "message": "Tên người dùng đã tồn tại."}

        hashed_password = hash_password_sha256(password)

        try:
            db.execute(
                "INSERT INTO users (Username, Password_hash, Email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )
            return {"success": True, "message": "Đăng ký thành công."}
        except Exception as e:
            return {"success": False, "message": f"Lỗi đăng ký: {str(e)}"}

register = RegisterHandler()
