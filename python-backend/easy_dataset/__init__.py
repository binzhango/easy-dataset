"""
Easy Dataset - A reusable Python package for creating LLM fine-tuning datasets.

This package provides tools for:
- Document processing (PDF, DOCX, EPUB, Markdown, TXT)
- Intelligent text chunking
- AI-powered question and answer generation
- Dataset management and export
- Multi-format export (JSON, JSONL, CSV, Hugging Face, LLaMA Factory)
- Multi-language support (English, Chinese, Turkish)

Example usage:
    >>> from easy_dataset import EasyDataset
    >>> dataset = EasyDataset(database_url="sqlite:///my_dataset.db")
    >>> project = dataset.create_project(name="My Project", description="Test")
    >>> chunks = dataset.process_file(project.id, "document.pdf")
    >>> questions = dataset.generate_questions(project.id, [c.id for c in chunks])
"""

__version__ = "2.0.0"
__author__ = "Easy Dataset Contributors"
__license__ = "AGPL-3.0"

# Core functionality
from easy_dataset.core.easy_dataset import EasyDataset

# Models will be imported once implemented (task 3)
# from easy_dataset.models import Project, Chunk, Question, Dataset

# LLM providers will be imported once implemented (task 8)
# from easy_dataset.llm.providers import (
#     OpenAIProvider,
#     OllamaProvider,
#     GeminiProvider,
#     OpenRouterProvider,
#     LiteLLMProvider,
# )

__all__ = [
    "__version__",
    "EasyDataset",
    # "Project",
    # "Chunk",
    # "Question",
    # "Dataset",
    # "OpenAIProvider",
    # "OllamaProvider",
    # "GeminiProvider",
    # "OpenRouterProvider",
    # "LiteLLMProvider",
]
