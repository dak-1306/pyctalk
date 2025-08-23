# server/connection_handler_async.py
import asyncio
from server.client_session import ClientSession


class ConnectionHandlerAsync:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.server = None

    async def handle_client(self, reader, writer):
        client_address = writer.get_extra_info("peername")
        print(f"🔗 New connection from {client_address}")

        # Tạo ClientSession async
        client_session = ClientSession(reader, writer, client_address)
        await client_session.run()  # giả sử ClientSession cũng được viết async

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        addr = self.server.sockets[0].getsockname()
        print(f"📡 Async Server listening on {addr}")

        async with self.server:
            await self.server.serve_forever()


# Khởi tạo server
server = ConnectionHandlerAsync()


if __name__ == "__main__":
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped manually.")
