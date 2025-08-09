import sys
import socket
import json
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
sys.path.append('../..')

from client.UI.chatUI import Ui_ChatWindow

class ChatSignals(QObject):
    """Signals for thread-safe UI updates"""
    message_received = pyqtSignal(str, str)  # message, sender
    connection_status = pyqtSignal(bool)     # connected status

class ChatWindow(QMainWindow):
    def __init__(self, username, friend_username, client_socket=None):
        super().__init__()
        self.username = username
        self.friend_username = friend_username
        self.client_socket = client_socket
        self.ui = Ui_ChatWindow()
        self.ui.setupUi(self)
        
        # Setup signals
        self.signals = ChatSignals()
        self.signals.message_received.connect(self.onMessageReceived)
        self.signals.connection_status.connect(self.onConnectionStatusChanged)
        
        # Update UI with friend's name
        self.ui.lblFriendName.setText(friend_username)
        
        # Connect events
        self.ui.btnBack.clicked.connect(self.goBack)
        
        # Override send message to use real socket
        self.ui.btnSend.clicked.disconnect()
        self.ui.txtMessage.returnPressed.disconnect()
        self.ui.btnSend.clicked.connect(self.sendRealMessage)
        self.ui.txtMessage.returnPressed.connect(self.sendRealMessage)
        
        # Clear sample messages
        self.clearMessages()
        
        # Start listening for messages if connected
        if self.client_socket:
            self.startListening()
    
    def clearMessages(self):
        """Clear all sample messages"""
        # Remove all message bubbles
        while self.ui.messagesLayout.count() > 0:
            child = self.ui.messagesLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add stretch back
        self.ui.messagesLayout.addStretch()
    
    def sendRealMessage(self):
        """Send message through socket"""
        message_text = self.ui.txtMessage.text().strip()
        if not message_text:
            return
            
        if not self.client_socket:
            QMessageBox.warning(self, "Lỗi", "Không có kết nối đến server!")
            return
        
        try:
            # Create message data
            message_data = {
                "action": "send_message",
                "data": {
                    "to": self.friend_username,
                    "message": message_text,
                    "type": "text"
                }
            }
            
            # Send message
            message_json = json.dumps(message_data)
            self.client_socket.send(message_json.encode('utf-8'))
            
            # Add to UI as sent message
            self.ui.addMessage(message_text, True)
            self.ui.txtMessage.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi gửi tin nhắn", str(e))
    
    def startListening(self):
        """Start listening for incoming messages"""
        self.listen_thread = threading.Thread(target=self.listenForMessages)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def listenForMessages(self):
        """Listen for incoming messages in separate thread"""
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    message_data = json.loads(data.decode('utf-8'))
                    
                    if message_data.get("action") == "receive_message":
                        msg_info = message_data.get("data", {})
                        sender = msg_info.get("from", "Unknown")
                        message = msg_info.get("message", "")
                        
                        # Emit signal for thread-safe UI update
                        self.signals.message_received.emit(message, sender)
                        
                except json.JSONDecodeError:
                    print("Received invalid JSON data")
                    
        except Exception as e:
            print(f"Error in message listening: {e}")
            self.signals.connection_status.emit(False)
    
    def onMessageReceived(self, message, sender):
        """Handle received message (runs in main thread)"""
        self.ui.addMessage(message, False)
    
    def onConnectionStatusChanged(self, is_connected):
        """Handle connection status change"""
        if is_connected:
            self.ui.lblStatus.setText("● Online")
            self.ui.lblStatus.setStyleSheet("color: #42b883; font-size: 12px;")
        else:
            self.ui.lblStatus.setText("● Offline")
            self.ui.lblStatus.setStyleSheet("color: #e74c3c; font-size: 12px;")
    
    def goBack(self):
        """Go back to main window"""
        self.close()

class ChatClient:
    def __init__(self):
        self.socket = None
        self.username = None
        self.connected = False
    
    def connect_to_server(self, host='localhost', port=9000):
        """Connect to chat server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def login(self, username, password):
        """Login to server"""
        if not self.connected:
            return False
        
        try:
            login_data = {
                "action": "login",
                "data": {
                    "username": username,
                    "password": password
                }
            }
            
            message = json.dumps(login_data)
            self.socket.send(message.encode('utf-8'))
            
            # Wait for response
            response = self.socket.recv(1024)
            response_data = json.loads(response.decode('utf-8'))
            
            if response_data.get("success"):
                self.username = username
                return True
            else:
                print(f"Login failed: {response_data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def start_chat(self, friend_username):
        """Start chat with a friend"""
        if not self.connected or not self.username:
            return None
        
        return ChatWindow(self.username, friend_username, self.socket)
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
                self.connected = False

# Test function
def test_chat_ui():
    """Test function to show chat UI without server connection"""
    app = QApplication(sys.argv)
    
    # Create chat window for testing
    chat_window = ChatWindow("user1", "user2", None)
    
    # Add some test messages
    chat_window.ui.addMessage("Xin chào! 😊", False)
    chat_window.ui.addMessage("Chào bạn! Bạn có khỏe không?", True)
    chat_window.ui.addMessage("Mình khỏe, cảm ơn bạn. Còn bạn?", False)
    
    chat_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    test_chat_ui()
