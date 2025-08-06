# database/db.py
import mysql.connector
from mysql.connector import Error

class MySQLDatabase:
    def __init__(self, host="localhost", user="root", password="", database="pyctalk"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Kết nối tới MySQL server."""
        if self.connection is not None:
            return  # tránh kết nối lại
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ Đã kết nối MySQL Database thành công.")
        except Error as e:
            print(f"❌ Lỗi khi kết nối MySQL: {e}")

    def disconnect(self):
        """Đóng kết nối MySQL."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("🔌 Đã ngắt kết nối MySQL Database.")

    def execute(self, query, params=()):
        """Dùng cho INSERT, UPDATE, DELETE."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Error as e:
            print(f"❌ Lỗi SQL: {e}")

    def fetch_one(self, query, params=()):
        """Dùng cho SELECT 1 dòng."""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=()):
        """Dùng cho SELECT nhiều dòng."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

# Khởi tạo thể hiện duy nhất
db = MySQLDatabase()
