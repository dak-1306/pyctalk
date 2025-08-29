"""
Dialog để thêm bạn bè vào nhóm
"""
import asyncio
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, 
                             QCheckBox, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from client.Group_chat.group_api_client import GroupAPIClient


class AddFriendToGroupDialog(QDialog):
    """Dialog để thêm bạn bè vào nhóm"""
    
    # Signal được emit khi thêm thành viên thành công
    member_added = pyqtSignal()
    
    def __init__(self, group_id, group_name, user_id, username, client, parent=None):
        super().__init__(parent)
        self.group_id = str(group_id)
        self.group_name = group_name
        self.user_id = str(user_id)
        self.username = username
        # client ở đây thực chất đã là GroupAPIClient rồi
        self.group_api = client
        
        self.friends_data = []
        self.selected_friends = []
        
        self.setup_ui()
        self.load_friends()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        self.setWindowTitle(f"Thêm bạn bè vào nhóm: {self.group_name}")
        self.setFixedSize(400, 500)
        self.setModal(True)
        
        # Layout chính
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tiêu đề
        title_label = QLabel(f"Chọn bạn bè để thêm vào nhóm\n'{self.group_name}'")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Hướng dẫn
        instruction_label = QLabel("Chọn những người bạn muốn thêm vào nhóm:")
        instruction_label.setStyleSheet("color: #7f8c8d; font-size: 10pt;")
        layout.addWidget(instruction_label)
        
        # Progress bar để loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Danh sách bạn bè
        self.friends_list = QListWidget()
        self.friends_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: white;
                selection-background-color: #3498db;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.friends_list)
        
        # Thông tin đã chọn
        self.selected_info = QLabel("Đã chọn: 0 người")
        self.selected_info.setStyleSheet("color: #3498db; font-weight: bold;")
        layout.addWidget(self.selected_info)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Chọn tất cả / Bỏ chọn tất cả
        self.select_all_btn = QPushButton("Chọn tất cả")
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.select_all_btn)
        
        button_layout.addStretch()
        
        # Thêm vào nhóm
        self.add_btn = QPushButton("Thêm vào nhóm")
        self.add_btn.clicked.connect(self.add_selected_friends)
        self.add_btn.setEnabled(False)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.add_btn)
        
        # Hủy
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_friends(self):
        """Load danh sách bạn bè từ server"""
        print(f"[AddFriendDialog] Loading friends for username={self.username}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Sử dụng QTimer để chạy async function
        QTimer.singleShot(100, lambda: asyncio.create_task(self._load_friends_async()))
    
    async def _load_friends_async(self):
        """Async function để load bạn bè"""
        try:
            response = await self.group_api.get_user_friends(self.username)
            print(f"[AddFriendDialog] Friends response: {response}")
            
            if response and response.get('status') == 'ok':
                self.friends_data = response.get('data', [])
                self._display_friends()
            else:
                self._show_error("Không thể tải danh sách bạn bè")
        except Exception as e:
            print(f"❌ Error loading friends: {e}")
            self._show_error(f"Lỗi tải bạn bè: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def _display_friends(self):
        """Hiển thị danh sách bạn bè"""
        self.friends_list.clear()
        
        if not self.friends_data:
            item = QListWidgetItem("Bạn chưa có bạn bè nào để thêm vào nhóm")
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # Disable item
            self.friends_list.addItem(item)
            return
        
        for friend in self.friends_data:
            # Tạo checkable item đơn giản
            item = QListWidgetItem(f"{friend['friend_name']} (ID: {friend['friend_id']})")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            
            # Store friend data as item data
            item.setData(Qt.ItemDataRole.UserRole, friend)
            
            self.friends_list.addItem(item)
        
        # Connect signal for item changes
        self.friends_list.itemChanged.connect(self._on_selection_changed)
        
        print(f"[AddFriendDialog] Displayed {len(self.friends_data)} friends")
    
    def _on_selection_changed(self):
        """Xử lý khi có thay đổi selection"""
        self.selected_friends = []
        
        for i in range(self.friends_list.count()):
            item = self.friends_list.item(i)
            
            if item.checkState() == Qt.CheckState.Checked:
                friend_data = item.data(Qt.ItemDataRole.UserRole)
                if friend_data:
                    self.selected_friends.append(friend_data)
        
        # Cập nhật UI
        count = len(self.selected_friends)
        self.selected_info.setText(f"Đã chọn: {count} người")
        self.add_btn.setEnabled(count > 0)
        
        # Cập nhật text button chọn tất cả
        if count == len(self.friends_data):
            self.select_all_btn.setText("Bỏ chọn tất cả")
        else:
            self.select_all_btn.setText("Chọn tất cả")
    
    def toggle_select_all(self):
        """Chọn tất cả hoặc bỏ chọn tất cả"""
        select_all = self.select_all_btn.text() == "Chọn tất cả"
        
        for i in range(self.friends_list.count()):
            item = self.friends_list.item(i)
            
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                if select_all:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
    
    def add_selected_friends(self):
        """Thêm các bạn bè đã chọn vào nhóm"""
        if not self.selected_friends:
            return
        
        self.add_btn.setEnabled(False)
        self.add_btn.setText("Đang thêm...")
        
        # Sử dụng QTimer để chạy async function
        QTimer.singleShot(100, lambda: asyncio.create_task(self._add_friends_async()))
    
    async def _add_friends_async(self):
        """Async function để thêm bạn bè"""
        try:
            success_count = 0
            failed_friends = []
            
            for friend in self.selected_friends:
                try:
                    response = await self.group_api.add_friend_to_group(
                        self.group_id,
                        str(friend['friend_id']),
                        self.user_id
                    )
                    
                    if response and response.get('status') == 'ok':
                        success_count += 1
                        print(f"✅ Added {friend['friend_name']} to group")
                    else:
                        failed_friends.append(f"{friend['friend_name']}: {response.get('message', 'Lỗi không xác định')}")
                        print(f"❌ Failed to add {friend['friend_name']}: {response}")
                
                except Exception as e:
                    failed_friends.append(f"{friend['friend_name']}: {str(e)}")
                    print(f"❌ Exception adding {friend['friend_name']}: {e}")
            
            # Hiển thị kết quả
            if success_count > 0:
                # Emit signal để refresh member list
                self.member_added.emit()
                
                if failed_friends:
                    message = f"Đã thêm {success_count} người thành công.\n\nCác lỗi:\n" + "\n".join(failed_friends)
                    QMessageBox.warning(self, "Thêm một phần thành công", message)
                else:
                    QMessageBox.information(self, "Thành công", f"Đã thêm {success_count} người vào nhóm thành công!")
                
                self.accept()
            else:
                error_message = "Không thể thêm ai vào nhóm.\n\nLý do:\n" + "\n".join(failed_friends)
                QMessageBox.critical(self, "Thất bại", error_message)
        
        except Exception as e:
            print(f"❌ Error in _add_friends_async: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi không xác định: {str(e)}")
        
        finally:
            self.add_btn.setEnabled(True)
            self.add_btn.setText("Thêm vào nhóm")
    
    def _show_error(self, message):
        """Hiển thị thông báo lỗi"""
        QMessageBox.critical(self, "Lỗi", message)
