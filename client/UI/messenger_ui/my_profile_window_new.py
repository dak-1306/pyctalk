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
        
        # Load profile data on startup - use QTimer to ensure UI is ready
        QtCore.QTimer.singleShot(100, lambda: asyncio.create_task(self._load_profile_data()))
        
    def _setup_ui(self):
        """Setup the UI components"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header
        header_label = QtWidgets.QLabel("👤 Hồ sơ của tôi")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
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
            }
        """)
        
        # Form widget
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_widget)
        form_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)
        
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
                padding: 12px 24px;
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
                padding: 12px 24px;
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

    def _style_input(self, widget):
        """Apply consistent styling to input widgets"""
        if isinstance(widget, QtWidgets.QTextEdit):
            widget.setStyleSheet("""
                QTextEdit {
                    border: 2px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                QTextEdit:focus {
                    border-color: #3498db;
                }
            """)
        else:
            widget.setStyleSheet("""
                QLineEdit, QComboBox, QDateEdit {
                    border: 2px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                    min-height: 20px;
                }
                QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                    border-color: #3498db;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAKCAYAAACE2W/HAAABLUlEQVQoFY2RMU7DQBBFX2xhQ0FBQ4FCg+AEcAK4ABJwoEEiJSJSUqSgpOEacANOABdA4hKcgIqCBomEhISEB3k2O96xN5L/zO/Z987/Z9dJ0zQ2m81Gq9VKdJ1zbtO27UJVVcvdbhdN03QtJMuyP6Wlrutcuz0xTZN935/E1go+A1IqldbVT8qUvgUhpNZi3ZdP8dPsLGVZJqRzOSCj1MuI6dFWKwCxL2xvb4/H4/FsNPr4cDgs57nOOVf2fW/F48yx6gFo73y/r8bj8TLnp4v1et2aPVEWi2VdXV1/d4vL2dRqPp83q6vQI/zcFMtms1mzuAgKgGlqQ1EUQ1VZr9frZrPZfOOJSDFcJPqfkj0xjOuVyWQyXSwWs9VqNePffPa9/AOYn9e6Tf5AAAAAAABJRU5ErkJggg==);
                }
            """)

    async def _load_profile_data(self):
        """Load profile data from server"""
        try:
            print(f"[DEBUG] Loading profile for user ID: {self.user_id}")
            
            # Request profile data from server
            response = await self.client.send_json({
                'action': 'get_user_profile',
                'data': {'user_id': self.user_id}
            })
            
            print(f"[DEBUG] Profile response: {response}")
            
            if response and response.get('status') == 'ok':
                self.profile_data = response.get('data', {})
                self._populate_fields(self.profile_data)
            else:
                print(f"[DEBUG] Failed to load profile: {response}")
                # Show error message
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Lỗi", 
                    "Không thể tải thông tin hồ sơ. Vui lòng thử lại."
                )
                
        except Exception as e:
            print(f"[DEBUG] Exception loading profile: {e}")
            QtWidgets.QMessageBox.critical(
                self, 
                "Lỗi", 
                f"Đã xảy ra lỗi khi tải hồ sơ: {str(e)}"
            )

    def _populate_fields(self, data):
        """Populate form fields with profile data"""
        print(f"[DEBUG] _populate_fields called with data: {data}")
        
        try:
            # Set display name
            display_name = data.get('display_name', '')
            print(f"[DEBUG] Setting display_name: {display_name}")
            self.display_name_input.setText(display_name)
            
            # Update username display in header if needed
            if display_name:
                print(f"[DEBUG] Updated username_display to: {display_name}")
            
            # Set email
            self.email_input.setText(data.get('email', ''))
            
            # Set bio
            self.bio_input.setPlainText(data.get('bio', ''))
            
            # Set gender
            gender = data.get('gender', '')
            if gender == 'male':
                self.gender_combo.setCurrentText("Nam")
            elif gender == 'female':
                self.gender_combo.setCurrentText("Nữ")
            elif gender == 'other':
                self.gender_combo.setCurrentText("Khác")
            else:
                self.gender_combo.setCurrentIndex(0)  # "Chọn giới tính"
            
            # Set phone
            self.phone_input.setText(data.get('phone', ''))
            
            # Set location
            self.location_input.setText(data.get('location', ''))
            
            # Set birth date
            birth_date = data.get('birth_date')
            if birth_date:
                try:
                    # Convert string date to QDate
                    if isinstance(birth_date, str):
                        date_parts = birth_date.split('-')
                        if len(date_parts) == 3:
                            year, month, day = map(int, date_parts)
                            qdate = QtCore.QDate(year, month, day)
                            self.birth_date_input.setDate(qdate)
                except Exception as e:
                    print(f"[DEBUG] Error parsing birth_date: {e}")
            
            print("[DEBUG] _populate_fields completed.")
            
        except Exception as e:
            print(f"[DEBUG] Error in _populate_fields: {e}")

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
            
            # Get gender
            gender_text = self.gender_combo.currentText()
            if gender_text == "Nam":
                profile_data['gender'] = 'male'
            elif gender_text == "Nữ":
                profile_data['gender'] = 'female'
            elif gender_text == "Khác":
                profile_data['gender'] = 'other'
            else:
                profile_data['gender'] = ''
            
            # Get birth date
            birth_date = self.birth_date_input.date()
            if birth_date != QtCore.QDate.currentDate():
                profile_data['birth_date'] = birth_date.toString("yyyy-MM-dd")
            else:
                profile_data['birth_date'] = ''
            
            print(f"[DEBUG] Saving profile data: {profile_data}")
            
            # TODO: Send update request to server
            # For now, just show success message
            QtWidgets.QMessageBox.information(
                self,
                "Thành công",
                "Hồ sơ đã được cập nhật thành công!"
            )
            
            self.accept()
            
        except Exception as e:
            print(f"[DEBUG] Error saving profile: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể lưu hồ sơ: {str(e)}"
            )

    def _change_avatar(self):
        """Handle avatar change"""
        # TODO: Implement avatar upload
        QtWidgets.QMessageBox.information(
            self,
            "Thông báo",
            "Tính năng đổi ảnh đại diện sẽ được cập nhật trong phiên bản sau."
        )
