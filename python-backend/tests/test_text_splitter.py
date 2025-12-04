"""
Tests for text splitter functionality.
"""

import pytest
from easy_dataset.core.text_splitter import TextSplitter, split_markdown, extract_table_of_contents, toc_to_markdown


class TestTextSplitter:
    """Test suite for TextSplitter class."""
    
    def test_split_by_markdown_headers_basic(self):
        """Test basic markdown header splitting."""
        markdown = """# Header 1
Content for header 1.

## Header 2
Content for header 2.

### Header 3
Content for header 3."""
        
        splitter = TextSplitter()
        chunks = splitter.split_by_markdown_headers(markdown, min_length=10, max_length=200)
        
        assert len(chunks) > 0
        assert all(chunk.content for chunk in chunks)
        assert all(chunk.size > 0 for chunk in chunks)
    
    def test_split_by_delimiter(self):
        """Test splitting by custom delimiter."""
        text = "Part 1|||Part 2|||Part 3"
        splitter = TextSplitter()
        chunks = splitter.split_by_delimiter(text, "|||")
        
        assert len(chunks) == 3
        assert chunks[0] == "Part 1"
        assert chunks[1] == "Part 2"
        assert chunks[2] == "Part 3"
    
    def test_split_by_delimiter_empty_parts(self):
        """Test that empty parts are filtered out."""
        text = "Part 1|||  |||Part 3"
        splitter = TextSplitter()
        chunks = splitter.split_by_delimiter(text, "|||")
        
        assert len(chunks) == 2
        assert "Part 1" in chunks
        assert "Part 3" in chunks
    
    def test_split_with_overlap(self):
        """Test splitting with overlap."""
        text = "A" * 100 + "\n\n" + "B" * 100 + "\n\n" + "C" * 100
        splitter = TextSplitter()
        chunks = splitter.split_with_overlap(text, chunk_size=150, overlap=20)
        
        assert len(chunks) > 1
        # Check that chunks respect size limit (with some tolerance for separators)
        for chunk in chunks:
            assert len(chunk) <= 170  # chunk_size + overlap + separator
    
    def test_split_recursive(self):
        """Test recursive splitting."""
        text = "Sentence 1. Sentence 2. Sentence 3. Sentence 4. Sentence 5."
        splitter = TextSplitter()
        chunks = splitter.split_recursive(text, chunk_size=30, overlap=5)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 35  # Some tolerance
    
    def test_extract_table_of_contents(self):
        """Test TOC extraction."""
        markdown = """# Main Title
Content here.

## Section 1
More content.

### Subsection 1.1
Even more content.

## Section 2
Final content."""
        
        splitter = TextSplitter()
        toc = splitter.extract_table_of_contents(markdown)
        
        assert len(toc) > 0
        assert toc[0]['title'] == 'Main Title'
        assert toc[0]['level'] == 1
    
    def test_toc_to_markdown(self):
        """Test TOC to markdown conversion."""
        toc = [
            {
                'title': 'Main',
                'level': 1,
                'position': 0,
                'children': [
                    {
                        'title': 'Sub',
                        'level': 2,
                        'position': 10,
                        'children': []
                    }
                ]
            }
        ]
        
        splitter = TextSplitter()
        markdown = splitter.toc_to_markdown(toc, is_nested=True)
        
        assert 'Main' in markdown
        assert 'Sub' in markdown
    
    def test_normalize_text(self):
        """Test text normalization."""
        splitter = TextSplitter()
        
        # Test line ending normalization
        text_with_crlf = "Line 1\r\nLine 2\rLine 3\n"
        normalized = splitter.normalize_text(text_with_crlf)
        assert '\r' not in normalized
        assert normalized.count('\n') == 3
    
    def test_is_rtl_text(self):
        """Test RTL text detection."""
        splitter = TextSplitter()
        
        # Arabic text
        arabic = "مرحبا"
        assert splitter.is_rtl_text(arabic) is True
        
        # Hebrew text
        hebrew = "שלום"
        assert splitter.is_rtl_text(hebrew) is True
        
        # English text
        english = "Hello"
        assert splitter.is_rtl_text(english) is False
    
    def test_utf8_handling(self):
        """Test UTF-8 text handling with emojis and special characters."""
        text = "Hello 👋 World 🌍! Special chars: é, ñ, 中文"
        splitter = TextSplitter()
        
        # Should not raise any errors
        normalized = splitter.normalize_text(text)
        assert "👋" in normalized
        assert "🌍" in normalized
        assert "中文" in normalized
    
    def test_split_markdown_with_emojis(self):
        """Test markdown splitting with emojis in headers."""
        markdown = """# 📚 Documentation
Content here.

## 🚀 Getting Started
More content."""
        
        splitter = TextSplitter()
        chunks = splitter.split_by_markdown_headers(markdown, min_length=10, max_length=200)
        
        assert len(chunks) > 0
        # Verify emojis are preserved
        combined = "".join(chunk.content for chunk in chunks)
        assert "📚" in combined
        assert "🚀" in combined
    
    def test_count_graphemes(self):
        """Test grapheme counting."""
        splitter = TextSplitter()
        
        # Simple ASCII
        assert splitter.count_graphemes("Hello") == 5
        
        # With emoji
        text_with_emoji = "Hi 👋"
        count = splitter.count_graphemes(text_with_emoji)
        assert count >= 3  # At least "H", "i", " ", and emoji
    
    def test_safe_substring(self):
        """Test safe substring extraction."""
        splitter = TextSplitter()
        
        text = "Hello 世界 👋"
        substring = splitter.safe_substring(text, 0, 5)
        assert substring == "Hello"
        
        # Should not break multi-byte characters
        substring = splitter.safe_substring(text, 6, 8)
        assert len(substring) == 2


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_split_markdown_function(self):
        """Test split_markdown convenience function."""
        markdown = "# Title\nContent"
        result = split_markdown(markdown, min_length=5, max_length=100)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'content' in result[0]
        assert 'summary' in result[0]
    
    def test_extract_table_of_contents_function(self):
        """Test extract_table_of_contents convenience function."""
        markdown = "# Title\n## Subtitle"
        result = extract_table_of_contents(markdown)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_toc_to_markdown_function(self):
        """Test toc_to_markdown convenience function."""
        toc = [{'title': 'Test', 'level': 1, 'position': 0, 'children': []}]
        result = toc_to_markdown(toc)
        
        assert isinstance(result, str)
        assert 'Test' in result


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_text(self):
        """Test handling of empty text."""
        splitter = TextSplitter()
        
        chunks = splitter.split_by_markdown_headers("", min_length=10, max_length=100)
        assert len(chunks) == 0 or (len(chunks) == 1 and not chunks[0].content.strip())
        
        chunks = splitter.split_by_delimiter("", "|||")
        assert len(chunks) == 0
        
        chunks = splitter.split_with_overlap("", chunk_size=100, overlap=10)
        assert len(chunks) == 0
    
    def test_no_headers(self):
        """Test text without headers."""
        text = "Just plain text without any headers."
        splitter = TextSplitter()
        
        chunks = splitter.split_by_markdown_headers(text, min_length=5, max_length=100)
        assert len(chunks) >= 1
    
    def test_very_long_section(self):
        """Test handling of very long sections."""
        long_text = "A" * 5000
        markdown = f"# Header\n{long_text}"
        
        splitter = TextSplitter()
        chunks = splitter.split_by_markdown_headers(markdown, min_length=100, max_length=1000)
        
        # Should split long section into multiple chunks
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.content) <= 1200  # Some tolerance
    
    def test_nested_headers(self):
        """Test deeply nested headers."""
        markdown = """# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
Content at deepest level."""
        
        splitter = TextSplitter()
        toc = splitter.extract_table_of_contents(markdown)
        
        assert len(toc) > 0
        # Check that hierarchy is preserved
        assert toc[0]['level'] == 1
    
    def test_special_delimiter(self):
        """Test splitting with special regex characters as delimiter."""
        text = "Part 1|Part 2|Part 3"
        splitter = TextSplitter()
        chunks = splitter.split_by_delimiter(text, "|")
        
        assert len(chunks) == 3
    
    def test_multilingual_text(self):
        """Test handling of multilingual text."""
        text = """# English Header
English content.

# 中文标题
中文内容。

# عنوان عربي
محتوى عربي.

# Заголовок
Содержание."""
        
        splitter = TextSplitter()
        chunks = splitter.split_by_markdown_headers(text, min_length=5, max_length=200)
        
        assert len(chunks) > 0
        # Verify all languages are preserved
        combined = "".join(chunk.content for chunk in chunks)
        assert "English" in combined
        assert "中文" in combined
        assert "عربي" in combined
        assert "Содержание" in combined


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
