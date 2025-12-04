"""Image upload and storage service."""

import base64
import hashlib
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple

from PIL import Image
from sqlalchemy.orm import Session

from easy_dataset.models.image import Images
from easy_dataset.models.project import Projects

logger = logging.getLogger(__name__)


class ImageService:
    """
    Service for handling image uploads and storage.
    
    Supports:
    - Image uploads (JPEG, PNG, WebP)
    - Image metadata extraction (dimensions, size)
    - Image storage with unique filenames
    - Optional thumbnail generation
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
    
    # Maximum file size (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    def __init__(
        self,
        db_session: Session,
        storage_path: str = "uploads/images"
    ):
        """
        Initialize image service.
        
        Args:
            db_session: Database session
            storage_path: Base path for storing images
        """
        self.db = db_session
        self.storage_path = Path(storage_path)
        
        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def validate_image_format(self, filename: str) -> bool:
        """
        Validate image file format.
        
        Args:
            filename: Image filename
            
        Returns:
            True if format is supported
        """
        ext = Path(filename).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def validate_image_size(self, file_size: int) -> bool:
        """
        Validate image file size.
        
        Args:
            file_size: File size in bytes
            
        Returns:
            True if size is within limits
        """
        return file_size <= self.MAX_FILE_SIZE
    
    def extract_image_dimensions(
        self,
        image_data: BinaryIO
    ) -> Tuple[int, int]:
        """
        Extract image dimensions.
        
        Args:
            image_data: Binary image data
            
        Returns:
            Tuple of (width, height)
        """
        try:
            with Image.open(image_data) as img:
                return img.size
        except Exception as e:
            logger.warning(f"Failed to extract image dimensions: {e}")
            return (0, 0)
    
    def generate_unique_filename(
        self,
        original_filename: str,
        project_id: str
    ) -> str:
        """
        Generate unique filename for storage.
        
        Args:
            original_filename: Original filename
            project_id: Project ID
            
        Returns:
            Unique filename
        """
        # Get file extension
        ext = Path(original_filename).suffix.lower()
        
        # Generate hash from filename and project_id
        hash_input = f"{project_id}_{original_filename}".encode()
        file_hash = hashlib.md5(hash_input).hexdigest()[:12]
        
        # Create unique filename
        return f"{file_hash}{ext}"
    
    def save_image_file(
        self,
        image_data: BinaryIO,
        filename: str,
        project_id: str
    ) -> str:
        """
        Save image file to storage.
        
        Args:
            image_data: Binary image data
            filename: Unique filename
            project_id: Project ID
            
        Returns:
            Relative path to saved file
        """
        # Create project subdirectory
        project_dir = self.storage_path / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = project_dir / filename
        
        # Save file
        with open(file_path, "wb") as f:
            image_data.seek(0)
            f.write(image_data.read())
        
        # Return relative path
        return str(Path(project_id) / filename)
    
    def generate_thumbnail(
        self,
        image_path: Path,
        thumbnail_size: Tuple[int, int] = (200, 200)
    ) -> Optional[str]:
        """
        Generate thumbnail for image (optional feature).
        
        Args:
            image_path: Path to original image
            thumbnail_size: Thumbnail dimensions
            
        Returns:
            Path to thumbnail or None if generation failed
        """
        try:
            with Image.open(image_path) as img:
                # Create thumbnail
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Generate thumbnail filename
                thumb_filename = f"thumb_{image_path.name}"
                thumb_path = image_path.parent / thumb_filename
                
                # Save thumbnail
                img.save(thumb_path)
                
                return str(thumb_path)
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {e}")
            return None
    
    async def upload_image(
        self,
        project_id: str,
        image_name: str,
        image_data: BinaryIO,
        generate_thumb: bool = False
    ) -> Images:
        """
        Upload and store an image.
        
        Args:
            project_id: Project ID
            image_name: Original image filename
            image_data: Binary image data
            generate_thumb: Whether to generate thumbnail
            
        Returns:
            Created Images model instance
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If project not found
        """
        # Validate project exists
        project = self.db.query(Projects).filter(
            Projects.id == project_id
        ).first()
        
        if not project:
            raise RuntimeError(f"Project not found: {project_id}")
        
        # Validate image format
        if not self.validate_image_format(image_name):
            raise ValueError(
                f"Unsupported image format. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Get file size
        image_data.seek(0, 2)  # Seek to end
        file_size = image_data.tell()
        image_data.seek(0)  # Reset to beginning
        
        # Validate file size
        if not self.validate_image_size(file_size):
            raise ValueError(
                f"Image size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        
        # Extract dimensions
        width, height = self.extract_image_dimensions(image_data)
        image_data.seek(0)  # Reset after reading
        
        # Generate unique filename
        unique_filename = self.generate_unique_filename(image_name, project_id)
        
        # Save image file
        relative_path = self.save_image_file(image_data, unique_filename, project_id)
        
        # Generate thumbnail if requested
        if generate_thumb:
            full_path = self.storage_path / relative_path
            self.generate_thumbnail(full_path)
        
        # Create database record
        image = Images(
            project_id=project_id,
            image_name=image_name,
            path=relative_path,
            size=file_size,
            width=width if width > 0 else None,
            height=height if height > 0 else None
        )
        
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        
        logger.info(
            f"Image uploaded: {image_name} ({width}x{height}, {file_size} bytes) "
            f"for project {project_id}"
        )
        
        return image
    
    def get_image(self, image_id: str) -> Optional[Images]:
        """
        Get image by ID.
        
        Args:
            image_id: Image ID
            
        Returns:
            Images model instance or None
        """
        return self.db.query(Images).filter(Images.id == image_id).first()
    
    def list_images(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Images]:
        """
        List images for a project.
        
        Args:
            project_id: Project ID
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of Images instances
        """
        return self.db.query(Images).filter(
            Images.project_id == project_id
        ).order_by(
            Images.create_at.desc()
        ).limit(limit).offset(offset).all()
    
    def delete_image(self, image_id: str) -> bool:
        """
        Delete an image.
        
        Args:
            image_id: Image ID
            
        Returns:
            True if deleted, False if not found
        """
        image = self.get_image(image_id)
        
        if not image:
            return False
        
        # Delete file from storage
        try:
            file_path = self.storage_path / image.path
            if file_path.exists():
                file_path.unlink()
                
                # Delete thumbnail if exists
                thumb_path = file_path.parent / f"thumb_{file_path.name}"
                if thumb_path.exists():
                    thumb_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete image file: {e}")
        
        # Delete database record
        self.db.delete(image)
        self.db.commit()
        
        logger.info(f"Image deleted: {image_id}")
        
        return True
    
    def get_image_data(self, image_id: str) -> Optional[bytes]:
        """
        Get image binary data.
        
        Args:
            image_id: Image ID
            
        Returns:
            Image binary data or None
        """
        image = self.get_image(image_id)
        
        if not image:
            return None
        
        file_path = self.storage_path / image.path
        
        if not file_path.exists():
            logger.warning(f"Image file not found: {file_path}")
            return None
        
        with open(file_path, "rb") as f:
            return f.read()
    
    def get_image_base64(self, image_id: str) -> Optional[str]:
        """
        Get image as base64 encoded string.
        
        Args:
            image_id: Image ID
            
        Returns:
            Base64 encoded image data or None
        """
        image_data = self.get_image_data(image_id)
        
        if not image_data:
            return None
        
        return base64.b64encode(image_data).decode("utf-8")
    
    def get_image_data_url(self, image_id: str) -> Optional[str]:
        """
        Get image as data URL.
        
        Args:
            image_id: Image ID
            
        Returns:
            Data URL string or None
        """
        image = self.get_image(image_id)
        
        if not image:
            return None
        
        image_data = self.get_image_data(image_id)
        
        if not image_data:
            return None
        
        # Determine MIME type from extension
        ext = Path(image.path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }
        mime_type = mime_types.get(ext, "image/jpeg")
        
        # Create data URL
        base64_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{base64_data}"
    
    def get_project_image_stats(self, project_id: str) -> Dict[str, int]:
        """
        Get image statistics for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with statistics
        """
        images = self.list_images(project_id, limit=10000)
        
        total_size = sum(img.size for img in images)
        
        return {
            "total_images": len(images),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
