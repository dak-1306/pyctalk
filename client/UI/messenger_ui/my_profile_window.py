from PyQt6 import QtCore, QtWidgets, QtGui
import asyncio

class MyProfileWindow(QtWidgets.QDialog):
    """Window to display and edit current user's profile"""
    
    def __init__(self, client, user_id, username, parent=None):
        super().__init__(parent)
        self.client = client
        self.user_id = user_id
        self.username = username
        self.profile_data = {}
        
        self.setWindowTitle(f"Hồ sơ của {username}")
        self.setFixedSize(600, 700)
        self.setWindowFlags(QtCore.Qt.WindowType.Dialog | QtCore.Qt.WindowType.WindowCloseButtonHint)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 12px;
            }
        """)
        
        self._setup_ui()
        
        # Load profile data on startup
        asyncio.create_task(self._load_profile_data())
        
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with title and close button
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QtWidgets.QLabel("👤 Hồ sơ của tôi")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        
        close_btn = QtWidgets.QPushButton("✖")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
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
        
        # Main content area
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                margin: 0px 15px 15px 15px;
            }
        """)
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Create profile sections
        self._create_profile_sections(content_layout)
        
        layout.addWidget(content_widget)
        
        # Footer with action buttons
        self._create_footer_buttons(layout)
        
    def _create_profile_sections(self, layout):
        """Create all profile sections"""
        # Avatar and basic info section
        self._create_avatar_section(layout)
        
        # Personal information section
        self._create_personal_info_section(layout)
        
        # Account settings section
        self._create_account_section(layout)
        
    def _create_avatar_section(self, layout):
        """Create avatar and basic info section"""
        avatar_frame = QtWidgets.QFrame()
        avatar_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        avatar_layout = QtWidgets.QVBoxLayout(avatar_frame)
        avatar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Avatar
        self.avatar_label = QtWidgets.QLabel()
        avatar_pixmap = QtGui.QPixmap(80, 80)
        avatar_pixmap.fill(QtGui.QColor("#6366f1"))
        self.avatar_label.setPixmap(avatar_pixmap)
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border-radius: 40px;
                border: 3px solid white;
                background-color: #6366f1;
            }
        """)
        self.avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(self.avatar_label)
        
        # Username
        self.username_display = QtWidgets.QLabel(f"@{self.username}")
        self.username_display.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 10px;
            }
        """)
        self.username_display.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(self.username_display)
        
        # Status
        self.status_label = QtWidgets.QLabel("🟢 Trực tuyến")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #27ae60;
                margin-bottom: 10px;
            }
        """)
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(self.status_label)
        
        # Change avatar button
        change_avatar_btn = QtWidgets.QPushButton("📷 Đổi ảnh đại diện")
        change_avatar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        change_avatar_btn.clicked.connect(self._change_avatar)
        avatar_layout.addWidget(change_avatar_btn)
        
        layout.addWidget(avatar_frame)
        
    def _create_personal_info_section(self, layout):
        """Create personal information section"""
        info_frame = QtWidgets.QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        info_layout = QtWidgets.QVBoxLayout(info_frame)
        
        # Section title
        title_label = QtWidgets.QLabel("📝 Thông tin cá nhân")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        info_layout.addWidget(title_label)
        
        # Create form fields
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)
        
        # Style for form labels
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        
        # Display name
        self.display_name_input = QtWidgets.QLineEdit()
        self.display_name_input.setPlaceholderText("Tên hiển thị...")
        self._style_input(self.display_name_input)
        form_layout.addRow("Tên hiển thị:", self.display_name_input)
        
        # Bio
        self.bio_input = QtWidgets.QTextEdit()
        self.bio_input.setPlaceholderText("Giới thiệu về bản thân...")
        self.bio_input.setMaximumHeight(60)
        self._style_input(self.bio_input)
        form_layout.addRow("Tiểu sử:", self.bio_input)
        
        # Phone
        self.phone_input = QtWidgets.QLineEdit()
        self.phone_input.setPlaceholderText("Số điện thoại...")
        self._style_input(self.phone_input)
        form_layout.addRow("Điện thoại:", self.phone_input)
        
        # Location
        self.location_input = QtWidgets.QLineEdit()
        self.location_input.setPlaceholderText("Địa chỉ...")
        self._style_input(self.location_input)
        form_layout.addRow("Địa chỉ:", self.location_input)
        
        # Gender
        self.gender_combo = QtWidgets.QComboBox()
        self.gender_combo.addItems(["Không xác định", "Nam", "Nữ", "Khác"])
        self._style_input(self.gender_combo)
        form_layout.addRow("Giới tính:", self.gender_combo)
        
        # Birth date
        self.birth_date_edit = QtWidgets.QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDate(QtCore.QDate.currentDate())
        self._style_input(self.birth_date_edit)
        form_layout.addRow("Ngày sinh:", self.birth_date_edit)
        
        info_layout.addLayout(form_layout)
        layout.addWidget(info_frame)
        
    def _create_account_section(self, layout):
        """Create account settings section"""
        account_frame = QtWidgets.QFrame()
        account_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        account_layout = QtWidgets.QVBoxLayout(account_frame)
        
        # Section title
        title_label = QtWidgets.QLabel("⚙️ Cài đặt tài khoản")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        account_layout.addWidget(title_label)
        
        # Account info
        info_layout = QtWidgets.QVBoxLayout()
        
        username_info = QtWidgets.QLabel(f"Tên đăng nhập: {self.username}")
        username_info.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 5px 0;")
        info_layout.addWidget(username_info)
        
        user_id_info = QtWidgets.QLabel(f"ID người dùng: {self.user_id}")
        user_id_info.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 5px 0;")
        info_layout.addWidget(user_id_info)
        
        # Change password button
        change_password_btn = QtWidgets.QPushButton("🔑 Đổi mật khẩu")
        change_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        change_password_btn.clicked.connect(self._change_password)
        info_layout.addWidget(change_password_btn)
        
        account_layout.addLayout(info_layout)
        layout.addWidget(account_frame)
        
    def _create_footer_buttons(self, layout):
        """Create footer action buttons"""
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.setContentsMargins(20, 10, 20, 20)
        
        # Save button
        save_btn = QtWidgets.QPushButton("💾 Lưu thay đổi")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self._save_profile)
        
        # Cancel button  
        cancel_btn = QtWidgets.QPushButton("❌ Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        footer_layout.addStretch()
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(save_btn)
        layout.addLayout(footer_layout)
        
    def _style_input(self, widget):
        """Apply consistent styling to input widgets"""
        widget.setStyleSheet("""
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
            }
        """)
        
    async def _load_profile_data(self):
        """Load user profile data from server"""
        try:
            response = await self.client.send_request("get_user_profile", {
                "user_id": self.user_id
            })
            
            print(f"[DEBUG] Profile response: {response}")
            
            if response and response.get("success"):
                self.profile_data = response.get("profile", {})
                self._populate_fields()
            else:
                print(f"[DEBUG] Failed to load profile: {response}")
                # Set default values if no profile exists
                self._set_default_values()
                
        except Exception as e:
            print(f"[ERROR] Error loading profile: {e}")
            self._set_default_values()
            
    def _populate_fields(self):
        """Populate form fields with profile data"""
        # Basic info
        display_name = self.profile_data.get("display_name", self.username)
        self.display_name_input.setText(display_name)
        
        bio = self.profile_data.get("bio", "")
        self.bio_input.setPlainText(bio)
        
        phone = self.profile_data.get("phone", "")
        self.phone_input.setText(phone)
        
        location = self.profile_data.get("location", "")
        self.location_input.setText(location)
        
        # Gender
        gender = self.profile_data.get("gender", "")
        gender_index = 0  # Default: "Không xác định"
        if gender == "male":
            gender_index = 1
        elif gender == "female": 
            gender_index = 2
        elif gender == "other":
            gender_index = 3
        self.gender_combo.setCurrentIndex(gender_index)
        
        # Birth date
        birth_date = self.profile_data.get("birth_date")
        if birth_date:
            try:
                date = QtCore.QDate.fromString(birth_date, "yyyy-MM-dd")
                if date.isValid():
                    self.birth_date_edit.setDate(date)
            except:
                pass
                
    def _set_default_values(self):
        """Set default values when no profile data exists"""
        self.display_name_input.setText(self.username)
        
    async def _save_profile(self):
        """Save profile changes to server"""
        try:
            # Get gender value
            gender_map = ["", "male", "female", "other"]
            gender = gender_map[self.gender_combo.currentIndex()]
            
            # Prepare profile data
            profile_data = {
                "user_id": self.user_id,
                "display_name": self.display_name_input.text().strip(),
                "bio": self.bio_input.toPlainText().strip(),
                "phone": self.phone_input.text().strip(),
                "location": self.location_input.text().strip(),
                "gender": gender,
                "birth_date": self.birth_date_edit.date().toString("yyyy-MM-dd")
            }
            
            print(f"[DEBUG] Saving profile data: {profile_data}")
            
            response = await self.client.send_request("update_user_profile", profile_data)
            
            print(f"[DEBUG] Save profile response: {response}")
            
            if response and response.get("success"):
                QtWidgets.QMessageBox.information(self, "Thành công", "Cập nhật hồ sơ thành công!")
                self.close()
            else:
                error_msg = response.get("message", "Lỗi không xác định") if response else "Lỗi kết nối"
                QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật hồ sơ: {error_msg}")
                
        except Exception as e:
            print(f"[ERROR] Error saving profile: {e}")
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu hồ sơ: {str(e)}")
            
    def _change_avatar(self):
        """Handle avatar change"""
        QtWidgets.QMessageBox.information(
            self, 
            "Thông báo", 
            "Tính năng đổi ảnh đại diện sẽ được bổ sung trong phiên bản tiếp theo!"
        )
        
    def _change_password(self):
        """Handle password change"""
        QtWidgets.QMessageBox.information(
            self, 
            "Thông báo", 
            "Tính năng đổi mật khẩu sẽ được bổ sung trong phiên bản tiếp theo!"
        )
