from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
import asyncio

class UserProfileWindow(QtWidgets.QDialog):
    """Window to display user profile information"""
    
    def __init__(self, user_data, current_user_id, client, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.current_user_id = current_user_id
        self.client = client
        self.user_id = user_data.get('user_id') or user_data.get('friend_id')
        self.username = user_data.get('username') or user_data.get('friend_name')
        self.profile_data = {}
        self.mutual_groups = []
        
        self.setWindowTitle(f"Thông tin tài khoản - {self.username}")
        self.setFixedSize(450, 650)
        self.setModal(True)
        
        # Set window flags
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.WindowTitleHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint
        )
        
        self._setup_ui()
        
        # Load profile data on startup
        asyncio.create_task(self._load_profile_data())
        
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with close button
        header_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("👤 Thông tin tài khoản")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
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
        
        # Main content area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(20)
        
        self._create_profile_sections()
        
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
        
    def _create_profile_sections(self):
        """Create all profile sections"""
        # Avatar and basic info section
        self._create_avatar_section()
        
        # Personal information section
        self._create_personal_info_section()
        
        # Mutual groups section
        self._create_mutual_groups_section()
        
        # Action buttons section
        self._create_action_buttons_section()
        
    def _create_avatar_section(self):
        """Create avatar and basic info section"""
        avatar_frame = QtWidgets.QFrame()
        avatar_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        avatar_layout = QtWidgets.QVBoxLayout(avatar_frame)
        avatar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Avatar placeholder
        self.avatar_label = QtWidgets.QLabel("👤")
        self.avatar_label.setFixedSize(120, 120)
        self.avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 3px solid #3498db;
                border-radius: 60px;
                background-color: #ecf0f1;
                font-size: 48px;
            }
        """)
        avatar_layout.addWidget(self.avatar_label)
        
        # Username
        self.username_label = QtWidgets.QLabel(f"@{self.username}")
        self.username_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.username_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        avatar_layout.addWidget(self.username_label)
        
        # Display name
        self.display_name_label = QtWidgets.QLabel("Đang tải...")
        self.display_name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.display_name_label.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-bottom: 10px;")
        avatar_layout.addWidget(self.display_name_label)
        
        self.content_layout.addWidget(avatar_frame)
        
    def _create_personal_info_section(self):
        """Create personal information section"""
        info_frame = QtWidgets.QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        info_layout = QtWidgets.QVBoxLayout(info_frame)
        
        # Section title
        info_title = QtWidgets.QLabel("📋 Thông tin cá nhân")
        info_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495e; margin-bottom: 10px;")
        info_layout.addWidget(info_title)
        
        # Bio
        self.bio_label = QtWidgets.QLabel("💬 Giới thiệu:")
        self.bio_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        info_layout.addWidget(self.bio_label)
        
        self.bio_content = QtWidgets.QLabel("Đang tải...")
        self.bio_content.setWordWrap(True)
        self.bio_content.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; padding: 8px; background-color: #f8f9fa; border-radius: 6px;")
        info_layout.addWidget(self.bio_content)
        
        # Personal details in grid
        details_layout = QtWidgets.QGridLayout()
        details_layout.setSpacing(10)
        
        # Gender
        gender_label = QtWidgets.QLabel("👤 Giới tính:")
        gender_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.gender_value = QtWidgets.QLabel("Đang tải...")
        self.gender_value.setStyleSheet("color: #7f8c8d;")
        details_layout.addWidget(gender_label, 0, 0)
        details_layout.addWidget(self.gender_value, 0, 1)
        
        # Birth date
        birth_label = QtWidgets.QLabel("🎂 Sinh nhật:")
        birth_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.birth_value = QtWidgets.QLabel("Đang tải...")
        self.birth_value.setStyleSheet("color: #7f8c8d;")
        details_layout.addWidget(birth_label, 1, 0)
        details_layout.addWidget(self.birth_value, 1, 1)
        
        # Location
        location_label = QtWidgets.QLabel("📍 Khu vực:")
        location_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.location_value = QtWidgets.QLabel("Đang tải...")
        self.location_value.setStyleSheet("color: #7f8c8d;")
        details_layout.addWidget(location_label, 2, 0)
        details_layout.addWidget(self.location_value, 2, 1)
        
        # Email
        email_label = QtWidgets.QLabel("📧 Email:")
        email_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.email_value = QtWidgets.QLabel("Đang tải...")
        self.email_value.setStyleSheet("color: #7f8c8d;")
        details_layout.addWidget(email_label, 3, 0)
        details_layout.addWidget(self.email_value, 3, 1)
        
        info_layout.addLayout(details_layout)
        self.content_layout.addWidget(info_frame)
        
    def _create_mutual_groups_section(self):
        """Create mutual groups section"""
        groups_frame = QtWidgets.QFrame()
        groups_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        groups_layout = QtWidgets.QVBoxLayout(groups_frame)
        
        # Section title
        groups_title = QtWidgets.QLabel("👥 Nhóm chung")
        groups_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495e; margin-bottom: 10px;")
        groups_layout.addWidget(groups_title)
        
        # Groups list
        self.groups_list_widget = QtWidgets.QListWidget()
        self.groups_list_widget.setMaximumHeight(150)
        self.groups_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #e1e8ed;
                border-radius: 6px;
                background-color: #f8f9fa;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e1e8ed;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        groups_layout.addWidget(self.groups_list_widget)
        
        # Status label for groups
        self.groups_status_label = QtWidgets.QLabel("Đang tải nhóm chung...")
        self.groups_status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        groups_layout.addWidget(self.groups_status_label)
        
        self.content_layout.addWidget(groups_frame)
        
    def _create_action_buttons_section(self):
        """Create action buttons section"""
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # Send message button
        self.message_btn = QtWidgets.QPushButton("💬 Nhắn tin")
        self.message_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.message_btn.clicked.connect(self._send_message)
        
        # Add friend button (only show if not friends)
        self.friend_btn = QtWidgets.QPushButton("➕ Kết bạn")
        self.friend_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.friend_btn.clicked.connect(self._send_friend_request)
        
        actions_layout.addWidget(self.message_btn)
        actions_layout.addWidget(self.friend_btn)
        actions_layout.addStretch()
        
        self.content_layout.addLayout(actions_layout)
        
    async def _load_profile_data(self):
        """Load complete profile data"""
        try:
            # Load basic profile information
            profile_response = await self.client.send_request("get_user_profile", {
                "user_id": self.user_id
            })
            
            print(f"[DEBUG] Profile response: {profile_response}")
            
            if profile_response and profile_response.get("status") == "ok":
                self.profile_data = profile_response.get("data", {})
                self._update_profile_display()
            else:
                self._show_error("Không thể tải thông tin cá nhân")
                
            # Load mutual groups
            await self._load_mutual_groups()
            
        except Exception as e:
            print(f"[ERROR] Exception loading profile: {e}")
            self._show_error("Lỗi kết nối")
            
    def _update_profile_display(self):
        """Update UI with profile data"""
        profile = self.profile_data
        
        # Update display name
        display_name = profile.get('display_name', '') or profile.get('username', self.username)
        self.display_name_label.setText(display_name)
        
        # Update bio
        bio = profile.get('bio', '') or "Chưa có giới thiệu"
        self.bio_content.setText(bio)
        
        # Update gender
        gender_map = {
            'male': 'Nam',
            'female': 'Nữ', 
            'other': 'Khác',
            'not_specified': 'Không xác định'
        }
        gender = gender_map.get(profile.get('gender', 'not_specified'), 'Không xác định')
        self.gender_value.setText(gender)
        
        # Update birth date
        birth_date = profile.get('birth_date') or "Không cung cấp"
        self.birth_value.setText(str(birth_date))
        
        # Update location
        location = profile.get('location', '') or "Không cung cấp"
        self.location_value.setText(location)
        
        # Update email
        email = profile.get('email', '') or "Không cung cấp"
        self.email_value.setText(email)
        
    async def _load_mutual_groups(self):
        """Load mutual groups"""
        try:
            groups_response = await self.client.send_request("get_mutual_groups", {
                "user1_id": self.current_user_id,
                "user2_id": self.user_id
            })
            
            print(f"[DEBUG] Mutual groups response: {groups_response}")
            
            if groups_response and groups_response.get("status") == "ok":
                self.mutual_groups = groups_response.get("data", [])
                self._update_groups_display()
            else:
                self.groups_status_label.setText("Không có nhóm chung")
                
        except Exception as e:
            print(f"[ERROR] Exception loading mutual groups: {e}")
            self.groups_status_label.setText("Lỗi tải nhóm chung")
            
    def _update_groups_display(self):
        """Update groups list display"""
        self.groups_list_widget.clear()
        
        if not self.mutual_groups:
            self.groups_status_label.setText("Không có nhóm chung")
            return
            
        for group in self.mutual_groups:
            group_name = group.get('group_name', 'Unknown Group')
            member_count = group.get('member_count', 0)
            
            item_text = f"👥 {group_name} ({member_count} thành viên)"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, group)
            self.groups_list_widget.addItem(item)
            
        count = len(self.mutual_groups)
        self.groups_status_label.setText(f"Có {count} nhóm chung")
        
    def _show_error(self, message):
        """Show error message"""
        self.display_name_label.setText("Lỗi tải dữ liệu")
        self.bio_content.setText(message)
        self.gender_value.setText("N/A")
        self.birth_value.setText("N/A")
        self.location_value.setText("N/A")
        self.email_value.setText("N/A")
        
    def _send_message(self):
        """Handle send message button"""
        # Create chat data and emit signal to parent
        chat_data = {
            'friend_id': self.user_id,
            'friend_name': self.username,
            'current_user_id': self.current_user_id,
            'last_message': '',
            'last_message_time': '',
            'unread_count': 0
        }
        
        # Find parent main window and open chat
        parent_window = self.parent()
        while parent_window and not hasattr(parent_window, '_open_chat_window_1v1'):
            parent_window = parent_window.parent()
            
        if parent_window and hasattr(parent_window, '_open_chat_window_1v1'):
            parent_window._open_chat_window_1v1(chat_data)
            self.close()
        else:
            QtWidgets.QMessageBox.information(self, "Thông báo", "Không thể mở cửa sổ chat")
            
    def _send_friend_request(self):
        """Handle send friend request button"""
        # TODO: Implement friend request logic
        QtWidgets.QMessageBox.information(self, "Thông báo", f"Đã gửi lời mời kết bạn tới {self.username}")
        self.friend_btn.setText("📤 Đã gửi")
        self.friend_btn.setEnabled(False)
