import os
import uuid
import shutil
from pathlib import Path
from PIL import Image
import hashlib
from datetime import datetime

class MediaHandler:
    """Handle file uploads, processing, and storage for chat media"""
    
    def __init__(self, base_upload_dir="uploads"):
        self.base_dir = Path(base_upload_dir)
        self.images_dir = self.base_dir / "images"
        self.files_dir = self.base_dir / "files"
        self.thumbnails_dir = self.base_dir / "thumbnails"
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        # Supported file types
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
        self.audio_extensions = {'.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a'}
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        
    def _ensure_directories(self):
        """Create upload directories if they don't exist"""
        for directory in [self.images_dir, self.files_dir, self.thumbnails_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _generate_unique_filename(self, original_filename):
        """Generate unique filename while preserving extension"""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{unique_id}{file_ext}"
        
    def _get_file_hash(self, file_path):
        """Calculate SHA-256 hash of file for deduplication"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
        
    def _determine_message_type(self, file_path):
        """Determine message type based on file extension"""
        ext = Path(file_path).suffix.lower()
        if ext in self.image_extensions:
            return 'image'
        elif ext in self.video_extensions:
            return 'video'
        elif ext in self.audio_extensions:
            return 'audio'
        else:
            return 'file'
            
    def _create_thumbnail(self, image_path, thumbnail_size=(200, 200)):
        """Create thumbnail for images"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Generate thumbnail filename
                original_name = Path(image_path).stem
                thumbnail_name = f"thumb_{original_name}.jpg"
                thumbnail_path = self.thumbnails_dir / thumbnail_name
                
                # Save thumbnail
                img.save(thumbnail_path, 'JPEG', quality=85)
                return str(thumbnail_path)
        except Exception as e:
            print(f"[ERROR][MediaHandler] Failed to create thumbnail: {e}")
            return None
            
    def save_uploaded_file(self, source_file_path, original_filename):
        """
        Save uploaded file and return metadata
        
        Args:
            source_file_path: Path to the temporary uploaded file
            original_filename: Original name of the file
            
        Returns:
            dict: File metadata including paths, type, size, etc.
        """
        try:
            # Check file size
            file_size = os.path.getsize(source_file_path)
            if file_size > self.max_file_size:
                raise ValueError(f"File size ({file_size} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)")
            
            # Determine message type and target directory
            message_type = self._determine_message_type(original_filename)
            if message_type == 'image':
                target_dir = self.images_dir
            else:
                target_dir = self.files_dir
                
            # Generate unique filename
            unique_filename = self._generate_unique_filename(original_filename)
            target_path = target_dir / unique_filename
            
            # Copy file to target location
            shutil.copy2(source_file_path, target_path)
            
            # Get file info
            file_info = {
                'message_type': message_type,
                'file_path': str(target_path),
                'file_name': original_filename,
                'unique_filename': unique_filename,
                'file_size': file_size,
                'mime_type': self._get_mime_type(original_filename),
                'file_hash': self._get_file_hash(target_path),
                'thumbnail_path': None
            }
            
            # Create thumbnail for images
            if message_type == 'image':
                thumbnail_path = self._create_thumbnail(target_path)
                if thumbnail_path:
                    file_info['thumbnail_path'] = thumbnail_path
                    
            return file_info
            
        except Exception as e:
            print(f"[ERROR][MediaHandler] Failed to save file: {e}")
            raise
            
    def _get_mime_type(self, filename):
        """Get MIME type based on file extension"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
        
    def delete_file(self, file_path, thumbnail_path=None):
        """Delete file and its thumbnail"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"[INFO][MediaHandler] Deleted file: {file_path}")
                
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                print(f"[INFO][MediaHandler] Deleted thumbnail: {thumbnail_path}")
                
        except Exception as e:
            print(f"[ERROR][MediaHandler] Failed to delete file: {e}")
            
    def get_file_url(self, file_path):
        """Get URL for accessing file (for future web interface)"""
        if file_path:
            return f"/uploads/{Path(file_path).name}"
        return None
        
    def validate_file(self, file_path, allowed_extensions=None):
        """Validate file before processing"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes")
            
        if allowed_extensions:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in allowed_extensions:
                raise ValueError(f"File type not allowed: {file_ext}")
                
        return True
