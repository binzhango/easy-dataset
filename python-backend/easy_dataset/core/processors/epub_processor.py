"""
EPUB file processor implementation.

This module provides EPUB (electronic publication) document processing using ebooklib.
It extracts chapter content, metadata (title, author, etc.), and handles navigation structure.
"""

from pathlib import Path
from typing import Dict, List
import html

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError(
        "ebooklib and beautifulsoup4 are required for EPUB processing. "
        "Install them with: pip install ebooklib beautifulsoup4"
    )

from ..file_processor import FileProcessor, FileType, ProcessedDocument


class EPUBProcessor(FileProcessor):
    """
    Processor for EPUB (electronic publication) documents.
    
    Extracts chapter content, metadata (title, author, language, etc.),
    and handles navigation structure. Uses ebooklib for EPUB parsing.
    """
    
    def supports(self, file_type: FileType) -> bool:
        """Check if this processor supports EPUB files."""
        return file_type == FileType.EPUB
    
    def process(self, file_path: Path) -> ProcessedDocument:
        """
        Process an EPUB file and extract its content.
        
        Args:
            file_path: Path to the EPUB file
            
        Returns:
            ProcessedDocument containing text, chapters, and metadata
            
        Raises:
            ValueError: If EPUB is invalid or corrupted
            IOError: If file cannot be read
        """
        self.validate_file(file_path)
        
        try:
            # Read the EPUB file
            book = epub.read_epub(str(file_path))
            
            # Extract chapters
            chapters = self._extract_chapters(book)
            
            # Combine all chapter text
            text_content = self._combine_chapters(chapters)
            
            # Extract metadata
            metadata = self._extract_metadata(book)
            metadata['chapter_count'] = len(chapters)
            metadata['chapters'] = chapters
            
            return ProcessedDocument(
                content=text_content,
                metadata=metadata,
                images=[]
            )
            
        except Exception as e:
            raise IOError(f"Error reading EPUB file: {e}")
    
    def _extract_chapters(self, book: epub.EpubBook) -> List[Dict]:
        """
        Extract chapters from EPUB book.
        
        Args:
            book: ebooklib EpubBook instance
            
        Returns:
            List of chapter dictionaries with title and content
        """
        chapters = []
        
        # Get all document items (chapters)
        for item in book.get_items():
            # Only process document items (XHTML content)
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Extract chapter content
                content = item.get_content()
                
                # Parse HTML content
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract title (from h1, h2, or title tag)
                title = self._extract_chapter_title(soup, item)
                
                # Extract text content
                text = self._extract_text_from_html(soup)
                
                if text.strip():
                    chapters.append({
                        'title': title,
                        'content': text,
                        'id': item.get_id() if hasattr(item, 'get_id') else None,
                    })
        
        return chapters
    
    def _extract_chapter_title(self, soup: BeautifulSoup, item) -> str:
        """
        Extract chapter title from HTML content.
        
        Args:
            soup: BeautifulSoup parsed HTML
            item: EPUB item
            
        Returns:
            Chapter title
        """
        # Try to find title in various places
        
        # 1. Look for h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # 2. Look for h2 tag
        h2 = soup.find('h2')
        if h2:
            return h2.get_text().strip()
        
        # 3. Look for title tag
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        # 4. Use item file name as fallback
        if hasattr(item, 'file_name'):
            return Path(item.file_name).stem
        
        return "Untitled Chapter"
    
    def _extract_text_from_html(self, soup: BeautifulSoup) -> str:
        """
        Extract plain text from HTML content.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Plain text content
        """
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _combine_chapters(self, chapters: List[Dict]) -> str:
        """
        Combine all chapters into a single text.
        
        Args:
            chapters: List of chapter dictionaries
            
        Returns:
            Combined text with chapter separators
        """
        text_parts = []
        
        for i, chapter in enumerate(chapters):
            # Add chapter header
            text_parts.append(f"# {chapter['title']}\n")
            text_parts.append(chapter['content'])
            
            # Add separator between chapters (except last one)
            if i < len(chapters) - 1:
                text_parts.append("\n\n---\n\n")
        
        return ''.join(text_parts)
    
    def _extract_metadata(self, book: epub.EpubBook) -> Dict:
        """
        Extract metadata from EPUB book.
        
        Args:
            book: ebooklib EpubBook instance
            
        Returns:
            Dictionary containing book metadata
        """
        metadata = {}
        
        # Extract title
        title = book.get_metadata('DC', 'title')
        if title:
            metadata['title'] = title[0][0] if title else None
        
        # Extract author(s)
        authors = book.get_metadata('DC', 'creator')
        if authors:
            metadata['authors'] = [author[0] for author in authors]
        
        # Extract language
        language = book.get_metadata('DC', 'language')
        if language:
            metadata['language'] = language[0][0] if language else None
        
        # Extract publisher
        publisher = book.get_metadata('DC', 'publisher')
        if publisher:
            metadata['publisher'] = publisher[0][0] if publisher else None
        
        # Extract publication date
        date = book.get_metadata('DC', 'date')
        if date:
            metadata['publication_date'] = date[0][0] if date else None
        
        # Extract description
        description = book.get_metadata('DC', 'description')
        if description:
            metadata['description'] = description[0][0] if description else None
        
        # Extract identifier (ISBN, etc.)
        identifier = book.get_metadata('DC', 'identifier')
        if identifier:
            metadata['identifier'] = identifier[0][0] if identifier else None
        
        # Extract subject/tags
        subjects = book.get_metadata('DC', 'subject')
        if subjects:
            metadata['subjects'] = [subject[0] for subject in subjects]
        
        return metadata
    
    def extract_navigation(self, book: epub.EpubBook) -> List[Dict]:
        """
        Extract navigation structure (table of contents).
        
        Args:
            book: ebooklib EpubBook instance
            
        Returns:
            List of navigation items with title and link
        """
        navigation = []
        
        # Get table of contents
        toc = book.toc
        
        def process_toc_item(item, level=0):
            """Recursively process TOC items."""
            if isinstance(item, tuple):
                # It's a section with nested items
                section = item[0]
                if hasattr(section, 'title'):
                    navigation.append({
                        'title': section.title,
                        'href': section.href if hasattr(section, 'href') else None,
                        'level': level,
                    })
                
                # Process nested items
                for nested_item in item[1]:
                    process_toc_item(nested_item, level + 1)
            else:
                # It's a single item
                if hasattr(item, 'title'):
                    navigation.append({
                        'title': item.title,
                        'href': item.href if hasattr(item, 'href') else None,
                        'level': level,
                    })
        
        # Process all TOC items
        for item in toc:
            process_toc_item(item)
        
        return navigation
