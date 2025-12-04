"""
Example demonstrating text splitting functionality.

This example shows how to use the TextSplitter class to:
- Split markdown by headers
- Split by custom delimiters
- Split with overlap
- Extract table of contents
- Handle multilingual text
"""

from easy_dataset.core.text_splitter import TextSplitter, split_markdown, extract_table_of_contents, toc_to_markdown


def example_markdown_splitting():
    """Example: Split markdown by headers."""
    print("=" * 60)
    print("Example 1: Markdown Header Splitting")
    print("=" * 60)
    
    markdown_text = """# Introduction
This is the introduction section with some content.

## Background
Here we discuss the background of the topic.

### Historical Context
Some historical information goes here.

## Methodology
This section describes our methodology.

# Results
Here are the results of our study.

## Key Findings
The key findings are listed here.
"""
    
    splitter = TextSplitter()
    chunks = splitter.split_by_markdown_headers(markdown_text, min_length=50, max_length=200)
    
    print(f"\nSplit into {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:")
        print(f"  Title: {chunk.title}")
        print(f"  Level: {chunk.level}")
        print(f"  Size: {chunk.size} characters")
        print(f"  Content preview: {chunk.content[:80]}...")
        print()


def example_delimiter_splitting():
    """Example: Split by custom delimiter."""
    print("=" * 60)
    print("Example 2: Custom Delimiter Splitting")
    print("=" * 60)
    
    text = """Section 1: Introduction
This is the first section.
---
Section 2: Main Content
This is the second section.
---
Section 3: Conclusion
This is the final section."""
    
    splitter = TextSplitter()
    chunks = splitter.split_by_delimiter(text, "---")
    
    print(f"\nSplit into {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:")
        print(f"  {chunk[:50]}...")
        print()


def example_overlap_splitting():
    """Example: Split with overlap."""
    print("=" * 60)
    print("Example 3: Splitting with Overlap")
    print("=" * 60)
    
    text = """This is a long document that needs to be split into smaller chunks.
Each chunk should have some overlap with the previous chunk to maintain context.

Paragraph 1: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Paragraph 2: Ut enim ad minim veniam, quis nostrud exercitation ullamco.
Laboris nisi ut aliquip ex ea commodo consequat.

Paragraph 3: Duis aute irure dolor in reprehenderit in voluptate velit.
Esse cillum dolore eu fugiat nulla pariatur."""
    
    splitter = TextSplitter()
    chunks = splitter.split_with_overlap(text, chunk_size=150, overlap=30)
    
    print(f"\nSplit into {len(chunks)} chunks with 30-character overlap:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i} ({len(chunk)} chars):")
        print(f"  {chunk[:80]}...")
        print()


def example_toc_extraction():
    """Example: Extract table of contents."""
    print("=" * 60)
    print("Example 4: Table of Contents Extraction")
    print("=" * 60)
    
    markdown_text = """# User Guide

## Getting Started
### Installation
### Configuration

## Features
### Text Processing
### Question Generation
### Answer Generation

## Advanced Topics
### Custom Prompts
### API Integration

# Developer Guide

## Architecture
## API Reference
"""
    
    splitter = TextSplitter()
    toc = splitter.extract_table_of_contents(markdown_text)
    toc_markdown = splitter.toc_to_markdown(toc, is_nested=True)
    
    print("\nExtracted Table of Contents:\n")
    print(toc_markdown)
    print()


def example_multilingual_text():
    """Example: Handle multilingual text."""
    print("=" * 60)
    print("Example 5: Multilingual Text Handling")
    print("=" * 60)
    
    multilingual_text = """# Documentation 📚

## English Section
This is content in English.

## 中文部分
这是中文内容。包含中文字符和标点符号。

## القسم العربي
هذا محتوى باللغة العربية. يتم التعامل معه بشكل صحيح.

## Emoji Section 🎉
Text with emojis: 👋 🌍 🚀 ✨
"""
    
    splitter = TextSplitter()
    
    # Check for RTL text
    print("\nChecking for RTL text:")
    print(f"  Contains RTL: {splitter.is_rtl_text(multilingual_text)}")
    
    # Split the text
    chunks = splitter.split_by_markdown_headers(multilingual_text, min_length=20, max_length=200)
    
    print(f"\nSplit into {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}: {chunk.title}")
        print(f"  Preview: {chunk.content[:60]}...")
        print()


def example_convenience_functions():
    """Example: Use convenience functions."""
    print("=" * 60)
    print("Example 6: Convenience Functions")
    print("=" * 60)
    
    markdown_text = """# Quick Start
## Step 1
Content for step 1.
## Step 2
Content for step 2.
"""
    
    # Use convenience function
    chunks = split_markdown(markdown_text, min_length=10, max_length=100)
    
    print(f"\nUsing split_markdown() function:")
    print(f"  Created {len(chunks)} chunks")
    print(f"  First chunk: {chunks[0]['title']}")
    
    # Extract TOC using convenience function
    toc = extract_table_of_contents(markdown_text)
    toc_md = toc_to_markdown(toc)
    
    print(f"\nUsing extract_table_of_contents() function:")
    print(toc_md)
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("TEXT SPLITTER EXAMPLES")
    print("=" * 60 + "\n")
    
    example_markdown_splitting()
    example_delimiter_splitting()
    example_overlap_splitting()
    example_toc_extraction()
    example_multilingual_text()
    example_convenience_functions()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
