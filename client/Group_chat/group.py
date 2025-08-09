import json
import threading
import time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem, QMessageBox, QInputDialog, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import QThread, pyqtSignal

class GroupChatWindow(QDialog):
    def __init__(self, client, user_id, username):
        super().__init__()
        self.client = client
        self.user_id = user_id
        self.username = username
        self.current_group = None
        
        # Threading management
        self.message_sender_thread = None
        
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
        right_panel.addWidget(self.send_progress)  # Add progress bar
        right_panel.addLayout(input_layout)
        right_panel.addLayout(actions_layout)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        
        self.setLayout(main_layout)
    
    def closeEvent(self, event):
        """Cleanup khi đóng window"""
        if self.message_sender_thread and self.message_sender_thread.isRunning():
            self.message_sender_thread.quit()
            self.message_sender_thread.wait(1000)  # Wait 1 second
        super().closeEvent(event)
    
    def load_user_groups(self):
        """Load danh sách nhóm của user"""
        try:
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
                error_msg = response.get("message", "Không thể tải danh sách nhóm") if response else "Không có phản hồi từ server"
                QMessageBox.warning(self, "Lỗi", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {str(e)}")
    
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
         
    def create_new_group(self):
        """Tạo nhóm mới"""
        group_name, ok = QInputDialog.getText(self, "Tạo nhóm mới", "Tên nhóm:")
        
        if not ok or not group_name.strip():
            return
            
        try:
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
                error_msg = response.get("message", "Không thể tạo nhóm") if response else "Không nhận được phản hồi từ server"
                QMessageBox.warning(self, "Lỗi", error_msg)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tạo nhóm: {e}")
    
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
            
        try:
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
                error_msg = response.get("message", "Không thể thêm thành viên") if response else "Không nhận được phản hồi từ server"
                QMessageBox.warning(self, "Lỗi", error_msg)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi thêm thành viên: {e}")
    
    def view_members(self):
        """Xem danh sách thành viên"""
        if not self.current_group:
            return
        try:
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
                members_text = "Thành viên nhóm:\n\n"
                for member in members:
                    members_text += f"• {member['username']} (ID: {member['user_id']})\n"
                
                QMessageBox.information(self, f"Thành viên nhóm {self.current_group['group_name']}", members_text)
            else:
                error_msg = response.get("message", "Không thể tải danh sách thành viên") if response else "Không nhận được phản hồi từ server"
                QMessageBox.warning(self, "Lỗi", error_msg)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tải danh sách thành viên: {e}")
