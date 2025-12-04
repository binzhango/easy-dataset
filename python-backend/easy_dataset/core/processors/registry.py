"""
Processor registry initialization.

This module registers all available file processors with the global registry.
"""

from ..file_processor import FileType, get_registry
from .pdf_processor import PDFProcessor
from .markdown_processor import MarkdownProcessor
from .docx_processor import DOCXProcessor
from .epub_processor import EPUBProcessor
from .txt_processor import TXTProcessor


def register_all_processors():
    """
    Register all available file processors with the global registry.
    
    This function should be called once during application initialization
    to make all processors available for use.
    """
    registry = get_registry()
    
    # Register each processor
    registry.register(FileType.PDF, PDFProcessor())
    registry.register(FileType.MARKDOWN, MarkdownProcessor())
    registry.register(FileType.DOCX, DOCXProcessor())
    registry.register(FileType.EPUB, EPUBProcessor())
    registry.register(FileType.TXT, TXTProcessor())


# Auto-register processors when this module is imported
register_all_processors()
