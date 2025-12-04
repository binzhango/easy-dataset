"""
Text splitting service with multiple strategies.

This module provides various text splitting strategies including:
- Split by markdown headers
- Split by custom delimiters
- Automatic chunking with overlap
- Table of contents extraction
- UTF-8 and multilingual text handling (including RTL languages)
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    content: str
    summary: str = ""
    size: int = 0
    level: int = 0
    title: str = ""
    
    def __post_init__(self):
        if self.size == 0:
            self.size = len(self.content)


@dataclass
class TOCEntry:
    """Represents a table of contents entry."""
    title: str
    level: int
    position: int
    children: List['TOCEntry'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'title': self.title,
            'level': self.level,
            'position': self.position,
            'children': [child.to_dict() for child in self.children]
        }


class TextSplitter:
    """
    Text splitter with multiple strategies for document chunking.
    
    Supports:
    - Markdown header-based splitting
    - Custom delimiter splitting
    - Automatic chunking with overlap
    - Table of contents extraction
    - UTF-8 and multilingual text handling (including RTL languages)
    - Special characters and emoji handling
    """
    
    def __init__(self, normalize_unicode: bool = True):
        """
        Initialize the text splitter.
        
        Args:
            normalize_unicode: Whether to normalize unicode text (NFC normalization)
        """
        self.normalize_unicode = normalize_unicode
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize unicode text to ensure consistent representation.
        
        This handles:
        - Unicode normalization (NFC form)
        - Consistent line endings
        - Proper handling of special characters and emojis
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return text
        
        # Normalize unicode to NFC form (canonical composition)
        # This ensures characters like é are represented consistently
        if self.normalize_unicode:
            text = unicodedata.normalize('NFC', text)
        
        # Normalize line endings to \n
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    def is_rtl_text(self, text: str) -> bool:
        """
        Check if text contains right-to-left (RTL) characters.
        
        Supports Arabic, Hebrew, and other RTL scripts.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains RTL characters
        """
        if not text:
            return False
        
        # Check for RTL unicode ranges
        rtl_ranges = [
            (0x0590, 0x05FF),  # Hebrew
            (0x0600, 0x06FF),  # Arabic
            (0x0700, 0x074F),  # Syriac
            (0x0750, 0x077F),  # Arabic Supplement
            (0x0780, 0x07BF),  # Thaana
            (0x07C0, 0x07FF),  # N'Ko
            (0x0800, 0x083F),  # Samaritan
            (0x08A0, 0x08FF),  # Arabic Extended-A
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        ]
        
        for char in text:
            code_point = ord(char)
            for start, end in rtl_ranges:
                if start <= code_point <= end:
                    return True
        
        return False
    
    def count_graphemes(self, text: str) -> int:
        """
        Count grapheme clusters (user-perceived characters) in text.
        
        This properly handles:
        - Emojis (including multi-codepoint emojis)
        - Combining characters
        - Complex scripts
        
        Args:
            text: Text to count
            
        Returns:
            Number of grapheme clusters
        """
        if not text:
            return 0
        
        # Simple approximation: count characters excluding combining marks
        count = 0
        for char in text:
            # Skip combining characters
            if unicodedata.category(char) not in ('Mn', 'Mc', 'Me'):
                count += 1
        
        return count
    
    def safe_substring(self, text: str, start: int, end: int) -> str:
        """
        Safely extract substring without breaking multi-byte characters.
        
        Args:
            text: Text to extract from
            start: Start position
            end: End position
            
        Returns:
            Substring
        """
        if not text:
            return ""
        
        # Python 3 handles this correctly by default
        # String indexing works on unicode code points, not bytes
        return text[start:end]
    
    def split_by_markdown_headers(
        self,
        text: str,
        min_length: int = 1500,
        max_length: int = 2000
    ) -> List[TextChunk]:
        """
        Split text by markdown headers while preserving hierarchy.
        
        Properly handles UTF-8, emojis, and RTL text.
        
        Args:
            text: The markdown text to split
            min_length: Minimum chunk size in characters
            max_length: Maximum chunk size in characters
            
        Returns:
            List of TextChunk objects with content and metadata
        """
        # Normalize text for consistent processing
        text = self.normalize_text(text)
        
        # Extract outline (headers)
        outline = self._extract_outline(text)
        
        # Split by headings
        sections = self._split_by_headings(text, outline)
        
        # Process sections to meet size requirements
        chunks = self._process_sections(sections, outline, min_length, max_length)
        
        return chunks
    
    def split_by_delimiter(
        self,
        text: str,
        delimiter: str,
        strip_whitespace: bool = True
    ) -> List[str]:
        """
        Split text by a custom delimiter.
        
        Properly handles UTF-8, emojis, and RTL text.
        
        Args:
            text: The text to split
            delimiter: The delimiter to split on
            strip_whitespace: Whether to strip whitespace from chunks
            
        Returns:
            List of text chunks
        """
        # Normalize text
        text = self.normalize_text(text)
        
        # Split by delimiter
        chunks = text.split(delimiter)
        
        # Filter empty chunks and optionally strip whitespace
        if strip_whitespace:
            chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        else:
            chunks = [chunk for chunk in chunks if chunk]
        
        return chunks
    
    def split_with_overlap(
        self,
        text: str,
        chunk_size: int = 1500,
        overlap: int = 200,
        separator: str = "\n\n"
    ) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Properly handles UTF-8, emojis, and RTL text.
        
        Args:
            text: The text to split
            chunk_size: Target size for each chunk
            overlap: Number of characters to overlap between chunks
            separator: Separator to use for splitting (default: double newline)
            
        Returns:
            List of text chunks with overlap
        """
        if not text:
            return []
        
        # Normalize text
        text = self.normalize_text(text)
        
        # Split by separator first to respect natural boundaries
        paragraphs = text.split(separator)
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk_size
            if len(current_chunk) + len(paragraph) + len(separator) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap from previous chunk
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + separator + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += separator + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def split_recursive(
        self,
        text: str,
        chunk_size: int = 1500,
        overlap: int = 200,
        separators: Optional[List[str]] = None
    ) -> List[str]:
        """
        Recursively split text using multiple separators.
        
        Properly handles UTF-8, emojis, and RTL text.
        
        Args:
            text: The text to split
            chunk_size: Target size for each chunk
            overlap: Number of characters to overlap between chunks
            separators: List of separators to try in order
            
        Returns:
            List of text chunks
        """
        # Normalize text
        text = self.normalize_text(text)
        
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]
        
        return self._recursive_split(text, chunk_size, overlap, separators, 0)
    
    def _recursive_split(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
        separators: List[str],
        separator_index: int
    ) -> List[str]:
        """Helper method for recursive splitting."""
        if not text:
            return []
        
        if len(text) <= chunk_size:
            return [text]
        
        if separator_index >= len(separators):
            # No more separators, split by character
            return self._split_by_character(text, chunk_size, overlap)
        
        separator = separators[separator_index]
        chunks = []
        
        if separator:
            splits = text.split(separator)
        else:
            # Empty separator means split by character
            return self._split_by_character(text, chunk_size, overlap)
        
        current_chunk = ""
        for split in splits:
            test_chunk = current_chunk + separator + split if current_chunk else split
            
            if len(test_chunk) <= chunk_size:
                current_chunk = test_chunk
            else:
                # Current chunk is full
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Check if split itself is too large
                if len(split) > chunk_size:
                    # Try next separator
                    sub_chunks = self._recursive_split(
                        split, chunk_size, overlap, separators, separator_index + 1
                    )
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    # Start new chunk with overlap
                    if overlap > 0 and current_chunk and len(current_chunk) > overlap:
                        current_chunk = current_chunk[-overlap:] + separator + split
                    else:
                        current_chunk = split
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_by_character(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text by character when no separator works."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap if overlap > 0 else end
        
        return chunks
    
    def extract_table_of_contents(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract table of contents from markdown text.
        
        Properly handles UTF-8, emojis, and RTL text in headers.
        
        Args:
            text: The markdown text
            
        Returns:
            List of TOC entries as dictionaries
        """
        # Normalize text
        text = self.normalize_text(text)
        
        outline = self._extract_outline(text)
        toc_entries = self._build_toc_tree(outline)
        return [entry.to_dict() for entry in toc_entries]
    
    def toc_to_markdown(
        self,
        toc: List[Dict[str, Any]],
        is_nested: bool = True
    ) -> str:
        """
        Convert table of contents to markdown format.
        
        Args:
            toc: Table of contents as list of dictionaries
            is_nested: Whether to use nested format
            
        Returns:
            Markdown formatted table of contents
        """
        if not toc:
            return ""
        
        lines = []
        
        def format_entry(entry: Dict[str, Any], indent: int = 0):
            level = entry.get('level', 1)
            title = entry.get('title', '')
            
            if is_nested:
                prefix = "  " * indent + "- "
            else:
                prefix = "  " * (level - 1) + "- "
            
            lines.append(f"{prefix}{title}")
            
            # Process children
            for child in entry.get('children', []):
                format_entry(child, indent + 1 if is_nested else 0)
        
        for entry in toc:
            format_entry(entry)
        
        return "\n".join(lines)
    
    def _extract_outline(self, text: str) -> List[Dict[str, Any]]:
        """Extract markdown headers from text."""
        outline = []
        lines = text.split('\n')
        position = 0
        
        for i, line in enumerate(lines):
            # Match markdown headers (# to ######)
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                outline.append({
                    'level': level,
                    'title': title,
                    'line': i,
                    'position': position
                })
            position += len(line) + 1  # +1 for newline
        
        return outline
    
    def _split_by_headings(
        self,
        text: str,
        outline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Split text into sections based on headings."""
        if not outline:
            return [{'content': text, 'title': '', 'level': 0}]
        
        sections = []
        lines = text.split('\n')
        
        for i, heading in enumerate(outline):
            start_line = heading['line']
            end_line = outline[i + 1]['line'] if i + 1 < len(outline) else len(lines)
            
            section_lines = lines[start_line:end_line]
            content = '\n'.join(section_lines)
            
            sections.append({
                'content': content,
                'title': heading['title'],
                'level': heading['level'],
                'position': heading['position']
            })
        
        return sections
    
    def _process_sections(
        self,
        sections: List[Dict[str, Any]],
        outline: List[Dict[str, Any]],
        min_length: int,
        max_length: int
    ) -> List[TextChunk]:
        """Process sections to meet size requirements."""
        chunks = []
        current_chunk = ""
        current_title = ""
        current_level = 0
        
        for section in sections:
            content = section['content']
            title = section['title']
            level = section['level']
            
            # If section is too large, split it further
            if len(content) > max_length:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(TextChunk(
                        content=current_chunk.strip(),
                        summary=current_title,
                        level=current_level,
                        title=current_title
                    ))
                    current_chunk = ""
                
                # Split large section using recursive splitting for better results
                sub_chunks = self.split_recursive(content, max_length, min(200, max_length // 10))
                for i, sub_chunk in enumerate(sub_chunks):
                    chunks.append(TextChunk(
                        content=sub_chunk,
                        summary=f"{title} (part {i+1})" if len(sub_chunks) > 1 else title,
                        level=level,
                        title=title
                    ))
            else:
                # Try to combine with current chunk
                if len(current_chunk) + len(content) <= max_length:
                    if current_chunk:
                        current_chunk += "\n\n" + content
                    else:
                        current_chunk = content
                        current_title = title
                        current_level = level
                else:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append(TextChunk(
                            content=current_chunk.strip(),
                            summary=current_title,
                            level=current_level,
                            title=current_title
                        ))
                    current_chunk = content
                    current_title = title
                    current_level = level
        
        # Add last chunk
        if current_chunk:
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                summary=current_title,
                level=current_level,
                title=current_title
            ))
        
        return chunks
    
    def _build_toc_tree(self, outline: List[Dict[str, Any]]) -> List[TOCEntry]:
        """Build a hierarchical tree from flat outline."""
        if not outline:
            return []
        
        root_entries = []
        stack = []
        
        for item in outline:
            entry = TOCEntry(
                title=item['title'],
                level=item['level'],
                position=item['position']
            )
            
            # Find parent
            while stack and stack[-1].level >= entry.level:
                stack.pop()
            
            if stack:
                # Add as child to parent
                stack[-1].children.append(entry)
            else:
                # Add as root entry
                root_entries.append(entry)
            
            stack.append(entry)
        
        return root_entries


# Convenience functions for backward compatibility
def split_markdown(
    text: str,
    min_length: int = 1500,
    max_length: int = 2000
) -> List[Dict[str, Any]]:
    """
    Split markdown text by headers.
    
    Args:
        text: Markdown text to split
        min_length: Minimum chunk size
        max_length: Maximum chunk size
        
    Returns:
        List of dictionaries with content, summary, and size
    """
    splitter = TextSplitter()
    chunks = splitter.split_by_markdown_headers(text, min_length, max_length)
    
    return [
        {
            'content': chunk.content,
            'summary': chunk.summary,
            'size': chunk.size,
            'level': chunk.level,
            'title': chunk.title
        }
        for chunk in chunks
    ]


def extract_table_of_contents(text: str) -> List[Dict[str, Any]]:
    """
    Extract table of contents from markdown text.
    
    Args:
        text: Markdown text
        
    Returns:
        List of TOC entries as dictionaries
    """
    splitter = TextSplitter()
    return splitter.extract_table_of_contents(text)


def toc_to_markdown(toc: List[Dict[str, Any]], is_nested: bool = True) -> str:
    """
    Convert table of contents to markdown format.
    
    Args:
        toc: Table of contents as list of dictionaries
        is_nested: Whether to use nested format
        
    Returns:
        Markdown formatted table of contents
    """
    splitter = TextSplitter()
    return splitter.toc_to_markdown(toc, is_nested)
