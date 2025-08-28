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
        self.setFixedSize(500, 650)
        self.setWindowFlags(QtCore.Qt.WindowType.Dialog | QtCore.Qt.WindowType.WindowCloseButtonHint)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        
        self._setup_ui()
        
        # Load profile data on startup
        QtCore.QTimer.singleShot(100, lambda: asyncio.create_task(self._load_profile_data()))
        
    def _setup_ui(self):
        """Setup the UI components"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_label = QtWidgets.QLabel("👤 Hồ sơ của tôi")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
            }
        """)
        header_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Scroll area for form content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
                border-radius: 6px;
            }
        """)
        
        # Form widget
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_widget)
        form_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(10)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create form fields
        self._create_form_fields(form_layout)
        
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        save_btn = QtWidgets.QPushButton("💾 Lưu thay đổi")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self._save_profile)
        
        cancel_btn = QtWidgets.QPushButton("❌ Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)
        
    def _create_form_fields(self, layout):
        """Create form input fields"""
        # Username (read-only)
        username_input = QtWidgets.QLineEdit(f"@{self.username}")
        username_input.setReadOnly(True)
        self._style_input(username_input, readonly=True)
        layout.addRow("👤 Tên người dùng:", username_input)
        
        # Display name
        self.display_name_input = QtWidgets.QLineEdit()
        self._style_input(self.display_name_input)
        layout.addRow("📝 Tên hiển thị:", self.display_name_input)
        
        # Email
        self.email_input = QtWidgets.QLineEdit()
        self._style_input(self.email_input)
        layout.addRow("📧 Email:", self.email_input)
        
        # Bio
        self.bio_input = QtWidgets.QTextEdit()
        self.bio_input.setMaximumHeight(80)
        self._style_input(self.bio_input)
        layout.addRow("📖 Giới thiệu:", self.bio_input)
        
        # Gender
        self.gender_combo = QtWidgets.QComboBox()
        self.gender_combo.addItems(["Chọn giới tính", "Nam", "Nữ", "Khác"])
        self._style_input(self.gender_combo)
        layout.addRow("⚧ Giới tính:", self.gender_combo)
        
        # Phone
        self.phone_input = QtWidgets.QLineEdit()
        self._style_input(self.phone_input)
        layout.addRow("📱 Số điện thoại:", self.phone_input)
        
        # Location
        self.location_input = QtWidgets.QLineEdit()
        self._style_input(self.location_input)
        layout.addRow("📍 Địa điểm:", self.location_input)
        
        # Birth date
        self.birth_date_input = QtWidgets.QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QtCore.QDate.currentDate())
        self._style_input(self.birth_date_input)
        layout.addRow("🎂 Ngày sinh:", self.birth_date_input)
        
    def _style_input(self, widget, readonly=False):
        """Apply consistent styling to input widgets"""
        if readonly:
            style = """
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: #ecf0f1;
                    font-size: 13px;
                    color: #7f8c8d;
                }
            """
        else:
            style = """
                QLineEdit, QTextEdit, QComboBox, QDateEdit {
                    padding: 8px;
                    border: 2px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: white;
                    font-size: 13px;
                    color: #2c3e50;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                    border-color: #3498db;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #7f8c8d;
                    margin-right: 5px;
                }
            """
        widget.setStyleSheet(style)

    async def _load_profile_data(self):
        """Load profile data from server"""
        try:
            print(f"[DEBUG] Loading profile for user_id: {self.user_id}")
            
            response = await self.client.send_json({
                'action': 'get_user_profile',
                'data': {'user_id': self.user_id}
            })
            
            print(f"[DEBUG] Profile response: {response}")
            
            if response and response.get('status') == 'ok':
                self.profile_data = response.get('data', {})
                self._populate_fields()
            else:
                print(f"[ERROR] Failed to load profile: {response}")
                
        except Exception as e:
            print(f"[ERROR] Error loading profile: {e}")
            
    def _populate_fields(self):
        """Populate form fields with profile data"""
        print(f"[DEBUG] _populate_fields called with data: {self.profile_data}")
        
        # Display name
        display_name = self.profile_data.get("display_name", self.username)
        print(f"[DEBUG] Setting display_name: {display_name}")
        self.display_name_input.setText(display_name)
        
        # Email
        email = self.profile_data.get("email", "")
        self.email_input.setText(email)
        
        # Bio
        bio = self.profile_data.get("bio", "")
        self.bio_input.setPlainText(bio)
        
        # Phone
        phone = self.profile_data.get("phone", "")
        self.phone_input.setText(phone)
        
        # Location
        location = self.profile_data.get("location", "")
        self.location_input.setText(location)
        
        # Gender
        gender = self.profile_data.get("gender", "")
        gender_index = 0  # Default: "Chọn giới tính"
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
                # Parse date string to QDate
                if isinstance(birth_date, str):
                    # Assuming format: YYYY-MM-DD
                    year, month, day = birth_date.split('-')
                    qdate = QtCore.QDate(int(year), int(month), int(day))
                    self.birth_date_input.setDate(qdate)
            except Exception as e:
                print(f"[DEBUG] Error parsing birth_date: {e}")
        
        print("[DEBUG] _populate_fields completed")

    def _save_profile(self):
        """Save profile changes"""
        try:
            # Collect form data
            profile_data = {
                'user_id': self.user_id,
                'display_name': self.display_name_input.text().strip(),
                'email': self.email_input.text().strip(),
                'bio': self.bio_input.toPlainText().strip(),
                'phone': self.phone_input.text().strip(),
                'location': self.location_input.text().strip(),
            }
            
            # Gender
            gender_map = {0: "", 1: "male", 2: "female", 3: "other"}
            profile_data['gender'] = gender_map.get(self.gender_combo.currentIndex(), "")
            
            # Birth date
            birth_date = self.birth_date_input.date()
            if birth_date != QtCore.QDate.currentDate():
                profile_data['birth_date'] = birth_date.toString("yyyy-MM-dd")
            else:
                profile_data['birth_date'] = ""
            
            print(f"[DEBUG] Saving profile data: {profile_data}")
            
            # Create async task to save data
            asyncio.create_task(self._send_save_request(profile_data))
            
        except Exception as e:
            print(f"[ERROR] Error saving profile: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể lưu hồ sơ: {e}")

    async def _send_save_request(self, profile_data):
        """Send save request to server"""
        try:
            response = await self.client.send_json({
                'action': 'update_user_profile',
                'data': profile_data
            })
            
            print(f"[DEBUG] Save response: {response}")
            
            if response and response.get('status') == 'ok':
                QtWidgets.QMessageBox.information(self, "Thành công", "Hồ sơ đã được cập nhật!")
                self.accept()  # Close dialog
            else:
                error_msg = response.get('message', 'Lỗi không xác định') if response else 'Không có phản hồi từ server'
                QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể lưu hồ sơ: {error_msg}")
                
        except Exception as e:
            print(f"[ERROR] Error sending save request: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể kết nối server: {e}")
