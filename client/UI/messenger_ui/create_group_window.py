from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
import asyncio

class FriendSelectionItem(QtWidgets.QWidget):
    """Widget for selecting friends to add to group"""
    selection_changed = pyqtSignal(dict, bool)  # friend_data, is_selected
    
    def __init__(self, friend_data, parent=None):
        super().__init__(parent)
        self.friend_data = friend_data
        self.is_selected = False
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        
        # Checkbox
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.stateChanged.connect(self._on_selection_changed)
        layout.addWidget(self.checkbox)
        
        # Avatar placeholder
        avatar_label = QtWidgets.QLabel("👤")
        avatar_label.setFixedSize(35, 35)
        avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #3498db;
                border-radius: 17px;
                background-color: #ecf0f1;
                font-size: 16px;
            }
        """)
        layout.addWidget(avatar_label)
        
        # Friend name
        friend_name = self.friend_data.get('friend_name', 'Unknown')
        name_label = QtWidgets.QLabel(f"<b>{friend_name}</b>")
        name_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Add hover effect
        self.setStyleSheet("""
            FriendSelectionItem {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                margin: 1px;
            }
            FriendSelectionItem:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
        """)
        
    def set_selected(self, selected):
        """Programmatically set selection state"""
        self.checkbox.setChecked(selected)
        
    def is_checked(self):
        """Get current checkbox state"""
        return self.checkbox.isChecked()
        
    def _on_selection_changed(self, state):
        # Fix: So sánh với int value thay vì enum
        self.is_selected = state == QtCore.Qt.CheckState.Checked.value
        print(f"[DEBUG] Friend selection changed: {self.friend_data.get('friend_name')} = {self.is_selected}")
        print(f"[DEBUG] Checkbox state value: {state}, CheckState.Checked.value: {QtCore.Qt.CheckState.Checked.value}")
        print(f"[DEBUG] State comparison result: {state == QtCore.Qt.CheckState.Checked.value}")
        self.selection_changed.emit(self.friend_data, self.is_selected)
        
        # Update visual style based on selection
        if self.is_selected:
            self.setStyleSheet("""
                FriendSelectionItem {
                    border: 2px solid #3498db;
                    border-radius: 6px;
                    background-color: #e3f2fd;
                    margin: 1px;
                }
            """)
        else:
            self.setStyleSheet("""
                FriendSelectionItem {
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    background-color: white;
                    margin: 1px;
                }
                FriendSelectionItem:hover {
                    background-color: #f8f9fa;
                    border-color: #3498db;
                }
            """)

class CreateGroupWindow(QtWidgets.QDialog):
    """Window for creating a new group with friend selection"""
    group_created = pyqtSignal(dict)  # Emit when group is successfully created
    
    def __init__(self, client, username, user_id, parent=None):
        super().__init__(parent)
        self.client = client
        self.username = username
        self.user_id = user_id
        self.friends_list = []
        self.selected_friends = {}  # {friend_id: friend_data}
        
        self.setWindowTitle("Tạo nhóm mới")
        self.setFixedSize(500, 650)
        self.setModal(True)
        
        # Set window flags
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.WindowTitleHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        
        self._setup_ui()
        
        # Load friends on startup
        asyncio.create_task(self._load_friends())
        
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("🏗️ Tạo nhóm mới")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        # Group name input
        name_layout = QtWidgets.QVBoxLayout()
        name_label = QtWidgets.QLabel("📝 Tên nhóm:")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #34495e;")
        
        self.group_name_input = QtWidgets.QLineEdit()
        self.group_name_input.setPlaceholderText("Nhập tên nhóm...")
        self.group_name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.group_name_input.textChanged.connect(self._validate_form)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.group_name_input)
        layout.addLayout(name_layout)
        
        # Friends selection section
        friends_label = QtWidgets.QLabel("👥 Chọn bạn bè để thêm vào nhóm:")
        friends_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #34495e;")
        layout.addWidget(friends_label)
        
        # Info note
        info_label = QtWidgets.QLabel("💡 Chỉ có thể thêm những người đã kết bạn với bạn")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Search box for friends
        search_layout = QtWidgets.QHBoxLayout()
        search_icon = QtWidgets.QLabel("🔍")
        search_icon.setStyleSheet("font-size: 14px;")
        
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm bạn bè...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self._filter_friends)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Selection controls
        controls_layout = QtWidgets.QHBoxLayout()
        
        self.select_all_btn = QtWidgets.QPushButton("✅ Chọn tất cả")
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.select_all_btn.clicked.connect(self._select_all_friends)
        
        self.deselect_all_btn = QtWidgets.QPushButton("❌ Bỏ chọn tất cả")
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.deselect_all_btn.clicked.connect(self._deselect_all_friends)
        
        controls_layout.addWidget(self.select_all_btn)
        controls_layout.addWidget(self.deselect_all_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Friends list
        self.status_label = QtWidgets.QLabel("Đang tải danh sách bạn bè...")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        self.friends_container = QtWidgets.QWidget()
        self.friends_layout = QtWidgets.QVBoxLayout(self.friends_container)
        self.friends_layout.setContentsMargins(5, 5, 5, 5)
        self.friends_layout.setSpacing(5)
        self.friends_layout.addStretch()
        
        scroll_area.setWidget(self.friends_container)
        layout.addWidget(scroll_area)
        
        # Selected friends summary
        self.selected_summary = QtWidgets.QLabel("👥 Đã chọn: 0 bạn bè")
        self.selected_summary.setStyleSheet("font-weight: bold; color: #3498db; font-size: 13px; padding: 5px;")
        layout.addWidget(self.selected_summary)
        
        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("❌ Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        self.create_btn = QtWidgets.QPushButton("🏗️ Tạo nhóm")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.create_btn.clicked.connect(lambda: asyncio.create_task(self._create_group()))
        self.create_btn.setEnabled(False)  # Initially disabled
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.create_btn)
        layout.addLayout(button_layout)
        
    async def _load_friends(self):
        """Load friends from server"""
        try:
            self.status_label.setText("Đang tải...")
            
            response = await self.client.send_request("get_friends", {
                "username": self.username
            })
            
            print(f"[DEBUG] CreateGroup friends response: {response}")
            
            if response and response.get("status") == "ok":
                self.friends_list = response.get("data", [])
                self._display_friends(self.friends_list)
                
                if not self.friends_list:
                    self.status_label.setText("Bạn chưa có bạn bè nào để tạo nhóm")
                else:
                    self.status_label.setText(f"Có {len(self.friends_list)} bạn bè")
            else:
                self.status_label.setText("Lỗi tải dữ liệu")
                print(f"[ERROR] Failed to load friends: {response}")
                
        except Exception as e:
            self.status_label.setText("Lỗi kết nối")
            print(f"[ERROR] Exception loading friends: {e}")
            
    def _display_friends(self, friends):
        """Display friends in the UI"""
        print(f"[DEBUG] _display_friends called with {len(friends)} friends")
        
        # Clear existing items (except stretch)
        while self.friends_layout.count() > 1:
            item = self.friends_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add friend selection items
        for friend in friends:
            print(f"[DEBUG] Creating FriendSelectionItem for: {friend}")
            friend_item = FriendSelectionItem(friend)
            friend_item.selection_changed.connect(self._on_friend_selection_changed)
            self.friends_layout.insertWidget(self.friends_layout.count() - 1, friend_item)
            print(f"[DEBUG] Added FriendSelectionItem, signal connected")
            
        # Test: Programmatically select first friend for debugging
        if friends:
            QtCore.QTimer.singleShot(1000, self._test_select_first_friend)
            
    def _test_select_first_friend(self):
        """Test method to programmatically select first friend"""
        print("[DEBUG] Testing programmatic selection...")
        for i in range(self.friends_layout.count()):
            item = self.friends_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), FriendSelectionItem):
                friend_item = item.widget()
                print(f"[DEBUG] Testing selection for: {friend_item.friend_data.get('friend_name')}")
                friend_item.set_selected(True)
                break
            
    def _filter_friends(self, search_text):
        """Filter friends based on search text"""
        search_text = search_text.lower()
        
        # Find all FriendSelectionItem widgets
        for i in range(self.friends_layout.count()):
            item = self.friends_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), FriendSelectionItem):
                friend_item = item.widget()
                friend_name = friend_item.friend_data.get('friend_name', '').lower()
                
                # Show/hide based on search match
                is_visible = search_text in friend_name
                friend_item.setVisible(is_visible)
    
    def _select_all_friends(self):
        """Select all visible friends"""
        for i in range(self.friends_layout.count()):
            item = self.friends_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), FriendSelectionItem):
                friend_item = item.widget()
                if friend_item.isVisible():
                    friend_item.checkbox.setChecked(True)
    
    def _deselect_all_friends(self):
        """Deselect all friends"""
        for i in range(self.friends_layout.count()):
            item = self.friends_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), FriendSelectionItem):
                friend_item = item.widget()
                friend_item.checkbox.setChecked(False)
    
    def _on_friend_selection_changed(self, friend_data, is_selected):
        """Handle when a friend is selected/deselected"""
        friend_id = friend_data.get('friend_id')
        friend_name = friend_data.get('friend_name')
        
        print(f"[DEBUG] _on_friend_selection_changed: {friend_name} (ID: {friend_id}) = {is_selected}")
        
        if is_selected:
            self.selected_friends[friend_id] = friend_data
        else:
            self.selected_friends.pop(friend_id, None)
        
        # Update summary
        count = len(self.selected_friends)
        self.selected_summary.setText(f"👥 Đã chọn: {count} bạn bè")
        print(f"[DEBUG] Selected friends count: {count}")
        
        # Update form validation
        self._validate_form()
        
    def _validate_form(self):
        """Validate form and enable/disable create button"""
        group_name = self.group_name_input.text().strip()
        has_members = len(self.selected_friends) > 0
        
        is_valid = bool(group_name and has_members)
        print(f"[DEBUG] Form validation: group_name='{group_name}', has_members={has_members}, is_valid={is_valid}")
        
        self.create_btn.setEnabled(is_valid)
        
        if is_valid:
            self.create_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
        else:
            self.create_btn.setStyleSheet("""
                QPushButton {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        
    async def _create_group(self):
        """Create the group"""
        try:
            group_name = self.group_name_input.text().strip()
            
            if not group_name:
                QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên nhóm")
                return
                
            if not self.selected_friends:
                QtWidgets.QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất một bạn bè")
                return
            
            # Disable button during creation
            self.create_btn.setEnabled(False)
            self.create_btn.setText("⏳ Đang tạo...")
            
            # Create group
            response = await self.client.send_request("create_group", {
                "group_name": group_name,
                "user_id": self.user_id
            })
            
            print(f"[DEBUG] Create group response: {response}")
            
            if response and response.get("status") == "ok":
                group_id = response.get("group_id")
                
                # Add selected friends to the group
                successful_adds = 0
                failed_adds = []
                
                for friend_id, friend_data in self.selected_friends.items():
                    try:
                        add_response = await self.client.send_request("add_user_to_group", {
                            "group_id": group_id,
                            "user_id": friend_id
                        })
                        
                        if add_response and add_response.get("status") == "ok":
                            successful_adds += 1
                        else:
                            failed_adds.append(friend_data.get('friend_name', 'Unknown'))
                            
                    except Exception as e:
                        print(f"[ERROR] Failed to add {friend_data.get('friend_name')} to group: {e}")
                        failed_adds.append(friend_data.get('friend_name', 'Unknown'))
                
                # Show result
                if successful_adds > 0:
                    message = f"✅ Đã tạo nhóm '{group_name}' thành công!\n"
                    message += f"Đã thêm {successful_adds} thành viên."
                    
                    if failed_adds:
                        message += f"\nKhông thể thêm: {', '.join(failed_adds)}"
                    
                    QtWidgets.QMessageBox.information(self, "Thành công", message)
                    
                    # Emit signal and close
                    self.group_created.emit({
                        "group_id": group_id,
                        "group_name": group_name,
                        "member_count": successful_adds + 1  # +1 for creator
                    })
                    self.close()
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "Cảnh báo", 
                        f"Đã tạo nhóm '{group_name}' nhưng không thể thêm thành viên nào.\nBạn có thể thêm thành viên sau."
                    )
                    self.close()
                    
            else:
                error_msg = response.get("message", "Không thể tạo nhóm") if response else "Lỗi kết nối"
                QtWidgets.QMessageBox.critical(self, "Lỗi", f"Tạo nhóm thất bại: {error_msg}")
                
        except Exception as e:
            print(f"[ERROR] Exception creating group: {e}")
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối: {str(e)}")
            
        finally:
            # Re-enable button
            self.create_btn.setEnabled(True)
            self.create_btn.setText("🏗️ Tạo nhóm")
