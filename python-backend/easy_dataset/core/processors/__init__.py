"""
File processors for different document formats.

This package contains implementations of FileProcessor for various
document formats including PDF, Markdown, DOCX, EPUB, and TXT.
"""

from .pdf_processor import PDFProcessor
from .markdown_processor import MarkdownProcessor
from .docx_processor import DOCXProcessor
from .epub_processor import EPUBProcessor
from .txt_processor import TXTProcessor
from .registry import register_all_processors

__all__ = [
    'PDFProcessor',
    'MarkdownProcessor',
    'DOCXProcessor',
    'EPUBProcessor',
    'TXTProcessor',
    'register_all_processors',
]
