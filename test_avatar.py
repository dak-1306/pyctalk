#!/usr/bin/env python3
"""
Test script for avatar functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6 import QtWidgets, QtCore, QtGui
import asyncio
import base64

class AvatarTestWindow(QtWidgets.QWidget):
    """Test window for avatar functionality"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avatar Test")
        self.setFixedSize(400, 300)

        self.avatar_data = None
        self.avatar_filename = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the test UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QtWidgets.QLabel("🖼️ Test Chức năng Avatar")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Avatar display
        self.avatar_label = QtWidgets.QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #e0e0e0;
                border-radius: 50px;
                background-color: #f8f9fa;
            }
        """)
        self.avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setText("👤")
        self.avatar_label.setFont(QtGui.QFont("Arial", 30))

        avatar_container = QtWidgets.QWidget()
        avatar_layout = QtWidgets.QVBoxLayout(avatar_container)
        avatar_layout.addWidget(self.avatar_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(avatar_container)

        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()

        select_btn = QtWidgets.QPushButton("📁 Chọn ảnh")
        select_btn.clicked.connect(self._select_avatar)
        buttons_layout.addWidget(select_btn)

        clear_btn = QtWidgets.QPushButton("🗑️ Xóa")
        clear_btn.clicked.connect(self._clear_avatar)
        buttons_layout.addWidget(clear_btn)

        layout.addLayout(buttons_layout)

        # Info label
        self.info_label = QtWidgets.QLabel("Chưa có avatar")
        self.info_label.setStyleSheet("color: #666; font-size: 12px;")
        self.info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # Test encode/decode
        test_btn = QtWidgets.QPushButton("🔄 Test Encode/Decode")
        test_btn.clicked.connect(self._test_encode_decode)
        layout.addWidget(test_btn)

    def _select_avatar(self):
        """Select avatar image"""
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
                        100, 100,
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    )

                    # Create circular mask
                    mask = QtGui.QPixmap(100, 100)
                    mask.fill(QtCore.Qt.GlobalColor.transparent)

                    painter = QtGui.QPainter(mask)
                    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                    painter.drawEllipse(0, 0, 100, 100)
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

                    self.info_label.setText(f"✅ Đã chọn: {self.avatar_filename}")
                    print(f"[TEST] Avatar selected: {file_path}")
                    print(f"[TEST] Data length: {len(self.avatar_data)} characters")
                else:
                    QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể tải ảnh. Vui lòng chọn file ảnh hợp lệ.")

        except Exception as e:
            print(f"[ERROR] Error selecting avatar: {e}")
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể chọn ảnh: {e}")

    def _clear_avatar(self):
        """Clear avatar"""
        self.avatar_label.clear()
        self.avatar_label.setText("👤")
        self.avatar_label.setFont(QtGui.QFont("Arial", 30))
        self.avatar_data = None
        self.avatar_filename = None
        self.info_label.setText("Chưa có avatar")
        print("[TEST] Avatar cleared")

    def _test_encode_decode(self):
        """Test base64 encode/decode"""
        if not self.avatar_data:
            QtWidgets.QMessageBox.information(self, "Info", "Vui lòng chọn ảnh trước")
            return

        try:
            # Test decode
            decoded_data = base64.b64decode(self.avatar_data)

            # Save to temp file to verify
            temp_path = os.path.join(os.path.dirname(__file__), "temp_test_image.jpg")
            with open(temp_path, 'wb') as f:
                f.write(decoded_data)

            QtWidgets.QMessageBox.information(
                self, "Thành công",
                f"✅ Encode/Decode thành công!\n\n"
                f"Original size: {len(self.avatar_data)} chars\n"
                f"Decoded size: {len(decoded_data)} bytes\n"
                f"Temp file: {temp_path}"
            )

            print(f"[TEST] Decode successful, saved to: {temp_path}")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Lỗi encode/decode: {e}")
            print(f"[ERROR] Encode/decode test failed: {e}")

def main():
    """Main function"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set dark theme for better visibility
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 0, 0))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))

    app.setPalette(dark_palette)

    window = AvatarTestWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
