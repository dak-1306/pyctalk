import json
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QListWidget, QMessageBox, QInputDialog

class GroupChatWindow(QDialog):
    def __init__(self, client, user_id, username):
        super().__init__()
        self.client = client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        self.setupUI()
        self.load_user_groups()
        
    def setupUI(self):
        self.setWindowTitle("PycTalk - Group Chat")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QHBoxLayout()
        
        # === Left Panel - Groups List ===
        left_panel = QVBoxLayout()
        
        # Groups label and create button
        groups_header = QHBoxLayout()
        groups_label = QLabel("Nhóm của bạn:")
        groups_label.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold))
        
        create_group_btn = QPushButton("Tạo nhóm")
        create_group_btn.clicked.connect(self.create_new_group)
        create_group_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        groups_header.addWidget(groups_label)
        groups_header.addWidget(create_group_btn)
        
        # Groups list
        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.select_group)
        self.groups_list.setMaximumWidth(250)
        
        left_panel.addLayout(groups_header)
        left_panel.addWidget(self.groups_list)
        
        # === Right Panel - Chat Area ===
        right_panel = QVBoxLayout()
        
        # Group info
        self.group_info_label = QLabel("Chọn một nhóm để bắt đầu chat")
        self.group_info_label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Weight.Bold))
        self.group_info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Messages area
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Message input area
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Nhập tin nhắn...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setEnabled(False)
        
        send_btn = QPushButton("Gửi")
        send_btn.clicked.connect(self.send_message)
        send_btn.setEnabled(False)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        self.send_btn = send_btn
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_btn)
        
        # Group actions
        actions_layout = QHBoxLayout()
        
        add_member_btn = QPushButton("Thêm thành viên")
        add_member_btn.clicked.connect(self.add_member_dialog)
        add_member_btn.setEnabled(False)
        self.add_member_btn = add_member_btn
        
        view_members_btn = QPushButton("Xem thành viên")
        view_members_btn.clicked.connect(self.view_members)
        view_members_btn.setEnabled(False)
        self.view_members_btn = view_members_btn
        
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.clicked.connect(self.refresh_messages)
        refresh_btn.setEnabled(False)
        self.refresh_btn = refresh_btn
        
        actions_layout.addWidget(add_member_btn)
        actions_layout.addWidget(view_members_btn)
        actions_layout.addWidget(refresh_btn)
        
        right_panel.addWidget(self.group_info_label)
        right_panel.addWidget(self.messages_area)
        right_panel.addLayout(input_layout)
        right_panel.addLayout(actions_layout)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        
        self.setLayout(main_layout)
    
    def load_user_groups(self):
        """Load danh sách nhóm của user"""
        request = {
            "action": "get_user_groups",
            "data": {"user_id": self.user_id}
        }
        
        response = self.client.send_json(request)
        if response and response.get("success"):
            self.groups_list.clear()
            for group in response.get("groups", []):
                item_text = f"{group['group_name']} (ID: {group['group_id']})"
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, group)
                self.groups_list.addItem(item)
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể tải danh sách nhóm")
    
    def select_group(self, item):
        """Chọn nhóm để chat"""
        group_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.current_group = group_data
        
        # Update UI
        self.group_info_label.setText(f"Nhóm: {group_data['group_name']} (ID: {group_data['group_id']})")
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.add_member_btn.setEnabled(True)
        self.view_members_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        
        # Load messages
        self.load_group_messages()
    
    def load_group_messages(self):
        """Load tin nhắn của nhóm"""
        if not self.current_group:
            return
            
        request = {
            "action": "get_group_messages",
            "data": {
                "group_id": self.current_group["group_id"],
                "user_id": self.user_id,
                "limit": 50
            }
        }
        
        response = self.client.send_json(request)
        if response and response.get("success"):
            self.messages_area.clear()
            messages = response.get("messages", [])
            
            # Reverse để hiển thị tin nhắn cũ nhất trước
            messages.reverse()
            
            for msg in messages:
                time_str = msg["time_send"].split("T")[1].split(".")[0] if msg["time_send"] else "Unknown"
                message_text = f"[{time_str}] {msg['sender_name']}: {msg['content']}"
                self.messages_area.append(message_text)
            
            # Scroll to bottom
            scrollbar = self.messages_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể tải tin nhắn")
    
    def send_message(self):
        """Gửi tin nhắn"""
        if not self.current_group:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhóm trước")
            return
            
        message_content = self.message_input.text().strip()
        if not message_content:
            return
        
        request = {
            "action": "send_group_message",
            "data": {
                "sender_id": self.user_id,
                "group_id": self.current_group["group_id"],
                "content": message_content
            }
        }
        
        response = self.client.send_json(request)
        if response and response.get("success"):
            self.message_input.clear()
            # Add message to display immediately
            message_data = response.get("message_data", {})
            time_str = message_data.get("time_send", "").split("T")[1].split(".")[0] if message_data.get("time_send") else "Now"
            message_text = f"[{time_str}] {self.username}: {message_content}"
            self.messages_area.append(message_text)
            
            # Scroll to bottom
            scrollbar = self.messages_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            QMessageBox.warning(self, "Lỗi", response.get("message", "Không thể gửi tin nhắn"))
    
    def create_new_group(self):
        """Tạo nhóm mới"""
        group_name, ok = QInputDialog.getText(self, "Tạo nhóm mới", "Tên nhóm:")
        
        if not ok or not group_name.strip():
            return
            
        request = {
            "action": "create_group",
            "data": {
                "group_name": group_name.strip(),
                "user_id": self.user_id
            }
        }
        
        response = self.client.send_json(request)
        if response and response.get("success"):
            QMessageBox.information(self, "Thành công", f"Đã tạo nhóm '{group_name}' thành công!")
            self.load_user_groups()  # Reload groups list
        else:
            QMessageBox.warning(self, "Lỗi", response.get("message", "Không thể tạo nhóm"))
    
    def add_member_dialog(self):
        """Dialog thêm thành viên"""
        if not self.current_group:
            return
            
        user_id_str, ok = QInputDialog.getText(self, "Thêm thành viên", "ID người dùng:")
        
        if not ok or not user_id_str.strip():
            return
            
        try:
            add_user_id = int(user_id_str.strip())
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "ID người dùng phải là số")
            return
            
        request = {
            "action": "add_member_to_group",
            "data": {
                "group_id": self.current_group["group_id"],
                "user_id": add_user_id,
                "admin_id": self.user_id
            }
        }
        
        response = self.client.send_json(request)
        if response and response.get("success"):
            QMessageBox.information(self, "Thành công", "Đã thêm thành viên thành công!")
        else:
            QMessageBox.warning(self, "Lỗi", response.get("message", "Không thể thêm thành viên"))
    
    def view_members(self):
        """Xem danh sách thành viên"""
        if not self.current_group:
            return
            
        request = {
            "action": "get_group_members",
            "data": {
                "group_id": self.current_group["group_id"],
                "user_id": self.user_id
            }
        }
        
        response = self.client.send_json(request)
        if response and response.get("success"):
            members = response.get("members", [])
            members_text = "Thành viên nhóm:\\n\\n"
            for member in members:
                members_text += f"• {member['username']} (ID: {member['user_id']})\\n"
            
            QMessageBox.information(self, f"Thành viên nhóm {self.current_group['group_name']}", members_text)
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể tải danh sách thành viên")
    
    def refresh_messages(self):
        """Làm mới tin nhắn"""
        if self.current_group:
            self.load_group_messages()
