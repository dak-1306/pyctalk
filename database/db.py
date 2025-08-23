# database/db.py
import asyncio
import aiomysql


class AsyncMySQLDatabase:
    def __init__(self, host="localhost", user="root", password="dang13062005", database="pyctalk"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.pool = None

    async def connect(self):
        """Kết nối tới MySQL server với connection pool."""
        if self.pool is not None:
            return  # tránh tạo lại pool
        try:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.database,
                autocommit=True,     # tự động commit
                charset="utf8mb4",
                use_unicode=True,
                minsize=1,           # số kết nối tối thiểu
                maxsize=10,          # số kết nối tối đa
                connect_timeout=10   # timeout kết nối
            )
            print("✅ Đã kết nối MySQL Database (async) thành công.")
        except Exception as e:
            print(f"❌ Lỗi khi kết nối MySQL (async): {e}")
            self.pool = None

    async def disconnect(self):
        """Đóng connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            print("🔌 Đã ngắt kết nối MySQL Database (async).")

    async def execute(self, query, params=()):
        """Dùng cho INSERT, UPDATE, DELETE."""
        try:
            if self.pool is None:
                await self.connect()
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
        except Exception as e:
            print(f"❌ Lỗi SQL Execute (async): {e}")
            raise  # Báo lỗi lên trên để messenger_db.py nhận biết
    async def fetch_one(self, query, params=()):
        """Dùng cho SELECT 1 dòng."""
        try:
            if self.pool is None:
                await self.connect()
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return await cursor.fetchone()
        except Exception as e:
            print(f"❌ Lỗi SQL Fetch One (async): {e}")
            return None

    async def fetch_all(self, query, params=()):
        """Dùng cho SELECT nhiều dòng."""
        try:
            if self.pool is None:
                await self.connect()
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return await cursor.fetchall()
        except Exception as e:
            print(f"❌ Lỗi SQL Fetch All (async): {e}")
            return []


# Khởi tạo thể hiện duy nhất
db = AsyncMySQLDatabase()
