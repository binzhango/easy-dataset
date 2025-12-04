# Easy Dataset - Python Package

A reusable Python package for creating LLM fine-tuning datasets from documents.

## Features

- 📄 **Document Processing**: Support for PDF, DOCX, EPUB, Markdown, and TXT files
- ✂️ **Intelligent Text Chunking**: Multiple splitting strategies with configurable overlap
- 🤖 **AI-Powered Generation**: Question and answer generation using multiple LLM providers
- 🌐 **Multi-Provider Support**: OpenAI, Ollama, Gemini, OpenRouter, LiteLLM
- 📊 **Dataset Management**: Organize, filter, and rate your training data
- 💾 **Multiple Export Formats**: JSON, JSONL, CSV, Hugging Face, LLaMA Factory
- 🌍 **Internationalization**: Support for English, Chinese (zh-CN), and Turkish (tr)
- 🖼️ **Image Datasets**: Vision-language dataset creation with image support
- 💬 **Multi-turn Conversations**: Generate dialogue datasets for chat models

## Installation

### From PyPI (when published)

```bash
pip install easy-dataset
```

### From Source

```bash
git clone https://github.com/yourusername/easy-dataset-python
cd easy-dataset-python
pip install -e .
```

### With Optional Dependencies

```bash
# Install with FastAPI server support
pip install easy-dataset[server]

# Install with all LLM providers
pip install easy-dataset[llm]

# Install with desktop application support
pip install easy-dataset[desktop]

# Install everything including development tools
pip install easy-dataset[all]
```

## Quick Start

### As a Library

```python
from easy_dataset import EasyDataset

# Initialize
dataset = EasyDataset(database_url="sqlite:///my_dataset.db")

# Configure LLM provider
dataset.configure_llm({
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4"
})

# Create a project
project = dataset.create_project(
    name="My Project",
    description="Dataset for fine-tuning"
)

# Process a document
chunks = dataset.process_file(project.id, "document.pdf")

# Generate questions
questions = dataset.generate_questions(
    project.id,
    chunk_ids=[chunk.id for chunk in chunks]
)

# Generate answers
answers = dataset.generate_answers(
    project.id,
    question_ids=[q.id for q in questions]
)

# Export dataset
dataset.export_dataset(
    project_id=project.id,
    format="json",
    output_path="dataset.json"
)
```

### As a Standalone Server

```bash
# Start the FastAPI server
easy-dataset serve --port 8000

# Or with uvicorn directly
uvicorn easy_dataset_server.main:app --host 0.0.0.0 --port 8000
```

### Using the CLI

```bash
# Initialize a new project
easy-dataset init my-project --description "My dataset project"

# Process files
easy-dataset process my-project document.pdf

# Generate questions
easy-dataset generate-questions my-project --model gpt-4

# Generate answers
easy-dataset generate-answers my-project

# Export dataset
easy-dataset export my-project --format json --output dataset.json
```

## Usage Examples

See the `examples/` directory for more detailed usage examples:

- `standalone_server.py` - Running as a standalone API server
- `embedded_usage.py` - Using as a library in your application
- `custom_frontend.py` - Integrating with Flask/Django
- `batch_processing.py` - Batch processing multiple documents

## Supported LLM Providers

- **OpenAI**: GPT-3.5, GPT-4, GPT-4o, o1 models
- **Ollama**: Local models (Llama, Mistral, etc.)
- **Gemini**: Google's Gemini Pro and Gemini Pro Vision
- **OpenRouter**: Access to 100+ models through unified API
- **LiteLLM**: Unified interface for 100+ providers

## Supported File Formats

- **PDF**: Text extraction with pypdf2/pdfplumber
- **DOCX**: Microsoft Word documents
- **EPUB**: E-books with chapter extraction
- **Markdown**: With structure preservation
- **TXT**: Plain text with encoding detection

## Export Formats

- **JSON**: Standard JSON format for LLM training
- **JSONL**: JSON Lines for streaming processing
- **CSV**: Comma-separated values
- **Hugging Face**: Compatible with `datasets` library
- **LLaMA Factory**: Ready for LLaMA Factory training

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/easy-dataset-python
cd easy-dataset-python

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=easy_dataset --cov-report=html

# Run specific test file
pytest tests/test_file_processor.py
```

### Code Quality

```bash
# Format code with black
black easy_dataset/ easy_dataset_server/ tests/

# Lint with ruff
ruff check easy_dataset/ easy_dataset_server/

# Type check with mypy
mypy easy_dataset/
```

## Architecture

The package is designed with clear separation of concerns:

- **Core Layer** (`easy_dataset/core/`): Framework-agnostic business logic
- **Models Layer** (`easy_dataset/models/`): SQLAlchemy database models
- **Schemas Layer** (`easy_dataset/schemas/`): Pydantic validation schemas
- **LLM Layer** (`easy_dataset/llm/`): LLM provider integrations
- **Server Layer** (`easy_dataset_server/`): Optional FastAPI server
- **CLI Layer** (`easy_dataset/cli.py`): Command-line interface

## Documentation

Full documentation is available at: https://easy-dataset.readthedocs.io (coming soon)

## License

AGPL-3.0 - See LICENSE file for details

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## Support

- GitHub Issues: https://github.com/yourusername/easy-dataset-python/issues
- Documentation: https://easy-dataset.readthedocs.io

## Roadmap

- [x] Core package structure
- [ ] Document processing implementation
- [ ] LLM provider integrations
- [ ] FastAPI server
- [ ] Desktop application
- [ ] Complete test coverage
- [ ] Documentation
- [ ] PyPI publication

---

**Note**: This is version 2.0.0 - a complete rewrite of Easy Dataset in Python. The original JavaScript/TypeScript version remains available in the main branch.
