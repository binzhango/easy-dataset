# Text Splitter Module

The text splitter module provides comprehensive text chunking capabilities for the Easy Dataset Python backend. It supports multiple splitting strategies and handles UTF-8, multilingual text, emojis, and right-to-left (RTL) languages.

## Features

- **Markdown Header Splitting**: Split documents by markdown headers while preserving hierarchy
- **Custom Delimiter Splitting**: Split text using any custom delimiter
- **Overlap Chunking**: Create chunks with configurable overlap for context preservation
- **Recursive Splitting**: Intelligently split text using multiple separators
- **Table of Contents Extraction**: Extract and format document structure
- **UTF-8 Support**: Full support for Unicode, emojis, and special characters
- **RTL Language Support**: Proper handling of Arabic, Hebrew, and other RTL scripts
- **Multilingual Text**: Seamless processing of mixed-language documents

## Installation

The text splitter is included in the `easy_dataset` package:

```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from easy_dataset.core.text_splitter import TextSplitter

# Create a splitter instance
splitter = TextSplitter()

# Split markdown by headers
markdown = """# Chapter 1
Content here.

## Section 1.1
More content."""

chunks = splitter.split_by_markdown_headers(markdown, min_length=100, max_length=1000)
```

### Splitting Strategies

#### 1. Markdown Header Splitting

Split documents by markdown headers while preserving the document hierarchy:

```python
chunks = splitter.split_by_markdown_headers(
    text=markdown_text,
    min_length=1500,  # Minimum chunk size
    max_length=2000   # Maximum chunk size
)

for chunk in chunks:
    print(f"Title: {chunk.title}")
    print(f"Level: {chunk.level}")
    print(f"Content: {chunk.content}")
```

#### 2. Custom Delimiter Splitting

Split text using any custom delimiter:

```python
text = "Part 1|||Part 2|||Part 3"
chunks = splitter.split_by_delimiter(text, delimiter="|||")
# Returns: ["Part 1", "Part 2", "Part 3"]
```

#### 3. Overlap Chunking

Create chunks with overlap to maintain context:

```python
chunks = splitter.split_with_overlap(
    text=long_text,
    chunk_size=1500,
    overlap=200,
    separator="\n\n"
)
```

#### 4. Recursive Splitting

Intelligently split using multiple separators:

```python
chunks = splitter.split_recursive(
    text=text,
    chunk_size=1500,
    overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

### Table of Contents

Extract and format document structure:

```python
# Extract TOC
toc = splitter.extract_table_of_contents(markdown_text)

# Convert to markdown format
toc_markdown = splitter.toc_to_markdown(toc, is_nested=True)
print(toc_markdown)
```

### Multilingual Text Handling

The text splitter automatically handles UTF-8, emojis, and RTL languages:

```python
# Check for RTL text
is_rtl = splitter.is_rtl_text("مرحبا")  # True for Arabic

# Normalize text (handles line endings, unicode normalization)
normalized = splitter.normalize_text(text)

# Count grapheme clusters (user-perceived characters)
count = splitter.count_graphemes("Hello 👋")

# Safe substring extraction
substring = splitter.safe_substring(text, start=0, end=10)
```

### Convenience Functions

For quick usage, convenience functions are available:

```python
from easy_dataset.core.text_splitter import (
    split_markdown,
    extract_table_of_contents,
    toc_to_markdown
)

# Split markdown
chunks = split_markdown(markdown_text, min_length=1500, max_length=2000)

# Extract TOC
toc = extract_table_of_contents(markdown_text)

# Format TOC
toc_md = toc_to_markdown(toc, is_nested=True)
```

## API Reference

### TextSplitter Class

#### Constructor

```python
TextSplitter(normalize_unicode: bool = True)
```

- `normalize_unicode`: Whether to normalize unicode text (NFC normalization)

#### Methods

##### split_by_markdown_headers()

```python
split_by_markdown_headers(
    text: str,
    min_length: int = 1500,
    max_length: int = 2000
) -> List[TextChunk]
```

Split text by markdown headers while preserving hierarchy.

**Parameters:**
- `text`: The markdown text to split
- `min_length`: Minimum chunk size in characters
- `max_length`: Maximum chunk size in characters

**Returns:** List of `TextChunk` objects

##### split_by_delimiter()

```python
split_by_delimiter(
    text: str,
    delimiter: str,
    strip_whitespace: bool = True
) -> List[str]
```

Split text by a custom delimiter.

**Parameters:**
- `text`: The text to split
- `delimiter`: The delimiter to split on
- `strip_whitespace`: Whether to strip whitespace from chunks

**Returns:** List of text chunks

##### split_with_overlap()

```python
split_with_overlap(
    text: str,
    chunk_size: int = 1500,
    overlap: int = 200,
    separator: str = "\n\n"
) -> List[str]
```

Split text into chunks with overlap.

**Parameters:**
- `text`: The text to split
- `chunk_size`: Target size for each chunk
- `overlap`: Number of characters to overlap between chunks
- `separator`: Separator to use for splitting

**Returns:** List of text chunks with overlap

##### split_recursive()

```python
split_recursive(
    text: str,
    chunk_size: int = 1500,
    overlap: int = 200,
    separators: Optional[List[str]] = None
) -> List[str]
```

Recursively split text using multiple separators.

**Parameters:**
- `text`: The text to split
- `chunk_size`: Target size for each chunk
- `overlap`: Number of characters to overlap between chunks
- `separators`: List of separators to try in order (default: `["\n\n", "\n", ". ", " ", ""]`)

**Returns:** List of text chunks

##### extract_table_of_contents()

```python
extract_table_of_contents(text: str) -> List[Dict[str, Any]]
```

Extract table of contents from markdown text.

**Parameters:**
- `text`: The markdown text

**Returns:** List of TOC entries as dictionaries

##### toc_to_markdown()

```python
toc_to_markdown(
    toc: List[Dict[str, Any]],
    is_nested: bool = True
) -> str
```

Convert table of contents to markdown format.

**Parameters:**
- `toc`: Table of contents as list of dictionaries
- `is_nested`: Whether to use nested format

**Returns:** Markdown formatted table of contents

##### normalize_text()

```python
normalize_text(text: str) -> str
```

Normalize unicode text to ensure consistent representation.

**Parameters:**
- `text`: Text to normalize

**Returns:** Normalized text

##### is_rtl_text()

```python
is_rtl_text(text: str) -> bool
```

Check if text contains right-to-left (RTL) characters.

**Parameters:**
- `text`: Text to check

**Returns:** True if text contains RTL characters

##### count_graphemes()

```python
count_graphemes(text: str) -> int
```

Count grapheme clusters (user-perceived characters) in text.

**Parameters:**
- `text`: Text to count

**Returns:** Number of grapheme clusters

##### safe_substring()

```python
safe_substring(text: str, start: int, end: int) -> str
```

Safely extract substring without breaking multi-byte characters.

**Parameters:**
- `text`: Text to extract from
- `start`: Start position
- `end`: End position

**Returns:** Substring

### TextChunk Class

A dataclass representing a chunk of text with metadata:

```python
@dataclass
class TextChunk:
    content: str      # The text content
    summary: str      # Summary or title
    size: int         # Size in characters
    level: int        # Header level (for markdown)
    title: str        # Section title
```

### TOCEntry Class

A dataclass representing a table of contents entry:

```python
@dataclass
class TOCEntry:
    title: str                    # Entry title
    level: int                    # Header level
    position: int                 # Position in document
    children: List['TOCEntry']    # Child entries
```

## Examples

See `examples/text_splitting_example.py` for comprehensive examples demonstrating all features.

Run the examples:

```bash
python examples/text_splitting_example.py
```

## Testing

Run the test suite:

```bash
pytest tests/test_text_splitter.py -v
```

The test suite includes:
- Basic splitting functionality tests
- Edge case handling
- Multilingual text tests
- UTF-8 and emoji handling
- RTL language detection
- Performance tests with large documents

## Implementation Details

### Unicode Normalization

The text splitter uses NFC (Canonical Composition) normalization to ensure consistent representation of unicode characters. This is important for:
- Combining characters (e.g., é can be represented as one character or e + combining accent)
- Emoji with modifiers
- Complex scripts

### RTL Language Support

The splitter detects RTL text by checking for characters in the following unicode ranges:
- Hebrew (U+0590 to U+05FF)
- Arabic (U+0600 to U+06FF)
- Syriac, Thaana, N'Ko, Samaritan
- Arabic Presentation Forms

### Grapheme Counting

The `count_graphemes()` method provides a more accurate count of user-perceived characters by:
- Excluding combining marks
- Properly handling multi-codepoint emojis
- Supporting complex scripts

## Performance Considerations

- **Large Documents**: For documents over 10MB, consider processing in chunks
- **Memory Usage**: The splitter loads the entire document into memory
- **Regex Performance**: Header extraction uses regex, which is fast for most documents
- **Unicode Operations**: Unicode normalization adds minimal overhead

## Compatibility

- **Python Version**: Requires Python 3.9+
- **Dependencies**: No external dependencies (uses standard library)
- **Encoding**: Assumes UTF-8 encoding for all text

## Migration from JavaScript

This module replaces the JavaScript text splitter (`lib/file/text-splitter.js`) with equivalent functionality:

| JavaScript | Python |
|------------|--------|
| `splitFileByType()` | `split_by_markdown_headers()`, `split_by_delimiter()`, etc. |
| `markdownSplitter.splitMarkdown()` | `split_by_markdown_headers()` |
| `markdownSplitter.extractTableOfContents()` | `extract_table_of_contents()` |
| `markdownSplitter.tocToMarkdown()` | `toc_to_markdown()` |
| LangChain text splitters | Built-in splitting methods |

## License

This module is part of the Easy Dataset project and is licensed under AGPL-3.0.
