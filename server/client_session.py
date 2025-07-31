import json
from user_handler import handle_login, handle_logout, handle_signin

class ClientSession:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.running = True

    def run(self):
        try:
            while self.running:
                length_prefix = self.client_socket.recv(4)
                if not length_prefix:
                    print(f"⛔ Client {self.client_address} disconnected.")
                    break

                message_length = int.from_bytes(length_prefix, 'big')
                message_data = b''
                while len(message_data) < message_length:
                    chunk = self.client_socket.recv(message_length - len(message_data))
                    if not chunk:
                        break
                    message_data += chunk

                if not message_data:
                    print(f"⛔ Client {self.client_address} disconnected.")
                    break

                self.handle_message(message_data)
        finally:
            self.client_socket.close()

    def handle_message(self, raw_data):
        try:
            data = json.loads(raw_data.decode())
            action = data.get("action")

            if action == "login":
                handle_login(data, self.client_socket)
            elif action == "logout":
                handle_logout(data, self.client_socket)
            elif action == "signin":
                handle_signin(data, self.client_socket)
            elif action == "send_message":
                pass  # handle_send_message(data)
            elif action == "create_group":
                pass  # handle_create_group(data)
            else:
                print(f"❓ Unknown action from {self.client_address}: {action}")

        except json.JSONDecodeError:
            print(f"❌ Invalid JSON from {self.client_address}")
