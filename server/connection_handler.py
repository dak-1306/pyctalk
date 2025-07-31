# server/connection_handler.py
import socket
import threading
from client_session import handle_client

HOST = '0.0.0.0'
PORT = 9000

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"📡 Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"🔗 New connection from {client_address}")
        
        # Tạo luồng riêng cho từng client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.daemon = True
        client_thread.start()
