"""
TXT file processor implementation.

This module provides plain text file processing with encoding detection.
It handles various encodings (UTF-8, Latin-1, etc.) and preserves line breaks
and formatting.
"""

from pathlib import Path
from typing import Dict, Optional

try:
    import chardet
except ImportError:
    raise ImportError(
        "chardet is required for text encoding detection. "
        "Install it with: pip install chardet"
    )

from ..file_processor import FileProcessor, FileType, ProcessedDocument


class TXTProcessor(FileProcessor):
    """
    Processor for plain text (TXT) files.
    
    Detects text encoding using chardet and handles various encodings
    (UTF-8, Latin-1, Windows-1252, etc.). Preserves line breaks and formatting.
    """
    
    # Common encodings to try if detection fails
    FALLBACK_ENCODINGS = ['utf-8', 'latin-1', 'windows-1252', 'ascii']
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize TXT processor.
        
        Args:
            confidence_threshold: Minimum confidence for encoding detection (0-1)
        """
        self.confidence_threshold = confidence_threshold
    
    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports TXT files."""
        return file_type == FileType.TXT
    
    def process(self, file_path: Path) -> ProcessedDocument:
        """
        Process a TXT file and extract its content.
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            ProcessedDocument containing text and encoding metadata
            
        Raises:
            ValueError: If encoding cannot be determined
            IOError: If file cannot be read
        """
        self.validate_file(file_path)
        
        try:
            # Detect encoding
            encoding = self._detect_encoding(file_path)
            
            # Read file with detected encoding
            with open(file_path, 'r', encoding=encoding) as file:
                text_content = file.read()
            
            # Extract metadata
            metadata = self._extract_metadata(text_content, encoding)
            
            return ProcessedDocument(
                content=text_content,
                metadata=metadata,
                images=[]
            )
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode text file with encoding {encoding}: {e}")
        except Exception as e:
            raise IOError(f"Error reading TXT file: {e}")
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding name
            
        Raises:
            ValueError: If encoding cannot be determined
        """
        # Read file in binary mode for detection
        with open(file_path, 'rb') as file:
            # Read a sample for detection (first 10KB should be enough)
            raw_data = file.read(10240)
        
        # Detect encoding
        result = chardet.detect(raw_data)
        
        if result['encoding'] is None:
            # Try fallback encodings
            return self._try_fallback_encodings(file_path)
        
        encoding = result['encoding']
        confidence = result['confidence']
        
        # Check confidence threshold
        if confidence < self.confidence_threshold:
            # Low confidence, try fallback encodings
            try:
                return self._try_fallback_encodings(file_path)
            except ValueError:
                # If fallback fails, use detected encoding anyway
                pass
        
        return encoding
    
    def _try_fallback_encodings(self, file_path: Path) -> str:
        """
        Try fallback encodings when detection fails or has low confidence.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Working encoding name
            
        Raises:
            ValueError: If no encoding works
        """
        for encoding in self.FALLBACK_ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    # Try to read the file
                    file.read()
                # If successful, return this encoding
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        raise ValueError(
            f"Could not determine encoding for file: {file_path}. "
            f"Tried: {', '.join(self.FALLBACK_ENCODINGS)}"
        )
    
    def _extract_metadata(self, text: str, encoding: str) -> Dict:
        """
        Extract metadata from text content.
        
        Args:
            text: Text content
            encoding: Detected encoding
            
        Returns:
            Dictionary containing text metadata
        """
        lines = text.split('\n')
        
        metadata = {
            'encoding': encoding,
            'line_count': len(lines),
            'character_count': len(text),
            'word_count': len(text.split()),
            'is_empty': not text.strip(),
        }
        
        # Detect if text contains special characters
        metadata['has_non_ascii'] = any(ord(char) > 127 for char in text)
        
        # Detect line ending style
        if '\r\n' in text:
            metadata['line_ending'] = 'CRLF (Windows)'
        elif '\r' in text:
            metadata['line_ending'] = 'CR (Old Mac)'
        else:
            metadata['line_ending'] = 'LF (Unix/Mac)'
        
        return metadata
    
    def detect_encoding_only(self, file_path: Path) -> Dict:
        """
        Detect encoding without reading the full file.
        
        Useful for quick encoding checks.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with encoding and confidence
        """
        with open(file_path, 'rb') as file:
            raw_data = file.read(10240)
        
        result = chardet.detect(raw_data)
        
        return {
            'encoding': result['encoding'],
            'confidence': result['confidence'],
            'language': result.get('language'),
        }
