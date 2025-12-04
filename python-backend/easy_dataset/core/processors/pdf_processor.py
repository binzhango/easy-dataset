"""
PDF file processor implementation.

This module provides PDF document processing using PyPDF2 for text extraction
and metadata handling. It supports extracting text from all pages and
extracting images from PDFs.
"""

from pathlib import Path
from typing import Dict, List, Optional
import io
import base64

try:
    from PyPDF2 import PdfReader
    from PyPDF2.errors import PdfReadError
except ImportError:
    raise ImportError(
        "PyPDF2 is required for PDF processing. "
        "Install it with: pip install pypdf2"
    )

from ..file_processor import FileProcessor, FileType, ProcessedDocument


class PDFProcessor(FileProcessor):
    """
    Processor for PDF documents.
    
    Extracts text content from all pages, metadata, and optionally images.
    Uses PyPDF2 for PDF parsing and text extraction.
    """
    
    def __init__(self, extract_images: bool = True):
        """
        Initialize PDF processor.
        
        Args:
            extract_images: Whether to extract images from PDFs
        """
        self.extract_images = extract_images
    
    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports PDF files."""
        return file_type == FileType.PDF
    
    def process(self, file_path: Path) -> ProcessedDocument:
        """
        Process a PDF file and extract its content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ProcessedDocument containing extracted text, metadata, and images
            
        Raises:
            ValueError: If PDF is invalid or corrupted
            IOError: If file cannot be read
        """
        self.validate_file(file_path)
        
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                # Extract text from all pages
                text_content = self._extract_text(reader)
                
                # Extract metadata
                metadata = self._extract_metadata(reader)
                
                # Extract images if enabled
                images = []
                if self.extract_images:
                    images = self._extract_images(reader)
                
                return ProcessedDocument(
                    content=text_content,
                    metadata=metadata,
                    images=images
                )
                
        except PdfReadError as e:
            raise ValueError(f"Invalid or corrupted PDF file: {e}")
        except Exception as e:
            raise IOError(f"Error reading PDF file: {e}")
    
    def _extract_text(self, reader: PdfReader) -> str:
        """
        Extract text from all pages of the PDF.
        
        Args:
            reader: PyPDF2 PdfReader instance
            
        Returns:
            Concatenated text from all pages
        """
        text_parts = []
        
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    # Add page separator for multi-page documents
                    if text_parts:
                        text_parts.append(f"\n\n--- Page {page_num + 1} ---\n\n")
                    text_parts.append(page_text)
            except Exception as e:
                # Log warning but continue with other pages
                print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                continue
        
        return ''.join(text_parts)
    
    def _extract_metadata(self, reader: PdfReader) -> Dict:
        """
        Extract metadata from PDF.
        
        Args:
            reader: PyPDF2 PdfReader instance
            
        Returns:
            Dictionary containing PDF metadata
        """
        metadata = {
            'page_count': len(reader.pages),
        }
        
        # Extract document information if available
        if reader.metadata:
            doc_info = reader.metadata
            
            # Common metadata fields
            metadata_fields = {
                '/Title': 'title',
                '/Author': 'author',
                '/Subject': 'subject',
                '/Creator': 'creator',
                '/Producer': 'producer',
                '/CreationDate': 'creation_date',
                '/ModDate': 'modification_date',
            }
            
            for pdf_key, meta_key in metadata_fields.items():
                if pdf_key in doc_info:
                    value = doc_info[pdf_key]
                    # Convert to string if not already
                    metadata[meta_key] = str(value) if value else None
        
        return metadata
    
    def _extract_images(self, reader: PdfReader) -> List[Dict]:
        """
        Extract images from PDF pages.
        
        Args:
            reader: PyPDF2 PdfReader instance
            
        Returns:
            List of dictionaries containing image data and metadata
        """
        images = []
        
        for page_num, page in enumerate(reader.pages):
            try:
                # Check if page has images
                if '/XObject' in page['/Resources']:
                    xobjects = page['/Resources']['/XObject'].get_object()
                    
                    for obj_name in xobjects:
                        obj = xobjects[obj_name]
                        
                        # Check if it's an image
                        if obj['/Subtype'] == '/Image':
                            try:
                                image_data = self._extract_image_data(obj)
                                if image_data:
                                    image_data['page'] = page_num + 1
                                    image_data['name'] = obj_name
                                    images.append(image_data)
                            except Exception as e:
                                print(f"Warning: Could not extract image {obj_name} from page {page_num + 1}: {e}")
                                continue
                                
            except Exception as e:
                print(f"Warning: Could not process images on page {page_num + 1}: {e}")
                continue
        
        return images
    
    def _extract_image_data(self, image_obj) -> Optional[Dict]:
        """
        Extract data from an image object.
        
        Args:
            image_obj: PDF image object
            
        Returns:
            Dictionary containing image data or None if extraction fails
        """
        try:
            # Get image dimensions
            width = image_obj.get('/Width', 0)
            height = image_obj.get('/Height', 0)
            
            # Get image data
            data = image_obj.get_data()
            
            # Determine image format
            image_filter = image_obj.get('/Filter', '')
            if isinstance(image_filter, list):
                image_filter = image_filter[0] if image_filter else ''
            
            # Map PDF filters to image formats
            format_map = {
                '/DCTDecode': 'jpeg',
                '/JPXDecode': 'jp2',
                '/FlateDecode': 'png',
            }
            image_format = format_map.get(str(image_filter), 'unknown')
            
            # Encode image data as base64 for storage
            image_base64 = base64.b64encode(data).decode('utf-8')
            
            return {
                'width': width,
                'height': height,
                'format': image_format,
                'data': image_base64,
                'size': len(data),
            }
            
        except Exception as e:
            print(f"Warning: Could not extract image data: {e}")
            return None
