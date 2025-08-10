from database.db import db
import hashlib

def hash_password_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class LoginHandler:
    def login_user(self, username: str, password: str) -> dict:
        user = db.fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        if not user:
            return {"success": False, "message": "Tài khoản không tồn tại."}

        hashed_input = hash_password_sha256(password)
        stored_hash = user["password_hash"]

        if hashed_input == stored_hash:
            return {"success": True, "message": "Đăng nhập thành công.", "user_id": user["id"]}
        else:
            return {"success": False, "message": "Sai mật khẩu."}

login = LoginHandler()
