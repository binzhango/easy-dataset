"""
Example: File Processing with Easy Dataset

This example demonstrates how to use the file processors to extract
content from various document formats.
"""

from pathlib import Path
from easy_dataset.core.file_processor import get_registry, FileTypeDetector
from easy_dataset.core.processors import register_all_processors


def process_file_example(file_path: str):
    """
    Process a file and display its content and metadata.
    
    Args:
        file_path: Path to the file to process
    """
    path = Path(file_path)
    
    # Ensure processors are registered
    register_all_processors()
    
    # Get the global registry
    registry = get_registry()
    
    # Detect file type
    file_type = FileTypeDetector.detect(path)
    print(f"Detected file type: {file_type.value}")
    
    # Process the file
    try:
        document = registry.process_file(path)
        
        print(f"\n{'='*60}")
        print(f"File: {path.name}")
        print(f"{'='*60}")
        
        # Display metadata
        print("\nMetadata:")
        for key, value in document.metadata.items():
            if key != 'chapters' and key != 'headers':  # Skip large nested data
                print(f"  {key}: {value}")
        
        # Display content preview (first 500 characters)
        print("\nContent Preview:")
        content_preview = document.content[:500]
        if len(document.content) > 500:
            content_preview += "..."
        print(content_preview)
        
        # Display image count if any
        if document.images:
            print(f"\nExtracted {len(document.images)} images")
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"Error processing file: {e}")


def main():
    """Main example function."""
    print("Easy Dataset File Processing Example")
    print("=" * 60)
    
    # Example: Process different file types
    # Note: You'll need to provide actual file paths
    
    example_files = [
        # "path/to/document.pdf",
        # "path/to/document.md",
        # "path/to/document.docx",
        # "path/to/book.epub",
        # "path/to/document.txt",
    ]
    
    if not example_files or not any(example_files):
        print("\nNo example files provided.")
        print("To use this example, add file paths to the example_files list.")
        print("\nExample usage:")
        print("  from easy_dataset.core.file_processor import get_registry")
        print("  from easy_dataset.core.processors import register_all_processors")
        print("  ")
        print("  register_all_processors()")
        print("  registry = get_registry()")
        print("  document = registry.process_file(Path('document.pdf'))")
        print("  print(document.content)")
        return
    
    for file_path in example_files:
        if file_path and Path(file_path).exists():
            process_file_example(file_path)


if __name__ == "__main__":
    main()
