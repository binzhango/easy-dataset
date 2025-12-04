# File Processing Services

This document describes the file processing services implemented for the Easy Dataset Python backend.

## Overview

The file processing system provides a unified interface for extracting content from various document formats. It follows a plugin-based architecture where each file format has its own processor implementation.

## Architecture

### Base Components

1. **FileProcessor (Abstract Base Class)**
   - Defines the interface all processors must implement
   - Provides common validation logic
   - Located in: `easy_dataset/core/file_processor.py`

2. **ProcessedDocument**
   - Container for extracted content, metadata, and images
   - Returned by all processors

3. **FileTypeDetector**
   - Detects file types from extensions and MIME types
   - Supports: PDF, Markdown, DOCX, EPUB, TXT

4. **ProcessorRegistry**
   - Manages processor instances
   - Routes files to appropriate processors
   - Global singleton instance available via `get_registry()`

### Processor Implementations

All processors are located in `easy_dataset/core/processors/`:

#### 1. PDFProcessor (`pdf_processor.py`)
- **Library**: PyPDF2
- **Features**:
  - Text extraction from all pages
  - Metadata extraction (title, author, etc.)
  - Image extraction with base64 encoding
  - Page-by-page processing
- **Validates**: Requirements 2.1, 14.5

#### 2. MarkdownProcessor (`markdown_processor.py`)
- **Library**: markdown
- **Features**:
  - Structure preservation
  - Header hierarchy extraction (ATX and Setext styles)
  - Code block detection
  - Table detection
  - Section extraction for intelligent chunking
- **Validates**: Requirements 2.2

#### 3. DOCXProcessor (`docx_processor.py`)
- **Library**: python-docx
- **Features**:
  - Text extraction with formatting
  - Paragraph structure preservation
  - Table extraction (markdown-like format)
  - Heading detection and formatting
  - Metadata extraction (title, author, dates)
- **Validates**: Requirements 2.3

#### 4. EPUBProcessor (`epub_processor.py`)
- **Libraries**: ebooklib, beautifulsoup4
- **Features**:
  - Chapter extraction
  - Metadata extraction (title, author, language, etc.)
  - Navigation structure (table of contents)
  - HTML content parsing
  - Multi-chapter document handling
- **Validates**: Requirements 2.4

#### 5. TXTProcessor (`txt_processor.py`)
- **Library**: chardet
- **Features**:
  - Automatic encoding detection
  - Fallback encoding support (UTF-8, Latin-1, Windows-1252, ASCII)
  - Line ending detection (CRLF, LF, CR)
  - Character statistics
  - Non-ASCII character detection
- **Validates**: Requirements 2.5

## Usage

### Basic Usage

```python
from pathlib import Path
from easy_dataset.core.file_processor import get_registry
from easy_dataset.core.processors import register_all_processors

# Register all processors (do this once at startup)
register_all_processors()

# Get the global registry
registry = get_registry()

# Process a file
document = registry.process_file(Path("document.pdf"))

# Access content
print(document.content)
print(document.metadata)
print(f"Found {len(document.images)} images")
```

### Using Specific Processors

```python
from pathlib import Path
from easy_dataset.core.processors import PDFProcessor

# Create processor instance
processor = PDFProcessor(extract_images=True)

# Process file
document = processor.process(Path("document.pdf"))
```

### File Type Detection

```python
from pathlib import Path
from easy_dataset.core.file_processor import FileTypeDetector, FileType

# Detect from path
file_type = FileTypeDetector.detect(Path("document.pdf"))
print(file_type)  # FileType.PDF

# Check if supported
if file_type != FileType.UNKNOWN:
    print("File type is supported")
```

## File Validation

All processors validate files before processing:

- File existence check
- File size limit (100MB max)
- Empty file detection
- File type verification

```python
from easy_dataset.core.processors import TXTProcessor

processor = TXTProcessor()

try:
    processor.validate_file(Path("document.txt"))
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Validation error: {e}")
```

## Metadata Extraction

Each processor extracts format-specific metadata:

### PDF Metadata
- `page_count`: Number of pages
- `title`, `author`, `subject`: Document properties
- `creator`, `producer`: Software information
- `creation_date`, `modification_date`: Timestamps

### Markdown Metadata
- `header_count`: Number of headers
- `headers`: List of headers with level and text
- `has_code_blocks`: Boolean
- `has_tables`: Boolean
- `line_count`: Number of lines

### DOCX Metadata
- `paragraph_count`: Number of paragraphs
- `table_count`: Number of tables
- `heading_count`: Number of headings
- `title`, `author`, `subject`: Document properties
- `created`, `modified`: Timestamps

### EPUB Metadata
- `chapter_count`: Number of chapters
- `chapters`: List of chapters with title and content
- `title`, `authors`, `language`: Book properties
- `publisher`, `publication_date`: Publishing info
- `identifier`: ISBN or other identifier

### TXT Metadata
- `encoding`: Detected encoding
- `line_count`, `character_count`, `word_count`: Statistics
- `has_non_ascii`: Boolean
- `line_ending`: Line ending style (CRLF/LF/CR)

## Error Handling

All processors follow consistent error handling:

```python
try:
    document = registry.process_file(path)
except FileNotFoundError:
    # File doesn't exist
    pass
except ValueError as e:
    # Invalid file format or validation error
    print(f"Validation error: {e}")
except IOError as e:
    # File reading error
    print(f"IO error: {e}")
```

## Testing

Comprehensive tests are available in `tests/test_file_processors.py`:

```bash
# Run all file processor tests
pytest tests/test_file_processors.py -v

# Run specific test class
pytest tests/test_file_processors.py::TestFileTypeDetector -v
```

Test coverage includes:
- File type detection
- Processor instantiation
- Registry functionality
- Document creation
- File validation

## Dependencies

Required packages (already in `requirements.txt`):

```
pypdf2>=3.0.0          # PDF processing
python-docx>=0.8.11    # DOCX processing
ebooklib>=0.18         # EPUB processing
beautifulsoup4>=4.12.0 # HTML parsing for EPUB
chardet>=5.0.0         # Encoding detection
markdown>=3.4.0        # Markdown processing
```

## Future Enhancements

Potential improvements for future versions:

1. **Additional Formats**
   - RTF (Rich Text Format)
   - ODT (OpenDocument Text)
   - HTML files

2. **Enhanced Features**
   - OCR support for scanned PDFs
   - Image text extraction
   - Table structure preservation
   - Better formatting preservation

3. **Performance**
   - Streaming for large files
   - Parallel processing
   - Caching mechanisms

4. **Advanced Processing**
   - Language detection
   - Content classification
   - Automatic summarization

## Related Documentation

- [Design Document](../.kiro/specs/js-to-python-conversion/design.md)
- [Requirements Document](../.kiro/specs/js-to-python-conversion/requirements.md)
- [Task List](../.kiro/specs/js-to-python-conversion/tasks.md)

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review the example in `examples/file_processing_example.py`
3. Refer to the inline documentation in each processor
