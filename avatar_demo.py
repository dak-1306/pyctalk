#!/usr/bin/env python3
"""
Demo script for avatar functionality in PyQtalk
"""
import sys
import os
import asyncio
import base64
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6 import QtWidgets, QtCore, QtGui

class AvatarDemoApp(QtWidgets.QWidget):
    """Demo application for avatar functionality"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtalk - Avatar Demo")
        self.setFixedSize(800, 600)

        self.current_avatar_data = None
        self.current_avatar_filename = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the demo UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title = QtWidgets.QLabel("🎭 PyQtalk Avatar System Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #6366f1;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Description
        desc = QtWidgets.QLabel(
            "Demo chức năng avatar trong PyQtalk Messenger\n"
            "Upload, hiển thị và quản lý ảnh đại diện người dùng"
        )
        desc.setStyleSheet("color: #666; font-size: 12px;")
        desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        main_layout.addWidget(desc)

        # Main content area
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(20)

        # Left panel - Avatar upload
        self._create_left_panel(content_layout)

        # Right panel - Avatar preview
        self._create_right_panel(content_layout)

        main_layout.addLayout(content_layout)

        # Status bar
        self.status_label = QtWidgets.QLabel("Sẵn sàng")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        main_layout.addWidget(self.status_label)

    def _create_left_panel(self, parent_layout):
        """Create left panel for avatar upload"""
        left_widget = QtWidgets.QWidget()
        left_widget.setFixedWidth(300)
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        # Panel title
        panel_title = QtWidgets.QLabel("📤 Upload Avatar")
        panel_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")
        left_layout.addWidget(panel_title)

        # Current avatar display
        avatar_group = QtWidgets.QGroupBox("Ảnh hiện tại")
        avatar_layout = QtWidgets.QVBoxLayout(avatar_group)

        self.current_avatar = QtWidgets.QLabel()
        self.current_avatar.setFixedSize(120, 120)
        self.current_avatar.setStyleSheet("""
            QLabel {
                border: 3px solid #e0e0e0;
                border-radius: 60px;
                background-color: #f8f9fa;
            }
        """)
        self.current_avatar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.current_avatar.setText("👤")
        self.current_avatar.setFont(QtGui.QFont("Arial", 40))

        avatar_layout.addWidget(self.current_avatar, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(avatar_group)

        # Control buttons
        buttons_group = QtWidgets.QGroupBox("Điều khiển")
        buttons_layout = QtWidgets.QVBoxLayout(buttons_group)
        buttons_layout.setSpacing(8)

        select_btn = QtWidgets.QPushButton("📁 Chọn ảnh")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        select_btn.clicked.connect(self._select_avatar)
        buttons_layout.addWidget(select_btn)

        clear_btn = QtWidgets.QPushButton("🗑️ Xóa avatar")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        clear_btn.clicked.connect(self._clear_avatar)
        buttons_layout.addWidget(clear_btn)

        upload_btn = QtWidgets.QPushButton("📤 Upload lên server")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        upload_btn.clicked.connect(self._simulate_upload)
        buttons_layout.addWidget(upload_btn)

        left_layout.addWidget(buttons_group)

        # File info
        info_group = QtWidgets.QGroupBox("Thông tin file")
        info_layout = QtWidgets.QVBoxLayout(info_group)

        self.file_info = QtWidgets.QLabel("Chưa có file nào")
        self.file_info.setStyleSheet("color: #666; font-size: 11px;")
        self.file_info.setWordWrap(True)
        info_layout.addWidget(self.file_info)

        left_layout.addWidget(info_group)
        left_layout.addStretch()

        parent_layout.addWidget(left_widget)

    def _create_right_panel(self, parent_layout):
        """Create right panel for avatar preview"""
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        # Panel title
        panel_title = QtWidgets.QLabel("👀 Preview")
        panel_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")
        right_layout.addWidget(panel_title)

        # Preview sections
        self._create_preview_section(right_layout, "Topbar Avatar", self._create_topbar_preview)
        self._create_preview_section(right_layout, "Chat List Item", self._create_chat_list_preview)
        self._create_preview_section(right_layout, "Message Bubble", self._create_message_bubble_preview)

        right_layout.addStretch()
        parent_layout.addWidget(right_widget)

    def _create_preview_section(self, parent_layout, title, create_func):
        """Create a preview section"""
        group = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout(group)
        group_layout.setContentsMargins(10, 10, 10, 10)

        create_func(group_layout)

        parent_layout.addWidget(group)

    def _create_topbar_preview(self, layout):
        """Create topbar avatar preview"""
        preview = QtWidgets.QLabel()
        preview.setFixedSize(32, 32)
        preview.setStyleSheet("""
            QLabel {
                border-radius: 16px;
                border: 2px solid white;
                background-color: #6366f1;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        preview.setText("U")
        preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.topbar_preview = preview
        layout.addWidget(preview, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

    def _create_chat_list_preview(self, layout):
        """Create chat list item avatar preview"""
        preview = QtWidgets.QLabel()
        preview.setFixedSize(50, 50)
        preview.setStyleSheet("""
            QLabel {
                background-color: #6366f1;
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid #e4e6ea;
            }
        """)
        preview.setText("U")
        preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.chat_list_preview = preview
        layout.addWidget(preview, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

    def _create_message_bubble_preview(self, layout):
        """Create message bubble avatar preview"""
        preview = QtWidgets.QLabel()
        preview.setFixedSize(32, 32)
        preview.setStyleSheet("""
            QLabel {
                background-color: #0084FF;
                border-radius: 16px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        preview.setText("U")
        preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.message_bubble_preview = preview
        layout.addWidget(preview, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

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

                    self.current_avatar.setPixmap(scaled_pixmap)
                    self.current_avatar.setText("")  # Clear text

                    # Store file data
                    self.current_avatar_filename = os.path.basename(file_path)

                    # Read file as base64
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        self.current_avatar_data = base64.b64encode(file_data).decode('utf-8')

                    # Update file info
                    self.file_info.setText(
                        f"📁 File: {self.current_avatar_filename}\n"
                        f"📊 Size: {len(self.current_avatar_data)} chars\n"
                        f"🖼️ Dimensions: {pixmap.width()}x{pixmap.height()}"
                    )

                    # Update previews
                    self._update_previews()

                    self.status_label.setText(f"✅ Đã chọn avatar: {self.current_avatar_filename}")
                    print(f"[DEMO] Avatar selected: {file_path}")

                else:
                    QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể tải ảnh. Vui lòng chọn file ảnh hợp lệ.")

        except Exception as e:
            print(f"[ERROR] Error selecting avatar: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể chọn ảnh: {e}")

    def _clear_avatar(self):
        """Clear avatar"""
        self.current_avatar.clear()
        self.current_avatar.setText("👤")
        self.current_avatar.setFont(QtGui.QFont("Arial", 40))
        self.current_avatar_data = None
        self.current_avatar_filename = None
        self.file_info.setText("Chưa có file nào")

        # Reset previews
        self._reset_previews()

        self.status_label.setText("🗑️ Đã xóa avatar")
        print("[DEMO] Avatar cleared")

    def _simulate_upload(self):
        """Simulate avatar upload process"""
        if not self.current_avatar_data or not self.current_avatar_filename:
            QtWidgets.QMessageBox.information(self, "Info", "Vui lòng chọn ảnh trước")
            return

        try:
            # Simulate the upload process
            print(f"[DEMO] Simulating upload...")
            print(f"[DEMO] Filename: {self.current_avatar_filename}")
            print(f"[DEMO] Data size: {len(self.current_avatar_data)} characters")

            # Here you would normally send to server
            # For now, just show success message
            QtWidgets.QMessageBox.information(
                self, "Thành công",
                f"✅ Upload thành công!\n\n"
                f"File: {self.current_avatar_filename}\n"
                f"Size: {len(self.current_avatar_data)} chars\n"
                f"Đây là simulation - trong thực tế sẽ gửi lên server."
            )

            self.status_label.setText("📤 Upload hoàn thành")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Lỗi simulation: {e}")
            print(f"[ERROR] Simulation failed: {e}")

    def _update_previews(self):
        """Update all preview avatars"""
        if self.current_avatar_data:
            # Update topbar preview
            self.topbar_preview.setStyleSheet("""
                QLabel {
                    border-radius: 16px;
                    border: 2px solid #4CAF50;
                    background-color: #6366f1;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            self.topbar_preview.setText("📷")

            # Update chat list preview
            self.chat_list_preview.setStyleSheet("""
                QLabel {
                    background-color: #6366f1;
                    color: white;
                    border-radius: 25px;
                    font-size: 16px;
                    font-weight: bold;
                    border: 2px solid #4CAF50;
                }
            """)
            self.chat_list_preview.setText("📷")

            # Update message bubble preview
            self.message_bubble_preview.setStyleSheet("""
                QLabel {
                    background-color: #0084FF;
                    border-radius: 16px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    border: 2px solid #4CAF50;
                }
            """)
            self.message_bubble_preview.setText("📷")

    def _reset_previews(self):
        """Reset all preview avatars"""
        # Reset topbar preview
        self.topbar_preview.setStyleSheet("""
            QLabel {
                border-radius: 16px;
                border: 2px solid white;
                background-color: #6366f1;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.topbar_preview.setText("U")

        # Reset chat list preview
        self.chat_list_preview.setStyleSheet("""
            QLabel {
                background-color: #6366f1;
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid #e4e6ea;
            }
        """)
        self.chat_list_preview.setText("U")

        # Reset message bubble preview
        self.message_bubble_preview.setStyleSheet("""
            QLabel {
                background-color: #0084FF;
                border-radius: 16px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.message_bubble_preview.setText("U")

def main():
    """Main function"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application properties
    app.setApplicationName("PyQtalk Avatar Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("PyQtalk")

    # Create demo window
    window = AvatarDemoApp()
    window.show()

    print("[DEMO] Avatar demo application started")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
