"""
Markdown file processor implementation.

This module provides Markdown document processing with structure preservation,
header extraction, and hierarchy parsing. It handles code blocks and formatting
while maintaining the document structure.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import re

try:
    import markdown
    from markdown.extensions import toc, fenced_code, tables
except ImportError:
    raise ImportError(
        "markdown is required for Markdown processing. "
        "Install it with: pip install markdown"
    )

from ..file_processor import FileProcessor, FileType, ProcessedDocument


class MarkdownProcessor(FileProcessor):
    """
    Processor for Markdown documents.
    
    Parses markdown with structure preservation, extracts headers and hierarchy,
    and handles code blocks and formatting. Maintains the document structure
    for intelligent chunking.
    """
    
    def __init__(self):
        """Initialize Markdown processor."""
        # Initialize markdown parser with extensions
        self.md_parser = markdown.Markdown(
            extensions=[
                'toc',
                'fenced_code',
                'tables',
                'nl2br',
                'sane_lists',
            ]
        )
    
    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports Markdown files."""
        return file_type == FileType.MARKDOWN
    
    def process(self, file_path: Path) -> ProcessedDocument:
        """
        Process a Markdown file and extract its content.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            ProcessedDocument containing text, structure, and metadata
            
        Raises:
            ValueError: If Markdown is invalid
            IOError: If file cannot be read
        """
        self.validate_file(file_path)
        
        try:
            # Read the markdown file
            with open(file_path, 'r', encoding='utf-8') as file:
                markdown_text = file.read()
            
            # Extract structure and headers
            headers = self._extract_headers(markdown_text)
            
            # Parse markdown to HTML (for validation and processing)
            html_content = self.md_parser.convert(markdown_text)
            
            # Extract metadata
            metadata = {
                'header_count': len(headers),
                'headers': headers,
                'has_code_blocks': self._has_code_blocks(markdown_text),
                'has_tables': self._has_tables(markdown_text),
                'line_count': len(markdown_text.split('\n')),
            }
            
            # Reset parser for next use
            self.md_parser.reset()
            
            return ProcessedDocument(
                content=markdown_text,
                metadata=metadata,
                images=[]
            )
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid encoding in Markdown file: {e}")
        except Exception as e:
            raise IOError(f"Error reading Markdown file: {e}")
    
    def _extract_headers(self, markdown_text: str) -> List[Dict]:
        """
        Extract headers and their hierarchy from markdown.
        
        Args:
            markdown_text: Raw markdown text
            
        Returns:
            List of dictionaries containing header information
        """
        headers = []
        
        # Regex patterns for different header styles
        # ATX style: # Header
        atx_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        # Setext style: Header\n====== or Header\n------
        setext_pattern = re.compile(r'^(.+)\n([=\-])+$', re.MULTILINE)
        
        # Find ATX style headers
        for match in atx_pattern.finditer(markdown_text):
            level = len(match.group(1))
            text = match.group(2).strip()
            position = match.start()
            
            headers.append({
                'level': level,
                'text': text,
                'position': position,
                'style': 'atx'
            })
        
        # Find Setext style headers
        for match in setext_pattern.finditer(markdown_text):
            text = match.group(1).strip()
            underline = match.group(2)
            level = 1 if underline[0] == '=' else 2
            position = match.start()
            
            headers.append({
                'level': level,
                'text': text,
                'position': position,
                'style': 'setext'
            })
        
        # Sort by position to maintain document order
        headers.sort(key=lambda x: x['position'])
        
        return headers
    
    def _has_code_blocks(self, markdown_text: str) -> bool:
        """
        Check if markdown contains code blocks.
        
        Args:
            markdown_text: Raw markdown text
            
        Returns:
            True if code blocks are present
        """
        # Check for fenced code blocks (``` or ~~~)
        fenced_pattern = re.compile(r'^```|^~~~', re.MULTILINE)
        if fenced_pattern.search(markdown_text):
            return True
        
        # Check for indented code blocks (4 spaces or tab)
        indented_pattern = re.compile(r'^(    |\t).+$', re.MULTILINE)
        if indented_pattern.search(markdown_text):
            return True
        
        return False
    
    def _has_tables(self, markdown_text: str) -> bool:
        """
        Check if markdown contains tables.
        
        Args:
            markdown_text: Raw markdown text
            
        Returns:
            True if tables are present
        """
        # Check for table separator line (|---|---|)
        table_pattern = re.compile(r'^\|?[\s\-:|]+\|[\s\-:|]+\|?$', re.MULTILINE)
        return bool(table_pattern.search(markdown_text))
    
    def extract_sections(self, markdown_text: str) -> List[Dict]:
        """
        Extract sections based on headers.
        
        This method splits the markdown into sections based on headers,
        useful for intelligent chunking.
        
        Args:
            markdown_text: Raw markdown text
            
        Returns:
            List of sections with header and content
        """
        headers = self._extract_headers(markdown_text)
        
        if not headers:
            # No headers, return entire content as one section
            return [{
                'level': 0,
                'title': 'Document',
                'content': markdown_text
            }]
        
        sections = []
        lines = markdown_text.split('\n')
        
        for i, header in enumerate(headers):
            # Find start and end positions
            start_line = markdown_text[:header['position']].count('\n')
            
            # Find end position (next header or end of document)
            if i < len(headers) - 1:
                end_pos = headers[i + 1]['position']
                end_line = markdown_text[:end_pos].count('\n')
            else:
                end_line = len(lines)
            
            # Extract content for this section
            section_lines = lines[start_line:end_line]
            content = '\n'.join(section_lines)
            
            sections.append({
                'level': header['level'],
                'title': header['text'],
                'content': content
            })
        
        return sections
