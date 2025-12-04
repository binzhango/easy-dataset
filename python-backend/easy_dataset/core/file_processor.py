"""
Base file processor interface and utilities for document processing.

This module provides the abstract base class for all file processors,
along with utilities for file type detection, validation, and storage.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, BinaryIO
import hashlib
import mimetypes
from enum import Enum


class FileType(Enum):
    """Supported file types for processing."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    DOCX = "docx"
    EPUB = "epub"
    TXT = "txt"
    UNKNOWN = "unknown"


class ProcessedDocument:
    """Container for processed document data."""
    
    def __init__(
        self,
        content: str,
        metadata: Optional[Dict] = None,
        images: Optional[List[Dict]] = None
    ):
        """
        Initialize processed document.
        
        Args:
            content: Extracted text content
            metadata: Document metadata (title, author, etc.)
            images: List of extracted images with metadata
        """
        self.content = content
        self.metadata = metadata or {}
        self.images = images or []


class FileProcessor(ABC):
    """
    Abstract base class for file processors.
    
    Each file format (PDF, DOCX, etc.) should implement this interface
    to provide consistent document processing capabilities.
    """
    
    # Maximum file size in bytes (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    @abstractmethod
    def process(self, file_path: Path) -> ProcessedDocument:
        """
        Process a file and extract its content.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            ProcessedDocument containing extracted content and metadata
            
        Raises:
            ValueError: If file is invalid or unsupported
            IOError: If file cannot be read
        """
        pass
    
    @abstractmethod
    def supports(self, file_type: FileType) -> bool:
        """
        Check if this processor supports the given file type.
        
        Args:
            file_type: The file type to check
            
        Returns:
            True if this processor can handle the file type
        """
        pass
    
    def validate_file(self, file_path: Path) -> None:
        """
        Validate file before processing.
        
        Args:
            file_path: Path to the file to validate
            
        Raises:
            ValueError: If file is invalid
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        file_size = file_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({file_size} bytes) exceeds maximum "
                f"allowed size ({self.MAX_FILE_SIZE} bytes)"
            )
        
        if file_size == 0:
            raise ValueError("File is empty")


class FileTypeDetector:
    """Utility class for detecting file types."""
    
    # File extension to FileType mapping
    EXTENSION_MAP = {
        '.pdf': FileType.PDF,
        '.md': FileType.MARKDOWN,
        '.markdown': FileType.MARKDOWN,
        '.docx': FileType.DOCX,
        '.epub': FileType.EPUB,
        '.txt': FileType.TXT,
    }
    
    # MIME type to FileType mapping
    MIME_MAP = {
        'application/pdf': FileType.PDF,
        'text/markdown': FileType.MARKDOWN,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': FileType.DOCX,
        'application/epub+zip': FileType.EPUB,
        'text/plain': FileType.TXT,
    }
    
    @classmethod
    def detect_from_path(cls, file_path: Path) -> FileType:
        """
        Detect file type from file path extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected FileType
        """
        extension = file_path.suffix.lower()
        return cls.EXTENSION_MAP.get(extension, FileType.UNKNOWN)
    
    @classmethod
    def detect_from_mime(cls, mime_type: str) -> FileType:
        """
        Detect file type from MIME type.
        
        Args:
            mime_type: MIME type string
            
        Returns:
            Detected FileType
        """
        return cls.MIME_MAP.get(mime_type, FileType.UNKNOWN)
    
    @classmethod
    def detect(cls, file_path: Path) -> FileType:
        """
        Detect file type using multiple methods.
        
        First tries extension, then MIME type detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected FileType
        """
        # Try extension first
        file_type = cls.detect_from_path(file_path)
        if file_type != FileType.UNKNOWN:
            return file_type
        
        # Try MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            file_type = cls.detect_from_mime(mime_type)
            if file_type != FileType.UNKNOWN:
                return file_type
        
        return FileType.UNKNOWN


class FileStorageUtil:
    """Utility class for file storage operations."""
    
    @staticmethod
    def calculate_md5(file_path: Path) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash as hexadecimal string
        """
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    @staticmethod
    def get_file_metadata(file_path: Path) -> Dict:
        """
        Extract file metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        stat = file_path.stat()
        return {
            'file_name': file_path.name,
            'file_size': stat.st_size,
            'file_type': FileTypeDetector.detect(file_path).value,
            'md5': FileStorageUtil.calculate_md5(file_path),
            'extension': file_path.suffix.lower(),
        }


class ProcessorRegistry:
    """Registry for file processors."""
    
    def __init__(self):
        """Initialize the processor registry."""
        self._processors: Dict[FileType, FileProcessor] = {}
    
    def register(self, file_type: FileType, processor: FileProcessor) -> None:
        """
        Register a processor for a file type.
        
        Args:
            file_type: The file type this processor handles
            processor: The processor instance
        """
        self._processors[file_type] = processor
    
    def get_processor(self, file_type: FileType) -> Optional[FileProcessor]:
        """
        Get processor for a file type.
        
        Args:
            file_type: The file type to get processor for
            
        Returns:
            Processor instance or None if not found
        """
        return self._processors.get(file_type)
    
    def process_file(self, file_path: Path) -> ProcessedDocument:
        """
        Process a file using the appropriate processor.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            ProcessedDocument containing extracted content
            
        Raises:
            ValueError: If file type is not supported
        """
        file_type = FileTypeDetector.detect(file_path)
        
        if file_type == FileType.UNKNOWN:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        processor = self.get_processor(file_type)
        if processor is None:
            raise ValueError(f"No processor registered for {file_type.value}")
        
        processor.validate_file(file_path)
        return processor.process(file_path)


# Global processor registry instance
_registry = ProcessorRegistry()


def get_registry() -> ProcessorRegistry:
    """
    Get the global processor registry.
    
    Returns:
        The global ProcessorRegistry instance
    """
    return _registry
