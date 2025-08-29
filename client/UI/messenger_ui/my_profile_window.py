from PyQt6 import QtCore, QtWidgets, QtGui
import asyncio
import base64
import os

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
        self._create_avatar_section(form_layout)
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
        
    def _create_avatar_section(self, layout):
        """Create avatar upload section"""
        # Avatar container
        avatar_container = QtWidgets.QWidget()
        avatar_layout = QtWidgets.QVBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setSpacing(10)
        avatar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Avatar display
        self.avatar_label = QtWidgets.QLabel()
        self.avatar_label.setFixedSize(120, 120)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 3px solid #e0e0e0;
                border-radius: 60px;
                background-color: #f8f9fa;
            }
        """)
        self.avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setText("👤")
        self.avatar_label.setFont(QtGui.QFont("Arial", 40))
        
        # Buttons container
        buttons_container = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)
        
        # Upload button
        self.upload_btn = QtWidgets.QPushButton("📁 Chọn ảnh")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        self.upload_btn.clicked.connect(self._select_avatar)
        
        # Delete button
        self.delete_btn = QtWidgets.QPushButton("🗑️ Xóa")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.delete_btn.clicked.connect(self._delete_avatar)
        self.delete_btn.setEnabled(False)  # Disabled by default
        
        buttons_layout.addWidget(self.upload_btn)
        buttons_layout.addWidget(self.delete_btn)
        
        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addWidget(buttons_container)
        
        layout.addRow("🖼️ Ảnh đại diện:", avatar_container)
        
        # Store avatar data
        self.avatar_data = None
        self.avatar_filename = None
        
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
        
        # Avatar
        avatar_url = self.profile_data.get("avatar_url")
        if avatar_url:
            # Load avatar from server
            asyncio.create_task(self._load_avatar_from_url(avatar_url))
            self.delete_btn.setEnabled(True)
            print(f"[DEBUG] User has avatar: {avatar_url}")
        else:
            self.delete_btn.setEnabled(False)
        
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
            asyncio.create_task(self._save_profile_async(profile_data))
            
        except Exception as e:
            print(f"[ERROR] Error saving profile: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể lưu hồ sơ: {e}")

    async def _save_profile_async(self, profile_data):
        """Async method to save profile and upload avatar"""
        try:
            # Upload avatar first if there's new avatar data
            if self.avatar_data:
                avatar_response = await self._upload_avatar_to_server()
                if avatar_response.get('status') != 'ok':
                    QtWidgets.QMessageBox.warning(
                        self, "Lỗi", 
                        f"Không thể upload avatar: {avatar_response.get('message', 'Lỗi không xác định')}"
                    )
                    return
            
            # Then save profile data
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
            print(f"[ERROR] Error saving profile: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể kết nối server: {e}")
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

    def _select_avatar(self):
        """Select avatar image file"""
        try:
            file_dialog = QtWidgets.QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "Chọn ảnh đại diện",
                "",
                "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"
            )
            
            if file_path:
                # Load and display image
                pixmap = QtGui.QPixmap(file_path)
                if not pixmap.isNull():
                    # Scale to fit
                    scaled_pixmap = pixmap.scaled(
                        120, 120,
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    )
                    
                    # Create circular mask
                    mask = QtGui.QPixmap(120, 120)
                    mask.fill(QtCore.Qt.GlobalColor.transparent)
                    
                    painter = QtGui.QPainter(mask)
                    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                    painter.drawEllipse(0, 0, 120, 120)
                    painter.end()
                    
                    # Apply mask
                    scaled_pixmap.setMask(mask.createMaskFromColor(QtCore.Qt.GlobalColor.transparent))
                    
                    self.avatar_label.setPixmap(scaled_pixmap)
                    self.avatar_label.setText("")  # Clear text
                    
                    # Store file data
                    self.avatar_filename = os.path.basename(file_path)
                    
                    # Read file as base64
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        self.avatar_data = base64.b64encode(file_data).decode('utf-8')
                    
                    # Enable delete button
                    self.delete_btn.setEnabled(True)
                    
                    print(f"[DEBUG] Avatar selected: {file_path}")
                else:
                    QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể tải ảnh. Vui lòng chọn file ảnh hợp lệ.")
                    
        except Exception as e:
            print(f"[ERROR] Error selecting avatar: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể chọn ảnh: {e}")

    def _delete_avatar(self):
        """Delete current avatar"""
        try:
            # Reset to default
            self.avatar_label.clear()
            self.avatar_label.setText("👤")
            self.avatar_label.setFont(QtGui.QFont("Arial", 40))
            
            # Clear data
            self.avatar_data = None
            self.avatar_filename = None
            
            # Disable delete button
            self.delete_btn.setEnabled(False)
            
            print("[DEBUG] Avatar deleted locally")
            
        except Exception as e:
            print(f"[ERROR] Error deleting avatar: {e}")

    async def _load_avatar_from_url(self, avatar_url):
        """Load avatar image from URL"""
        try:
            print(f"[DEBUG] Loading avatar from URL: {avatar_url}")

            # For now, since we don't have a web server running, we'll just show a placeholder
            # In a real implementation, you would fetch the image from the server
            # For example:
            # import requests
            # response = requests.get(f"http://localhost:8080{avatar_url}")
            # if response.status_code == 200:
            #     image_data = response.content
            #     # Process and display the image

            # For demonstration, we'll just update the UI to show that an avatar exists
            self.avatar_label.setText("📷")  # Camera emoji to indicate avatar exists
            self.avatar_label.setFont(QtGui.QFont("Arial", 40))
            self.avatar_label.setStyleSheet("""
                QLabel {
                    border: 3px solid #4CAF50;
                    border-radius: 60px;
                    background-color: #f8f9fa;
                    color: #4CAF50;
                }
            """)

            print(f"[DEBUG] Avatar placeholder displayed for URL: {avatar_url}")

        except Exception as e:
            print(f"[ERROR] Error loading avatar from URL: {e}")
            # Fallback to default
            self.avatar_label.setText("👤")
            self.avatar_label.setFont(QtGui.QFont("Arial", 40))
            self.avatar_label.setStyleSheet("""
                QLabel {
                    border: 3px solid #e0e0e0;
                    border-radius: 60px;
                    background-color: #f8f9fa;
                }
            """)

    async def _upload_avatar_to_server(self):
        """Upload avatar to server"""
        try:
            if not self.avatar_data or not self.avatar_filename:
                return {"status": "ok"}  # No avatar to upload
                
            print(f"[DEBUG] Uploading avatar for user_id: {self.user_id}")
            
            response = await self.client.send_json({
                'action': 'upload_avatar',
                'data': {
                    'user_id': self.user_id,
                    'avatar_data': self.avatar_data,
                    'filename': self.avatar_filename
                }
            })
            
            print(f"[DEBUG] Upload avatar response: {response}")
            return response
            
        except Exception as e:
            print(f"[ERROR] Error uploading avatar: {e}")
            return {"status": "error", "message": str(e)}
