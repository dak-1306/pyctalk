import datetime
import os
from pathlib import Path
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor, QPixmap, QPainter, QIcon
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QSizePolicy)

class MediaMessageBubble(QWidget):
    """Extended message bubble for media content (images, files)"""
    sender_clicked = pyqtSignal(str)
    timestamp_clicked = pyqtSignal(str)
    file_clicked = pyqtSignal(str)  # Signal when file is clicked to open/download
    
    def __init__(self, message_data, is_sent=True, timestamp=None, sender_name=None, 
                 show_sender_name=False, show_timestamp=False, is_read=None, parent=None):
        super().__init__(parent)
        
        # Message data can contain text, media info, etc.
        self.message_data = message_data
        self.is_sent = is_sent
        self.timestamp = timestamp or datetime.datetime.now()
        self.sender_name = sender_name
        self.show_sender_name = show_sender_name
        self.show_timestamp = show_timestamp
        self.is_read = is_read
        
        # Extract message info
        self.message_type = message_data.get('message_type', 'text')
        self.content = message_data.get('content', '')
        self.file_path = message_data.get('file_path')
        self.file_name = message_data.get('file_name')
        self.file_size = message_data.get('file_size', 0)
        self.thumbnail_path = message_data.get('thumbnail_path')
        self.mime_type = message_data.get('mime_type', '')
        
        self._setup_ui()
        self._apply_styles()
        
    def _setup_ui(self):
        """Setup the UI based on message type"""
        # Use simple VBoxLayout since alignment will be handled by parent container
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Container for the message bubble
        self.bubble_container = QFrame()
        self.bubble_container.setObjectName("messageBubble")
        self.bubble_container.setMaximumWidth(350)  # Limit width to prevent stretching
        
        bubble_layout = QVBoxLayout(self.bubble_container)
        bubble_layout.setContentsMargins(12, 8, 12, 8)
        bubble_layout.setSpacing(5)
        
        # Add sender name if needed
        if self.show_sender_name and self.sender_name:
            sender_label = QLabel(self.sender_name)
            sender_label.setObjectName("senderName")
            sender_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            sender_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            sender_label.mousePressEvent = lambda e: self.sender_clicked.emit(self.sender_name)
            bubble_layout.addWidget(sender_label)
        
        # Add content based on message type
        if self.message_type == 'text':
            self._add_text_content(bubble_layout)
        elif self.message_type == 'image':
            self._add_image_content(bubble_layout)
        elif self.message_type in ['file', 'audio', 'video']:
            self._add_file_content(bubble_layout)
            
        # Add text content if present (for media with captions)
        if self.content.strip() and self.message_type != 'text':
            text_label = QLabel(self.content)
            text_label.setWordWrap(True)
            text_label.setFont(QFont("Segoe UI", 10))
            text_label.setObjectName("messageText")
            bubble_layout.addWidget(text_label)
        
        # Add timestamp if needed
        if self.show_timestamp:
            self._add_timestamp(bubble_layout)
            
        # Add read status for sent messages
        if self.is_sent and self.is_read is not None:
            self._add_read_status(bubble_layout)
        
        # Simply add the bubble to layout - alignment handled by parent
        layout.addWidget(self.bubble_container)
            
    def _add_text_content(self, layout):
        """Add text content to bubble"""
        text_label = QLabel(self.content)
        text_label.setWordWrap(True)
        text_label.setFont(QFont("Segoe UI", 10))
        text_label.setObjectName("messageText")
        layout.addWidget(text_label)
        
    def _add_image_content(self, layout):
        """Add image content to bubble"""
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use thumbnail if available, otherwise original image
        image_path = self.thumbnail_path or self.file_path
        
        if image_path and os.path.exists(image_path):
            # Create image label
            image_label = QLabel()
            image_label.setObjectName("imageContent")
            image_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Load and scale image
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale image to fit bubble (max 280x180 for better proportion)
                max_width = 280
                max_height = 180
                scaled_pixmap = pixmap.scaled(
                    max_width, max_height, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
                
                # Set minimum size to prevent tiny images
                image_label.setMinimumSize(120, 80)
                
                # Add subtle styling for better appearance
                image_label.setStyleSheet("""
                    QLabel {
                        border-radius: 8px;
                        background-color: transparent;
                    }
                """)
                
                # Click to view full image
                image_label.mousePressEvent = lambda e: self.file_clicked.emit(self.file_path)
            else:
                image_label.setText("🖼️ Image not available")
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image_label.setStyleSheet("""
                    QLabel {
                        color: #999;
                        font-size: 14px;
                        padding: 20px;
                        background-color: rgba(248, 249, 250, 0.8);
                        border-radius: 8px;
                        border: 1px solid #e9ecef;
                    }
                """)
                
            image_layout.addWidget(image_label)
        else:
            # Fallback if image not found
            placeholder = QLabel("🖼️ Image not found")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("""
                QLabel {
                    color: #999;
                    font-size: 14px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }
            """)
            image_layout.addWidget(placeholder)
            
        layout.addWidget(image_container)
        
    def _add_file_content(self, layout):
        """Add file content to bubble"""
        file_container = QFrame()
        file_container.setObjectName("fileContainer")
        file_layout = QHBoxLayout(file_container)
        file_layout.setContentsMargins(8, 8, 8, 8)
        file_layout.setSpacing(10)
        
        # File icon based on type
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.message_type == 'audio':
            icon_label.setText("🎵")
        elif self.message_type == 'video':
            icon_label.setText("🎬")
        else:
            # Determine icon by file extension
            if self.file_name:
                ext = Path(self.file_name).suffix.lower()
                if ext in ['.pdf']:
                    icon_label.setText("📄")
                elif ext in ['.doc', '.docx']:
                    icon_label.setText("📝")
                elif ext in ['.xls', '.xlsx']:
                    icon_label.setText("📊")
                elif ext in ['.zip', '.rar', '.7z']:
                    icon_label.setText("📦")
                else:
                    icon_label.setText("📎")
            else:
                icon_label.setText("📎")
                
        icon_label.setFont(QFont("Segoe UI", 16))
        file_layout.addWidget(icon_label)
        
        # File info
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # File name
        name_label = QLabel(self.file_name or "Unknown file")
        name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        name_label.setObjectName("fileName")
        info_layout.addWidget(name_label)
        
        # File size
        if self.file_size > 0:
            size_text = self._format_file_size(self.file_size)
            size_label = QLabel(size_text)
            size_label.setFont(QFont("Segoe UI", 9))
            size_label.setObjectName("fileSize")
            info_layout.addWidget(size_label)
            
        file_layout.addWidget(info_container)
        
        # Download/Open button
        action_btn = QPushButton()
        action_btn.setFixedSize(30, 30)
        action_btn.setText("📥")
        action_btn.setFont(QFont("Segoe UI", 12))
        action_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        action_btn.clicked.connect(lambda: self.file_clicked.emit(self.file_path))
        file_layout.addWidget(action_btn)
        
        # Make entire container clickable
        file_container.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        file_container.mousePressEvent = lambda e: self.file_clicked.emit(self.file_path)
        
        layout.addWidget(file_container)
        
    def _add_timestamp(self, layout):
        """Add timestamp to bubble"""
        from .time_formatter import TimeFormatter
        
        timestamp_label = QLabel(TimeFormatter.format_message_time(self.timestamp))
        timestamp_label.setFont(QFont("Segoe UI", 8))
        timestamp_label.setObjectName("timestamp")
        timestamp_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        timestamp_label.mousePressEvent = lambda e: self.timestamp_clicked.emit(str(self.timestamp))
        
        # Align timestamp
        if self.is_sent:
            timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            timestamp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
        layout.addWidget(timestamp_label)
        
    def _add_read_status(self, layout):
        """Add read status indicator for sent messages"""
        if self.is_read == 1:
            status_text = "✓✓"
            status_color = "#4fc3f7"  # Blue for read
        elif self.is_read == 0:
            status_text = "✓"
            status_color = "#666"  # Gray for sent but not read
        else:
            return  # Don't show status if unknown
            
        status_label = QLabel(status_text)
        status_label.setFont(QFont("Segoe UI", 8))
        status_label.setStyleSheet(f"color: {status_color};")
        status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(status_label)
        
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
            
    def _apply_styles(self):
        """Apply styles to the bubble"""
        if self.is_sent:
            # Sent message styles (right side, subtle background)
            self.setStyleSheet("""
                QFrame#messageBubble {
                    background-color: rgba(102, 126, 234, 0.1);
                    border-radius: 18px;
                    border-bottom-right-radius: 4px;
                    border: 1px solid rgba(102, 126, 234, 0.2);
                }
                QLabel#messageText, QLabel#fileName {
                    color: #333;
                }
                QLabel#senderName {
                    color: #667eea;
                    font-weight: bold;
                }
                QLabel#timestamp, QLabel#fileSize {
                    color: #888;
                }
                QFrame#fileContainer {
                    border-radius: 12px;
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    background-color: rgba(102, 126, 234, 0.05);
                }
                QLabel#imageContent {
                    border-radius: 12px;
                    border: 2px solid rgba(102, 126, 234, 0.2);
                }
                QPushButton {
                    background-color: #667eea;
                    border: none;
                    border-radius: 15px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #5a67d8;
                }
            """)
        else:
            # Received message styles (left side, light background)
            self.setStyleSheet("""
                QFrame#messageBubble {
                    background-color: #f8f9fa;
                    border-radius: 18px;
                    border-bottom-left-radius: 4px;
                    border: 1px solid #e9ecef;
                }
                QLabel#messageText, QLabel#fileName {
                    color: #333;
                }
                QLabel#senderName {
                    color: #667eea;
                    font-weight: bold;
                }
                QLabel#timestamp, QLabel#fileSize {
                    color: #888;
                }
                QFrame#fileContainer {
                    border-radius: 12px;
                    border: 1px solid #dee2e6;
                    background-color: #ffffff;
                }
                QLabel#imageContent {
                    border-radius: 12px;
                    border: 2px solid #e9ecef;
                }
                QPushButton {
                    background-color: #667eea;
                    border: none;
                    border-radius: 15px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #5a67d8;
                }
            """)
            
        # Set size constraints
        self.setMinimumHeight(50)
        self.setMaximumWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
