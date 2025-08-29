from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont, QCursor, QIcon, QPixmap, QAction
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QFileDialog, QProgressBar,
                           QMessageBox, QToolButton, QMenu)
import os
from pathlib import Path

class FileUploadWidget(QWidget):
    """Widget for selecting and uploading files/images"""
    file_selected = pyqtSignal(str, str)  # file_path, file_type
    upload_progress = pyqtSignal(int)  # progress percentage
    upload_complete = pyqtSignal(dict)  # file metadata
    upload_error = pyqtSignal(str)  # error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file_path = None
        self.selected_file_type = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the file upload UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Set maximum width for the entire widget to prevent it from taking too much space
        self.setMaximumWidth(80)
        
        # File selection button with dropdown menu
        self.file_btn = QToolButton()
        self.file_btn.setText("📎")
        self.file_btn.setFont(QFont("Segoe UI", 14))
        self.file_btn.setFixedSize(35, 35)
        self.file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.file_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_btn.setStyleSheet("""
            QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 17px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # Create dropdown menu
        self._create_file_menu()
        
        # Image button (quick access)
        self.image_btn = QPushButton("🖼️")
        self.image_btn.setFont(QFont("Segoe UI", 14))
        self.image_btn.setFixedSize(35, 35)
        self.image_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.image_btn.clicked.connect(self._select_image)
        self.image_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 17px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        layout.addWidget(self.file_btn)
        layout.addWidget(self.image_btn)
        # Remove stretch to keep buttons compact
        
    def _create_file_menu(self):
        """Create dropdown menu for file types"""
        menu = QMenu(self)
        
        # Image action
        image_action = QAction("🖼️ Images", self)
        image_action.triggered.connect(self._select_image)
        menu.addAction(image_action)
        
        # Document action
        doc_action = QAction("📄 Documents", self)
        doc_action.triggered.connect(self._select_document)
        menu.addAction(doc_action)
        
        # Audio action
        audio_action = QAction("🎵 Audio", self)
        audio_action.triggered.connect(self._select_audio)
        menu.addAction(audio_action)
        
        # Video action
        video_action = QAction("🎬 Video", self)
        video_action.triggered.connect(self._select_video)
        menu.addAction(video_action)
        
        # Any file action
        any_action = QAction("📎 Any File", self)
        any_action.triggered.connect(self._select_any_file)
        menu.addAction(any_action)
        
        self.file_btn.setMenu(menu)
        
    def _select_image(self):
        """Select image file"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.svg)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setWindowTitle("Select Image")
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = file_dialog.selectedFiles()
            if files:
                self._handle_file_selection(files[0], 'image')
                
    def _select_document(self):
        """Select document file"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Documents (*.pdf *.doc *.docx *.txt *.rtf *.xls *.xlsx *.ppt *.pptx)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setWindowTitle("Select Document")
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = file_dialog.selectedFiles()
            if files:
                self._handle_file_selection(files[0], 'file')
                
    def _select_audio(self):
        """Select audio file"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audio (*.mp3 *.wav *.ogg *.aac *.flac *.m4a)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setWindowTitle("Select Audio")
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = file_dialog.selectedFiles()
            if files:
                self._handle_file_selection(files[0], 'audio')
                
    def _select_video(self):
        """Select video file"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Video (*.mp4 *.avi *.mov *.wmv *.flv *.webm *.mkv)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setWindowTitle("Select Video")
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = file_dialog.selectedFiles()
            if files:
                self._handle_file_selection(files[0], 'video')
                
    def _select_any_file(self):
        """Select any file"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setWindowTitle("Select File")
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = file_dialog.selectedFiles()
            if files:
                self._handle_file_selection(files[0], 'file')
                
    def _handle_file_selection(self, file_path, file_type):
        """Handle file selection and validation"""
        try:
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError("Selected file does not exist")
                
            file_size = os.path.getsize(file_path)
            max_size = 50 * 1024 * 1024  # 50MB
            
            if file_size > max_size:
                QMessageBox.warning(
                    self, 
                    "File Too Large", 
                    f"File size ({file_size / (1024*1024):.1f} MB) exceeds maximum allowed size (50 MB)"
                )
                return
                
            self.selected_file_path = file_path
            self.selected_file_type = file_type
            
            # Emit signal
            self.file_selected.emit(file_path, file_type)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to select file: {str(e)}")
            self.upload_error.emit(str(e))
            
    def get_selected_file(self):
        """Get currently selected file"""
        return self.selected_file_path, self.selected_file_type
        
    def reset(self):
        """Reset file selection"""
        self.selected_file_path = None
        self.selected_file_type = None


class FilePreviewWidget(QWidget):
    """Widget to preview selected file before sending"""
    remove_file = pyqtSignal()
    
    def __init__(self, file_path, file_type, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_type = file_type
        self.file_name = Path(file_path).name
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup preview UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Preview container
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        preview_layout = QHBoxLayout(preview_frame)
        preview_layout.setContentsMargins(8, 8, 8, 8)
        preview_layout.setSpacing(10)
        
        # File icon or thumbnail
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.file_type == 'image' and os.path.exists(self.file_path):
            # Show thumbnail for images
            try:
                pixmap = QPixmap(self.file_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        40, 40, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    icon_label.setPixmap(scaled_pixmap)
                else:
                    icon_label.setText("🖼️")
                    icon_label.setFont(QFont("Segoe UI", 16))
            except:
                icon_label.setText("🖼️")
                icon_label.setFont(QFont("Segoe UI", 16))
        else:
            # Show appropriate icon for other file types
            if self.file_type == 'audio':
                icon_label.setText("🎵")
            elif self.file_type == 'video':
                icon_label.setText("🎬")
            else:
                icon_label.setText("📎")
            icon_label.setFont(QFont("Segoe UI", 16))
            
        preview_layout.addWidget(icon_label)
        
        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # File name
        name_label = QLabel(self.file_name)
        name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #333;")
        info_layout.addWidget(name_label)
        
        # File size
        size_text = self._format_file_size(self.file_size)
        size_label = QLabel(size_text)
        size_label.setFont(QFont("Segoe UI", 9))
        size_label.setStyleSheet("color: #666;")
        info_layout.addWidget(size_label)
        
        preview_layout.addLayout(info_layout)
        preview_layout.addStretch()
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(25, 25)
        remove_btn.setFont(QFont("Segoe UI", 12))
        remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        remove_btn.clicked.connect(self.remove_file.emit)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        preview_layout.addWidget(remove_btn)
        
        layout.addWidget(preview_frame)
        
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
