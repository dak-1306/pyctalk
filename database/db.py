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
        if self.connection is not None and self.connection.is_connected():
            return  # tránh kết nối lại
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,  # Tự động commit
                charset='utf8mb4',
                use_unicode=True,
                connection_timeout=10,  # Timeout 10 giây
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ Đã kết nối MySQL Database thành công.")
        except Error as e:
            print(f"❌ Lỗi khi kết nối MySQL: {e}")
            self.connection = None
            self.cursor = None

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
            if not self.connection or not self.connection.is_connected():
                self.connect()
            self.cursor.execute(query, params)
            if not self.connection.autocommit:
                self.connection.commit()
        except Error as e:
            print(f"❌ Lỗi SQL Execute: {e}")
            if self.connection:
                self.connection.rollback()

    def fetch_one(self, query, params=()):
        """Dùng cho SELECT 1 dòng."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Error as e:
            print(f"❌ Lỗi SQL Fetch One: {e}")
            return None

    def fetch_all(self, query, params=()):
        """Dùng cho SELECT nhiều dòng."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ Lỗi SQL Fetch All: {e}")
            return []

# Khởi tạo thể hiện duy nhất
db = MySQLDatabase()
