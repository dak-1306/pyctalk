from server.connection_handler import server

if __name__ == "__main__":
    print("🟢 Starting PycTalk server...")
    import asyncio
    asyncio.run(server.start())

