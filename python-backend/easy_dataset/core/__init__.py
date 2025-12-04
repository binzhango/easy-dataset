"""
Core business logic module (framework-agnostic).

This module contains the core functionality that can be used
independently of any web framework or UI layer.
"""

from easy_dataset.core.easy_dataset import EasyDataset
from easy_dataset.core.file_processor import (
    FileProcessor,
    FileType,
    ProcessedDocument,
    FileTypeDetector,
    FileStorageUtil,
    ProcessorRegistry,
    get_registry,
)

__all__ = [
    "EasyDataset",
    "FileProcessor",
    "FileType",
    "ProcessedDocument",
    "FileTypeDetector",
    "FileStorageUtil",
    "ProcessorRegistry",
    "get_registry",
]
