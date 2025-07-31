# server/client_session.py
import json
from user_handler import handle_login, handle_logout, handle_signin

def handle_client_message(raw_data):
    try:
        data = json.loads(raw_data.decode())  # Giải mã JSON từ bytes
        action = data.get("action")
        if action == "login":
            handle_login(data)
        elif action == "logout":
            handle_logout(data)
        elif action == "signin":
            handle_signin(data)
        elif action == "send_message":
            handle_send_message(data)
        elif action == "create_group":
            handle_create_group(data)
        else:
            print("Unknown action:", action)
    except json.JSONDecodeError:
        print("Invalid JSON format")



def handle_client(client_socket, client_address):
    try:
        while True:
            # Nhận độ dài của thông điệp (4 byte đầu tiên)
            length_prefix = client_socket.recv(4)
            if not length_prefix:
                print(f"⛔ Client {client_address} disconnected.")
                break
            message_length = int.from_bytes(length_prefix, 'big')
            message_data = b''
            while len(message_data) < message_length:
                chunk = client_socket.recv(message_length - len(message_data))
                if not chunk:
                    break
                message_data += chunk
            if not message_data:
                print(f"⛔ Client {client_address} disconnected.")
                break
            handle_client_message(message_data)
    finally:
        client_socket.close()

