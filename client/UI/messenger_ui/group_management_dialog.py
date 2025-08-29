from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QTimer
import asyncio

class GroupManagementDialog(QtWidgets.QDialog):
    """Dialog quản lý thành viên nhóm và quyền trưởng nhóm"""
    
    def __init__(self, group_data, current_user_id, client, parent=None):
        super().__init__(parent)
        self.group_data = group_data
        self.current_user_id = current_user_id
        self.client = client
        self.members = []
        self.current_user_role = "member"
        
        self.setWindowTitle(f"Quản lý nhóm: {group_data.get('group_name', 'Unknown')}")
        self.setFixedSize(500, 600)
        self.setup_ui()
        self.load_group_members()
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Group info
        info_group = QtWidgets.QGroupBox("Thông tin nhóm")
        info_layout = QtWidgets.QVBoxLayout()
        
        self.group_name_label = QtWidgets.QLabel(f"Tên nhóm: {self.group_data.get('group_name', 'Unknown')}")
        self.group_name_label.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold))
        info_layout.addWidget(self.group_name_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Members list
        members_group = QtWidgets.QGroupBox("Danh sách thành viên")
        members_layout = QtWidgets.QVBoxLayout()
        
        # Search/filter
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm thành viên...")
        members_layout.addWidget(self.search_input)
        
        # Members table
        self.members_table = QtWidgets.QTableWidget()
        self.members_table.setColumnCount(4)
        self.members_table.setHorizontalHeaderLabels(["Tên", "Vai trò", "Ngày tham gia", "Hành động"])
        self.members_table.horizontalHeader().setStretchLastSection(True)
        self.members_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        members_layout.addWidget(self.members_table)
        
        members_group.setLayout(members_layout)
        layout.addWidget(members_group)
        
        # Action buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.leave_btn = QtWidgets.QPushButton("Rời nhóm")
        self.leave_btn.clicked.connect(self.leave_group)
        self.leave_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; }")
        buttons_layout.addWidget(self.leave_btn)
        
        buttons_layout.addStretch()
        
        self.refresh_btn = QtWidgets.QPushButton("Làm mới")
        self.refresh_btn.clicked.connect(self.load_group_members)
        buttons_layout.addWidget(self.refresh_btn)
        
        self.close_btn = QtWidgets.QPushButton("Đóng")
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def load_group_members(self):
        """Load danh sách thành viên từ server"""
        print(f"[GroupManagement] Loading members for group_id={self.group_data.get('group_id')}")
        
        async def fetch_members():
            try:
                response = await self.client.get_group_members(
                    str(self.group_data.get('group_id')),
                    str(self.current_user_id)
                )
                
                if response and response.get("status") == "ok":
                    self.members = response.get("members", [])
                    # Find current user's role
                    for member in self.members:
                        if int(member["user_id"]) == int(self.current_user_id):
                            self.current_user_role = member["role"]
                            break
                    
                    self.update_members_table()
                else:
                    QtWidgets.QMessageBox.warning(self, "Lỗi", 
                                                f"Không thể tải danh sách thành viên: {response.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"[ERROR] Load group members: {e}")
                QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {e}")
        
        # Run async function
        loop = asyncio.get_event_loop()
        loop.create_task(fetch_members())
        
    def update_members_table(self):
        """Cập nhật bảng thành viên"""
        self.members_table.setRowCount(len(self.members))
        
        for row, member in enumerate(self.members):
            # Name
            name_item = QtWidgets.QTableWidgetItem(member["username"])
            self.members_table.setItem(row, 0, name_item)
            
            # Role
            role_text = "🛡️ Trưởng nhóm" if member["role"] == "admin" else "👤 Thành viên"
            role_item = QtWidgets.QTableWidgetItem(role_text)
            if member["role"] == "admin":
                role_item.setForeground(QtGui.QColor("#ff6b00"))
            self.members_table.setItem(row, 1, role_item)
            
            # Joined date
            joined_date = member.get("joined_at", "Unknown")
            if joined_date and joined_date != "Unknown":
                try:
                    # Format date nicely
                    from datetime import datetime
                    dt = datetime.strptime(joined_date, '%Y-%m-%d %H:%M:%S')
                    joined_date = dt.strftime('%d/%m/%Y')
                except:
                    pass
            date_item = QtWidgets.QTableWidgetItem(joined_date)
            self.members_table.setItem(row, 2, date_item)
            
            # Actions
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout()
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            member_id = member["user_id"]
            is_current_user = int(member_id) == int(self.current_user_id)
            is_admin = member["role"] == "admin"
            current_is_admin = self.current_user_role == "admin"
            
            # Transfer admin button (only for admins, to non-admins, not self)
            if current_is_admin and not is_admin and not is_current_user:
                transfer_btn = QtWidgets.QPushButton("Chuyển quyền")
                transfer_btn.setStyleSheet("QPushButton { background-color: #ff6b00; color: white; font-size: 10px; }")
                transfer_btn.clicked.connect(lambda checked, uid=member_id, name=member["username"]: self.transfer_admin(uid, name))
                actions_layout.addWidget(transfer_btn)
            
            # Remove member button (only for admins, not self)
            if current_is_admin and not is_current_user:
                remove_btn = QtWidgets.QPushButton("Xóa")
                remove_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-size: 10px; }")
                remove_btn.clicked.connect(lambda checked, uid=member_id, name=member["username"]: self.remove_member(uid, name))
                actions_layout.addWidget(remove_btn)
            
            actions_widget.setLayout(actions_layout)
            self.members_table.setCellWidget(row, 3, actions_widget)
            
        # Auto-resize columns
        self.members_table.resizeColumnsToContents()
        self.members_table.horizontalHeader().setStretchLastSection(True)
        
    def transfer_admin(self, new_admin_id, new_admin_name):
        """Chuyển quyền trưởng nhóm"""
        reply = QtWidgets.QMessageBox.question(
            self, "Xác nhận", 
            f"Bạn có chắc chắn muốn chuyển quyền trưởng nhóm cho {new_admin_name}?\\n\\n"
            f"Sau khi chuyển, bạn sẽ trở thành thành viên thường.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            async def do_transfer():
                try:
                    response = await self.client.transfer_leadership(
                        str(self.group_data.get('group_id')),
                        str(self.current_user_id),
                        str(new_admin_id)
                    )
                    
                    if response and response.get("status") == "ok":
                        QtWidgets.QMessageBox.information(self, "Thành công", 
                                                        f"Đã chuyển quyền trưởng nhóm cho {new_admin_name}")
                        self.load_group_members()  # Refresh
                    else:
                        QtWidgets.QMessageBox.warning(self, "Lỗi", 
                                                    f"Không thể chuyển quyền: {response.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {e}")
            
            loop = asyncio.get_event_loop()
            loop.create_task(do_transfer())
            
    def remove_member(self, member_id, member_name):
        """Xóa thành viên khỏi nhóm (chưa implement server-side)"""
        QtWidgets.QMessageBox.information(self, "Thông báo", 
                                        f"Tính năng xóa thành viên {member_name} sẽ được thêm trong phiên bản tiếp theo")
        
    def leave_group(self):
        """Rời khỏi nhóm"""
        if self.current_user_role == "admin":
            # Check if there are other admins
            other_admins = [m for m in self.members if m["role"] == "admin" and int(m["user_id"]) != int(self.current_user_id)]
            if not other_admins:
                QtWidgets.QMessageBox.warning(
                    self, "Không thể rời nhóm", 
                    "Bạn là trưởng nhóm duy nhất. Vui lòng chuyển quyền trưởng nhóm cho ai đó trước khi rời nhóm."
                )
                return
        
        reply = QtWidgets.QMessageBox.question(
            self, "Xác nhận", 
            f"Bạn có chắc chắn muốn rời khỏi nhóm '{self.group_data.get('group_name')}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            async def do_leave():
                try:
                    response = await self.client.leave_group(
                        str(self.group_data.get('group_id')),
                        str(self.current_user_id)
                    )
                    
                    if response and response.get("status") == "ok":
                        QtWidgets.QMessageBox.information(self, "Thành công", 
                                                        response.get("message", "Đã rời nhóm thành công"))
                        self.accept()  # Close dialog
                    else:
                        if response.get("require_transfer"):
                            QtWidgets.QMessageBox.warning(self, "Cần chuyển quyền", 
                                                        response.get("message", "Cần chuyển quyền trước khi rời nhóm"))
                        else:
                            QtWidgets.QMessageBox.warning(self, "Lỗi", 
                                                        f"Không thể rời nhóm: {response.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {e}")
            
            loop = asyncio.get_event_loop()
            loop.create_task(do_leave())
