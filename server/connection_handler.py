# server/connection_handler.py
import socket
import threading
from .client_session import ClientSession

class ConnectionHandler:
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"📡 Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"🔗 New connection from {client_address}")
            
            client_session = ClientSession(client_socket, client_address)
            thread = threading.Thread(target=client_session.run)
            thread.daemon = True
            thread.start()
server = ConnectionHandler()