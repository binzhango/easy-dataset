"""
Basic integration tests for file processors.

These tests verify that all file processors can be instantiated
and registered correctly.
"""

import pytest
from pathlib import Path

from easy_dataset.core.file_processor import (
    FileProcessor,
    FileType,
    ProcessedDocument,
    FileTypeDetector,
    ProcessorRegistry,
    get_registry,
)
from easy_dataset.core.processors import (
    PDFProcessor,
    MarkdownProcessor,
    DOCXProcessor,
    EPUBProcessor,
    TXTProcessor,
)


class TestFileTypeDetector:
    """Test file type detection."""
    
    def test_detect_pdf_from_extension(self):
        """Test PDF detection from file extension."""
        path = Path("test.pdf")
        file_type = FileTypeDetector.detect_from_path(path)
        assert file_type == FileType.PDF
    
    def test_detect_markdown_from_extension(self):
        """Test Markdown detection from file extension."""
        path = Path("test.md")
        file_type = FileTypeDetector.detect_from_path(path)
        assert file_type == FileType.MARKDOWN
    
    def test_detect_docx_from_extension(self):
        """Test DOCX detection from file extension."""
        path = Path("test.docx")
        file_type = FileTypeDetector.detect_from_path(path)
        assert file_type == FileType.DOCX
    
    def test_detect_epub_from_extension(self):
        """Test EPUB detection from file extension."""
        path = Path("test.epub")
        file_type = FileTypeDetector.detect_from_path(path)
        assert file_type == FileType.EPUB
    
    def test_detect_txt_from_extension(self):
        """Test TXT detection from file extension."""
        path = Path("test.txt")
        file_type = FileTypeDetector.detect_from_path(path)
        assert file_type == FileType.TXT
    
    def test_detect_unknown_from_extension(self):
        """Test unknown file type detection."""
        path = Path("test.xyz")
        file_type = FileTypeDetector.detect_from_path(path)
        assert file_type == FileType.UNKNOWN


class TestProcessorInstantiation:
    """Test that all processors can be instantiated."""
    
    def test_pdf_processor_instantiation(self):
        """Test PDFProcessor can be instantiated."""
        processor = PDFProcessor()
        assert isinstance(processor, FileProcessor)
        assert processor.supports(FileType.PDF)
        assert not processor.supports(FileType.MARKDOWN)
    
    def test_markdown_processor_instantiation(self):
        """Test MarkdownProcessor can be instantiated."""
        processor = MarkdownProcessor()
        assert isinstance(processor, FileProcessor)
        assert processor.supports(FileType.MARKDOWN)
        assert not processor.supports(FileType.PDF)
    
    def test_docx_processor_instantiation(self):
        """Test DOCXProcessor can be instantiated."""
        processor = DOCXProcessor()
        assert isinstance(processor, FileProcessor)
        assert processor.supports(FileType.DOCX)
        assert not processor.supports(FileType.PDF)
    
    def test_epub_processor_instantiation(self):
        """Test EPUBProcessor can be instantiated."""
        processor = EPUBProcessor()
        assert isinstance(processor, FileProcessor)
        assert processor.supports(FileType.EPUB)
        assert not processor.supports(FileType.PDF)
    
    def test_txt_processor_instantiation(self):
        """Test TXTProcessor can be instantiated."""
        processor = TXTProcessor()
        assert isinstance(processor, FileProcessor)
        assert processor.supports(FileType.TXT)
        assert not processor.supports(FileType.PDF)


class TestProcessorRegistry:
    """Test processor registry functionality."""
    
    def test_registry_creation(self):
        """Test creating a new registry."""
        registry = ProcessorRegistry()
        assert registry is not None
    
    def test_register_processor(self):
        """Test registering a processor."""
        registry = ProcessorRegistry()
        processor = PDFProcessor()
        
        registry.register(FileType.PDF, processor)
        retrieved = registry.get_processor(FileType.PDF)
        
        assert retrieved is processor
    
    def test_get_nonexistent_processor(self):
        """Test getting a processor that doesn't exist."""
        registry = ProcessorRegistry()
        processor = registry.get_processor(FileType.PDF)
        assert processor is None
    
    def test_global_registry(self):
        """Test global registry instance."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2


class TestProcessedDocument:
    """Test ProcessedDocument container."""
    
    def test_create_document(self):
        """Test creating a ProcessedDocument."""
        doc = ProcessedDocument(
            content="Test content",
            metadata={"key": "value"},
            images=[{"url": "test.jpg"}]
        )
        
        assert doc.content == "Test content"
        assert doc.metadata == {"key": "value"}
        assert doc.images == [{"url": "test.jpg"}]
    
    def test_create_document_with_defaults(self):
        """Test creating a ProcessedDocument with default values."""
        doc = ProcessedDocument(content="Test content")
        
        assert doc.content == "Test content"
        assert doc.metadata == {}
        assert doc.images == []


class TestFileValidation:
    """Test file validation in processors."""
    
    def test_validate_nonexistent_file(self):
        """Test validation fails for nonexistent file."""
        processor = TXTProcessor()
        with pytest.raises(FileNotFoundError):
            processor.validate_file(Path("nonexistent.txt"))
    
    def test_max_file_size_constant(self):
        """Test MAX_FILE_SIZE constant is set."""
        processor = TXTProcessor()
        assert processor.MAX_FILE_SIZE == 100 * 1024 * 1024  # 100MB
