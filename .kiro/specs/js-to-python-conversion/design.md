# Design Document

## Overview

This document outlines the technical design for converting the Easy Dataset application backend from JavaScript (Next.js) to Python as a **reusable Python package**. The conversion will maintain all existing functionality while leveraging Python's rich ecosystem for AI/ML applications, data processing, and web development.

**Important**: The frontend (React + Material-UI) will remain unchanged. Only the backend will be converted to Python.

**Key Design Decision**: The Python backend will be structured as a **reusable package** that can be:
- Installed via pip: `pip install easy-dataset`
- Used as a library in other Python projects
- Run as a standalone FastAPI server
- Embedded in different web frameworks (Flask, Django, etc.)
- Used programmatically without a web server

The Python backend will use modern frameworks and libraries:
- **Frontend**: React + Material-UI (unchanged, remains JavaScript)
- **Backend**: Reusable Python package with FastAPI integration (converted to Python)
- **Desktop**: Electron with Python backend (frontend unchanged, backend converted)
- **Database**: SQLAlchemy ORM with SQLite (converted to Python)
- **AI Integration**: LangChain, OpenAI SDK, and provider-specific libraries (converted to Python)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
│  (React + Material-UI - UNCHANGED, remains JavaScript)      │
│                                                              │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API / WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                   API Layer (FastAPI)                        │
│  - Route handlers                                            │
│  - Request validation (Pydantic)                            │
│  - Response serialization                                    │
│  - WebSocket for streaming                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Service Layer                                │
│  - Business logic                                            │
│  - Task orchestration                                        │
│  - LLM integration                                           │
│  - File processing                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Data Access Layer (SQLAlchemy)                  │
│  - ORM models                                                │
│  - Database operations                                       │
│  - Query builders                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                Database (SQLite)                             │
│  - Projects, Chunks, Questions, Datasets                     │
│  - Tasks, ModelConfig, Images                                │
└──────────────────────────────────────────────────────────────┘
```

### Module Structure

```
easy-dataset-python/
├── easy_dataset/               # Main package (installable)
│   ├── __init__.py            # Package exports
│   ├── core/                  # Core business logic (framework-agnostic)
│   │   ├── __init__.py
│   │   ├── file_processor.py
│   │   ├── text_splitter.py
│   │   ├── llm_client.py
│   │   ├── question_generator.py
│   │   ├── answer_generator.py
│   │   ├── dataset_manager.py
│   │   └── task_manager.py
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── chunk.py
│   │   ├── question.py
│   │   ├── dataset.py
│   │   ├── task.py
│   │   └── image.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── chunk.py
│   │   └── ...
│   ├── llm/                   # LLM integrations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── openai.py
│   │   │   ├── ollama.py
│   │   │   ├── openrouter.py
│   │   │   ├── litellm.py
│   │   │   └── gemini.py
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── question.py
│   │       ├── answer.py
│   │       └── evaluation.py
│   ├── database/              # Database utilities
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations/
│   ├── utils/                 # Helper functions
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── text_utils.py
│   │   └── validation.py
│   └── cli.py                 # CLI interface
├── easy_dataset_server/       # FastAPI server (optional)
│   ├── __init__.py
│   ├── main.py                # FastAPI application entry
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── chunks.py
│   │   ├── questions.py
│   │   ├── datasets.py
│   │   ├── tasks.py
│   │   ├── images.py
│   │   └── conversations.py
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── chunk.py
│   │   ├── question.py
│   │   ├── dataset.py
│   │   ├── task.py
│   │   └── image.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── chunk.py
│   │   └── ...
│   │   ├── projects.py
│   │   ├── chunks.py
│   │   ├── questions.py
│   │   ├── datasets.py
│   │   ├── tasks.py
│   │   ├── images.py
│   │   └── conversations.py
│   ├── dependencies.py        # FastAPI dependencies
│   └── config.py              # Server configuration
├── examples/                  # Usage examples
│   ├── standalone_server.py   # Run as standalone server
│   ├── embedded_usage.py      # Use as library
│   ├── custom_frontend.py     # Integrate with custom frontend
│   └── batch_processing.py    # Batch processing example
├── desktop/                    # Desktop application
│   ├── __init__.py
│   ├── main.py                # PyQt6 or Electron entry
│   └── resources/
├── frontend/                   # React frontend (UNCHANGED - keep existing)
│   └── ...                    # Existing Next.js/React code remains
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_api/
│   ├── test_services/
│   └── test_llm/
├── alembic/                    # Database migrations
│   └── versions/
├── locales/                    # i18n translations
│   ├── en/
│   ├── zh-CN/
│   └── tr/
├── setup.py                   # Package setup
├── pyproject.toml             # Modern package configuration
├── requirements.txt           # Dependencies
├── requirements-dev.txt       # Development dependencies
├── Dockerfile                 # Docker deployment
├── README.md                  # Package documentation
├── MANIFEST.in                # Package manifest
└── LICENSE                    # License file
```

## Package Architecture

### Design Philosophy

The backend is designed as a **reusable Python package** with clear separation between:
1. **Core business logic** (framework-agnostic)
2. **Web API layer** (FastAPI-specific, optional)
3. **CLI interface** (for command-line usage)

This allows developers to:
- Use the package programmatically in their own applications
- Run it as a standalone FastAPI server
- Integrate it with other web frameworks (Flask, Django, etc.)
- Use it in Jupyter notebooks for data processing
- Build custom frontends with any technology

### Package Usage Examples

#### 1. Programmatic Usage (Library)

```python
from easy_dataset import EasyDataset
from easy_dataset.llm import OpenAIProvider

# Initialize the dataset manager
dataset = EasyDataset(database_url="sqlite:///my_dataset.db")

# Configure LLM provider
llm_config = {
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4"
}
dataset.configure_llm(llm_config)

# Create a project
project = dataset.create_project(
    name="My Project",
    description="Dataset for fine-tuning"
)

# Process a file
file_path = "document.pdf"
chunks = dataset.process_file(project.id, file_path)

# Generate questions
questions = dataset.generate_questions(
    project_id=project.id,
    chunk_ids=[chunk.id for chunk in chunks]
)

# Generate answers
answers = dataset.generate_answers(
    project_id=project.id,
    question_ids=[q.id for q in questions]
)

# Export dataset
dataset.export_dataset(
    project_id=project.id,
    format="json",
    output_path="dataset.json"
)
```

#### 2. Standalone Server

```python
# easy_dataset_server/main.py
from fastapi import FastAPI
from easy_dataset_server.api import projects, chunks, questions, datasets

app = FastAPI(title="Easy Dataset API")

# Include routers
app.include_router(projects.router)
app.include_router(chunks.router)
app.include_router(questions.router)
app.include_router(datasets.router)

# Run with: uvicorn easy_dataset_server.main:app
```

#### 3. CLI Usage

```bash
# Install the package
pip install easy-dataset

# Initialize a new project
easy-dataset init my-project

# Process files
easy-dataset process my-project document.pdf

# Generate questions
easy-dataset generate-questions my-project --model gpt-4

# Generate answers
easy-dataset generate-answers my-project

# Export dataset
easy-dataset export my-project --format json --output dataset.json

# Start server
easy-dataset serve --port 8000
```

#### 4. Custom Integration

```python
from flask import Flask, jsonify
from easy_dataset import EasyDataset

app = Flask(__name__)
dataset = EasyDataset()

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    project = dataset.create_project(**data)
    return jsonify(project.to_dict())

# Use with any web framework
```

### Package Installation

```bash
# From PyPI (after publishing)
pip install easy-dataset

# From source
git clone https://github.com/user/easy-dataset-python
cd easy-dataset-python
pip install -e .

# With optional dependencies
pip install easy-dataset[server]  # Include FastAPI server
pip install easy-dataset[all]     # Include all optional dependencies
```

### Package Configuration

```python
# pyproject.toml
[project]
name = "easy-dataset"
version = "2.0.0"
description = "A reusable Python package for creating LLM fine-tuning datasets"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "AGPL-3.0"}
requires-python = ">=3.9"

dependencies = [
    "sqlalchemy>=2.0",
    "pydantic>=2.0",
    "openai>=1.0",
    "httpx>=0.24",
    "pypdf2>=3.0",
    "python-docx>=0.8",
    "ebooklib>=0.18",
    "chardet>=5.0",
]

[project.optional-dependencies]
server = [
    "fastapi>=0.104",
    "uvicorn[standard]>=0.24",
    "python-multipart>=0.0.6",
]
llm = [
    "litellm>=1.0",
    "google-generativeai>=0.3",
    "ollama>=0.1",
]
all = [
    "easy-dataset[server,llm]",
]

[project.scripts]
easy-dataset = "easy_dataset.cli:main"

[project.urls]
Homepage = "https://github.com/user/easy-dataset-python"
Documentation = "https://easy-dataset.readthedocs.io"
Repository = "https://github.com/user/easy-dataset-python"
```

## Components and Interfaces

### 1. Core Package Layer (Framework-Agnostic)

**Purpose**: Provide reusable business logic that can be used in any context.

**Key Components**:
- EasyDataset main class (facade pattern)
- File processors for each format
- Text splitter with multiple strategies
- LLM client with provider abstraction
- Question and answer generators
- Dataset manager and exporter
- Task manager for async operations

**Example Interface**:
```python
# easy_dataset/__init__.py
from easy_dataset.core.dataset_manager import EasyDataset
from easy_dataset.llm import OpenAIProvider, OllamaProvider, GeminiProvider
from easy_dataset.models import Project, Chunk, Question, Dataset

__version__ = "2.0.0"
__all__ = [
    "EasyDataset",
    "OpenAIProvider",
    "OllamaProvider", 
    "GeminiProvider",
    "Project",
    "Chunk",
    "Question",
    "Dataset",
]

# easy_dataset/core/dataset_manager.py
from typing import List, Optional
from sqlalchemy.orm import Session
from easy_dataset.database import get_session
from easy_dataset.models import Project, Chunk, Question

class EasyDataset:
    """Main interface for Easy Dataset functionality"""
    
    def __init__(self, database_url: str = "sqlite:///easy_dataset.db"):
        self.database_url = database_url
        self.session = get_session(database_url)
        self.llm_client = None
    
    def configure_llm(self, config: dict):
        """Configure LLM provider"""
        from easy_dataset.llm import create_provider
        self.llm_client = create_provider(config)
    
    def create_project(self, name: str, description: str) -> Project:
        """Create a new project"""
        project = Project(name=name, description=description)
        self.session.add(project)
        self.session.commit()
        return project
    
    def process_file(self, project_id: str, file_path: str) -> List[Chunk]:
        """Process a file and create chunks"""
        from easy_dataset.core.file_processor import FileProcessor
        processor = FileProcessor()
        chunks = processor.process(project_id, file_path)
        return chunks
    
    def generate_questions(
        self, 
        project_id: str, 
        chunk_ids: List[str],
        **kwargs
    ) -> List[Question]:
        """Generate questions from chunks"""
        from easy_dataset.core.question_generator import QuestionGenerator
        generator = QuestionGenerator(self.llm_client)
        questions = generator.generate(project_id, chunk_ids, **kwargs)
        return questions
```

### 2. API Layer (FastAPI - Optional)

**Purpose**: Provide REST API for web frontends (optional component).

**Key Components**:
- Route handlers that wrap core package functionality
- Pydantic models for request/response validation
- WebSocket endpoints for streaming
- Middleware for CORS, authentication, error handling

**Example Interface**:
```python
# easy_dataset_server/api/projects.py
from fastapi import APIRouter, Depends, HTTPException
from easy_dataset import EasyDataset
from easy_dataset.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])

def get_dataset() -> EasyDataset:
    """Dependency to get EasyDataset instance"""
    return EasyDataset()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    dataset: EasyDataset = Depends(get_dataset)
):
    """Create a new project via API"""
    result = dataset.create_project(
        name=project.name,
        description=project.description
    )
    return result

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    dataset: EasyDataset = Depends(get_dataset)
):
    """Get project details via API"""
    project = dataset.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

### 3. CLI Layer (Optional)

**Purpose**: Provide command-line interface for standalone usage.

**Example Interface**:
```python
# easy_dataset/cli.py
import click
from easy_dataset import EasyDataset

@click.group()
def main():
    """Easy Dataset CLI"""
    pass

@main.command()
@click.argument('name')
@click.option('--description', default='', help='Project description')
def init(name, description):
    """Initialize a new project"""
    dataset = EasyDataset()
    project = dataset.create_project(name, description)
    click.echo(f"Created project: {project.id}")

@main.command()
@click.argument('project_id')
@click.argument('file_path')
def process(project_id, file_path):
    """Process a file"""
    dataset = EasyDataset()
    chunks = dataset.process_file(project_id, file_path)
    click.echo(f"Created {len(chunks)} chunks")

@main.command()
@click.option('--port', default=8000, help='Server port')
def serve(port):
    """Start the API server"""
    import uvicorn
    uvicorn.run("easy_dataset_server.main:app", host="0.0.0.0", port=port)

if __name__ == '__main__':
    main()
```

### 4. Core Services (Framework-Agnostic)

**Purpose**: Implement business logic that can be used by any interface layer.

**Key Services**:

#### FileProcessorService
- Extract text from PDF, DOCX, EPUB, Markdown, TXT
- Handle file uploads and storage
- Generate file metadata (size, MD5, etc.)

**Libraries**: PyPDF2/pdfplumber, python-docx, ebooklib, markdown

#### TextSplitterService
- Split text by markdown headers
- Split by custom delimiters
- Automatic chunking with overlap
- Extract table of contents

**Libraries**: langchain.text_splitter, custom implementations

#### LLMService
- Unified interface for all LLM providers
- Handle streaming and non-streaming responses
- Retry logic with exponential backoff
- Extract thinking chains and answers

#### TaskService
- Create and manage background tasks
- Update task progress
- Handle task cancellation
- Task recovery on restart

**Libraries**: Celery or asyncio with database-backed queue

#### QuestionGeneratorService
- Generate questions from text chunks
- Support custom prompts and templates
- Batch processing with concurrency control

#### AnswerGeneratorService
- Generate answers for questions
- Support chain-of-thought reasoning
- Handle vision models for image questions

#### DatasetExporterService
- Export to JSON, JSONL, CSV
- Format for Hugging Face, LLaMA Factory
- Handle large datasets with streaming

### 3. LLM Integration Layer

**Purpose**: Provide unified interface to multiple LLM providers.

**Base Interface**:
```python
# app/llm/base.py
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Optional

class BaseLLMProvider(ABC):
    def __init__(self, config: Dict):
        self.config = config
        self.endpoint = config.get("endpoint")
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict:
        """Generate a chat completion"""
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion"""
        pass
    
    async def vision_chat(
        self,
        prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg",
        **kwargs
    ) -> Dict:
        """Generate a chat completion with image input"""
        raise NotImplementedError("Vision not supported by this provider")
```

**Provider Implementations**:

#### OpenAIProvider
- Use official `openai` Python SDK
- Support GPT-3.5, GPT-4, GPT-4o, o1 models
- Handle vision models (GPT-4V)
- Implement streaming with SSE

#### OllamaProvider
- Use `ollama` Python library or HTTP client
- Connect to local Ollama instance
- List available models
- Support streaming

#### OpenRouterProvider
- Use OpenAI-compatible API
- Access 100+ models through unified interface
- Handle provider-specific parameters

#### LiteLLMProvider
- Use `litellm` library
- Support 100+ providers through proxy
- Unified interface for all models
- Automatic fallback and load balancing

#### GeminiProvider
- Use `google-generativeai` SDK
- Support Gemini Pro, Gemini Pro Vision
- Handle Google-specific authentication
- Support multimodal inputs

### 4. Data Access Layer (SQLAlchemy)

**Purpose**: Manage database operations with ORM.

**Key Models**:
- Project, UploadFile, Chunk, Tag
- Question, Dataset, DatasetConversation
- Task, ModelConfig, CustomPrompt
- Image, ImageDataset, QuestionTemplate
- GaPair, LlmProvider, LlmModel

**Example Model**:
```python
# app/models/project.py
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import nanoid

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(12), primary_key=True, default=lambda: nanoid.generate(size=12))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    global_prompt = Column(Text, default="")
    question_prompt = Column(Text, default="")
    answer_prompt = Column(Text, default="")
    default_model_config_id = Column(String, nullable=True)
    create_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chunks = relationship("Chunk", back_populates="project", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="project", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
```

### 5. Task System

**Purpose**: Handle long-running asynchronous operations.

**Implementation Options**:
1. **Celery** (recommended for production): Distributed task queue with Redis/RabbitMQ
2. **asyncio + database**: Lightweight, no external dependencies

**Task Types**:
- file-processing
- question-generation
- answer-generation
- data-cleaning
- dataset-evaluation
- multi-turn-generation
- data-distillation
- image-question-generation
- image-dataset-generation

**Task Flow**:
```python
# app/services/task_service.py
class TaskService:
    async def create_task(self, project_id: str, task_type: str, config: Dict) -> Task:
        """Create a new task"""
        task = Task(
            project_id=project_id,
            task_type=task_type,
            status=TaskStatus.PROCESSING,
            total_count=config.get("total_count", 0),
            model_info=json.dumps(config.get("model_info", {}))
        )
        self.db.add(task)
        await self.db.commit()
        
        # Start task processing
        asyncio.create_task(self.process_task(task.id))
        return task
    
    async def process_task(self, task_id: str):
        """Process task asynchronously"""
        task = await self.get_task(task_id)
        
        try:
            if task.task_type == "question-generation":
                await self.process_question_generation(task)
            elif task.task_type == "answer-generation":
                await self.process_answer_generation(task)
            # ... other task types
            
            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.utcnow()
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.note = str(e)
        
        await self.db.commit()
```

### 6. Desktop Application

**Option 1: PyQt6** (Native Python)
- Full Python stack
- Native look and feel
- Better performance
- Embedded web view for React frontend

**Option 2: Electron + Python Backend** (RECOMMENDED)
- Keep existing Electron frontend (unchanged)
- Python backend as subprocess
- Communication via HTTP/WebSocket
- Easier migration path - minimal frontend changes

**Recommended**: Electron + Python Backend to preserve existing frontend

```python
# desktop/main.py
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys
import subprocess
import threading

class EasyDatasetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy Dataset")
        self.setGeometry(100, 100, 1200, 800)
        
        # Start backend server
        self.backend_process = None
        self.start_backend()
        
        # Create web view
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:8000"))
        self.setCentralWidget(self.browser)
    
    def start_backend(self):
        """Start FastAPI backend in subprocess"""
        self.backend_process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    def closeEvent(self, event):
        """Clean shutdown"""
        if self.backend_process:
            self.backend_process.terminate()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EasyDatasetApp()
    window.show()
    sys.exit(app.exec())
```

## Data Models

### Core Entities

The data models will be converted from Prisma schema to SQLAlchemy models, maintaining the same structure and relationships:

**Project**: Container for all user work
- Fields: id, name, description, prompts, model config
- Relations: chunks, questions, datasets, tasks, images

**UploadFile**: Uploaded document metadata
- Fields: id, project_id, file_name, path, size, md5
- Relations: project, ga_pairs

**Chunk**: Segmented text from documents
- Fields: id, project_id, file_id, content, summary, size
- Relations: project, questions

**Question**: Generated questions from chunks
- Fields: id, project_id, chunk_id, question, label, answered
- Relations: project, chunk, ga_pair

**Dataset**: Question-answer pairs for training
- Fields: id, project_id, question, answer, score, tags
- Relations: project

**Task**: Background job tracking
- Fields: id, project_id, task_type, status, progress
- Relations: project

**Image**: Uploaded images for vision tasks
- Fields: id, project_id, image_name, path, width, height
- Relations: project, image_datasets

**ModelConfig**: LLM provider configuration
- Fields: id, provider_id, endpoint, api_key, model_name
- Relations: project

### Database Schema Migration

Use Alembic for database migrations:
```python
# alembic/versions/001_initial.py
def upgrade():
    op.create_table(
        'projects',
        sa.Column('id', sa.String(12), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        # ... other columns
    )
    # ... other tables
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Document Processing Properties

**Property 1: PDF text extraction consistency**
*For any* PDF file, the Python Document Processor should extract the same text content as the JavaScript version
**Validates: Requirements 2.1**

**Property 2: Markdown structure preservation**
*For any* Markdown file with headers and formatting, parsing should correctly preserve the document structure and hierarchy
**Validates: Requirements 2.2**

**Property 3: DOCX format preservation**
*For any* DOCX file, the extracted text should preserve formatting structure including paragraphs, lists, and tables
**Validates: Requirements 2.3**

**Property 4: EPUB chapter extraction**
*For any* EPUB file, all chapters and metadata should be correctly extracted and accessible
**Validates: Requirements 2.4**

**Property 5: Text encoding detection**
*For any* text file with valid encoding, the system should correctly detect and decode the content without corruption
**Validates: Requirements 2.5**

### Text Chunking Properties

**Property 6: Markdown hierarchy preservation**
*For any* Markdown document with headers, splitting by headers should create chunks that preserve the document hierarchy
**Validates: Requirements 3.1**

**Property 7: Custom delimiter splitting**
*For any* text and custom delimiter pattern, the system should split the text exactly at delimiter boundaries
**Validates: Requirements 3.2**

**Property 8: Chunk size configuration**
*For any* text and chunk configuration (size, overlap), the created chunks should respect the size limits and overlap settings
**Validates: Requirements 3.3**

**Property 9: Table of contents extraction**
*For any* structured document, the extracted table of contents should accurately reflect the document's navigation structure
**Validates: Requirements 3.4**

**Property 10: UTF-8 text handling**
*For any* UTF-8 encoded text with multilingual content, the system should process it without character corruption
**Validates: Requirements 3.5**

### LLM Integration Properties

**Property 11: Streaming and non-streaming parity**
*For any* LLM provider and prompt, both streaming and non-streaming modes should produce equivalent final output
**Validates: Requirements 4.6**

**Property 12: Retry with exponential backoff**
*For any* failed API call, the system should retry up to 3 times with exponentially increasing delays before failing
**Validates: Requirements 4.7**

### Question Generation Properties

**Property 13: Question-chunk linkage**
*For any* generated question, it should maintain a valid reference to its source chunk in the database
**Validates: Requirements 5.3**

**Property 14: Template i18n support**
*For any* prompt template and supported language, the system should use the correct language-specific template
**Validates: Requirements 5.2**

**Property 15: Batch processing concurrency**
*For any* batch of chunks and parallelism setting, the system should process exactly that many chunks concurrently
**Validates: Requirements 5.5**

### Answer Generation Properties

**Property 16: Answer context inclusion**
*For any* answer generation request, the prompt should include both the question and source chunk as context
**Validates: Requirements 6.1**

**Property 17: Answer-question linkage**
*For any* generated answer, it should be correctly linked to its corresponding question in the database
**Validates: Requirements 6.3**

**Property 18: Question-answer pair integrity**
*For any* batch answer generation, all question-answer pairs should remain correctly linked after completion
**Validates: Requirements 6.5**

### Dataset Management Properties

**Property 19: Dataset metadata completeness**
*For any* dataset, viewing it should display all required metadata fields (creation date, size, tags)
**Validates: Requirements 7.2**

**Property 20: Dataset entry deletion isolation**
*For any* dataset entry deletion, the source question and chunk should remain unaffected in the database
**Validates: Requirements 7.6**

**Property 21: Dataset filtering correctness**
*For any* dataset and filter criteria (tags, ratings, content), the filtered results should include only entries matching all criteria
**Validates: Requirements 7.5**

### Export Properties

**Property 22: JSON export schema compliance**
*For any* dataset exported to JSON, the output should conform to standard LLM training schemas
**Validates: Requirements 8.1**

**Property 23: JSONL format correctness**
*For any* dataset exported to JSONL, each line should contain exactly one valid JSON object
**Validates: Requirements 8.2**

**Property 24: CSV special character escaping**
*For any* dataset with special characters or multiline content, CSV export should properly escape all content
**Validates: Requirements 8.3**

**Property 25: Hugging Face format compatibility**
*For any* dataset exported for Hugging Face, the format should be loadable by the datasets library
**Validates: Requirements 8.4**

**Property 26: LLaMA Factory format compliance**
*For any* dataset exported for LLaMA Factory, the output should include required configuration files and correct data format
**Validates: Requirements 8.5**

### Task System Properties

**Property 27: Task creation with status**
*For any* file processing task started, a task record should be created with status set to processing
**Validates: Requirements 9.1**

**Property 28: Task progress updates**
*For any* running task, the progress percentage should be updated as work completes
**Validates: Requirements 9.2**

**Property 29: Task completion status**
*For any* task that completes successfully, the status should be updated to completed and results should be stored
**Validates: Requirements 9.3**

**Property 30: Task failure handling**
*For any* task that fails, the error details should be captured and the task should be retryable
**Validates: Requirements 9.4**

**Property 31: Task cancellation**
*For any* task that is canceled, execution should stop and status should be marked as canceled
**Validates: Requirements 9.6**

### Frontend Properties

**Property 32: Loading indicator display**
*For any* action that takes time to complete, a loading indicator should be displayed to the user
**Validates: Requirements 10.3**

**Property 33: Error message display**
*For any* error that occurs, a user-friendly error message should be displayed
**Validates: Requirements 10.4**

### Internationalization Properties

**Property 34: Language selection application**
*For any* language selection, all UI text should be displayed in the chosen language
**Validates: Requirements 11.1**

**Property 35: Language-specific prompts**
*For any* content generation, the system should use prompts appropriate for the selected language
**Validates: Requirements 11.2**

**Property 36: New language support**
*For any* new language added via i18n files, the system should load and apply the translations
**Validates: Requirements 11.4**

### Database Properties

**Property 37: Project unique identifiers**
*For any* project created, it should have a unique identifier in the database
**Validates: Requirements 12.1**

**Property 38: Query filtering and sorting**
*For any* database query with filters and sort criteria, the results should match the criteria and be correctly ordered
**Validates: Requirements 12.4**

**Property 39: Database export completeness**
*For any* database backup operation, the exported file should contain all data from all tables
**Validates: Requirements 12.5**

### Desktop Application Properties

**Property 40: Desktop shutdown cleanup**
*For any* desktop application window close, the backend service should shut down gracefully without orphaned processes
**Validates: Requirements 13.3**

**Property 41: Update check functionality**
*For any* update check, the system should query for available updates and prompt the user if updates exist
**Validates: Requirements 13.5**

### Image Dataset Properties

**Property 42: Image format support**
*For any* image upload in JPEG, PNG, or WebP format, the system should successfully process and store the image
**Validates: Requirements 14.1**

**Property 43: Vision model usage**
*For any* image question generation, the system should use a vision-capable model from the configured provider
**Validates: Requirements 14.2**

**Property 44: Image dataset storage**
*For any* image dataset created, both image references and QA pairs should be correctly stored and linked
**Validates: Requirements 14.3**

**Property 45: Image export format**
*For any* image dataset export, the output should include either image paths or base64 encoded image data
**Validates: Requirements 14.4**

**Property 46: PDF image extraction**
*For any* PDF containing images, the images should be extracted and associated with their corresponding text chunks
**Validates: Requirements 14.5**

### Conversation Dataset Properties

**Property 47: Multi-turn conversation support**
*For any* conversation created, it should support multiple message turns with distinct roles
**Validates: Requirements 15.1**

**Property 48: Conversation context preservation**
*For any* conversation generation, context from previous turns should be maintained in subsequent turns
**Validates: Requirements 15.2**

**Property 49: Conversation message editing**
*For any* conversation, individual messages should be editable without affecting other messages
**Validates: Requirements 15.3**

**Property 50: Conversation export format**
*For any* conversation exported, the format should be compatible with chat model training (e.g., ShareGPT format)
**Validates: Requirements 15.4**

## Error Handling

### Error Categories

**1. File Processing Errors**
- Invalid file format
- Corrupted file data
- File size exceeds limit
- Encoding detection failure
- Extraction library errors

**Strategy**: Catch exceptions at file processor level, log detailed error, return user-friendly message, mark task as failed

**2. LLM API Errors**
- Network timeout
- Authentication failure
- Rate limiting
- Invalid model name
- Malformed response

**Strategy**: Implement retry with exponential backoff, fallback to alternative models if configured, log API errors, notify user

**3. Database Errors**
- Connection failure
- Constraint violation
- Transaction deadlock
- Disk space exhaustion

**Strategy**: Use database transactions, implement rollback on failure, retry transient errors, alert on persistent failures

**4. Task Processing Errors**
- Task timeout
- Resource exhaustion
- Concurrent modification
- Invalid task state

**Strategy**: Implement task timeout limits, graceful degradation, task recovery on restart, detailed error logging

**5. Validation Errors**
- Invalid input data
- Missing required fields
- Type mismatch
- Business rule violation

**Strategy**: Use Pydantic for request validation, return 422 with detailed error messages, validate at API boundary

### Error Response Format

```python
# app/schemas/error.py
from pydantic import BaseModel
from typing import Optional, List

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[List[ErrorDetail]] = None
    request_id: str
```

### Global Exception Handler

```python
# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import uuid

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    logger.error(f"Request {request_id} failed: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": [{"message": str(exc), "code": "INTERNAL_ERROR"}],
            "request_id": request_id
        }
    )
```

## Testing Strategy

### Unit Testing

**Framework**: pytest

**Coverage Areas**:
- Individual service methods
- LLM provider implementations
- File processors for each format
- Text splitters
- Data model operations
- Utility functions

**Example**:
```python
# tests/test_services/test_text_splitter.py
import pytest
from app.services.text_splitter import TextSplitterService

def test_split_by_markdown_headers():
    """Test splitting markdown by headers preserves hierarchy"""
    markdown = "# Header 1\nContent 1\n## Header 2\nContent 2"
    splitter = TextSplitterService()
    chunks = splitter.split_by_markdown_headers(markdown)
    
    assert len(chunks) == 2
    assert chunks[0]["level"] == 1
    assert chunks[1]["level"] == 2
    assert "Content 1" in chunks[0]["content"]

def test_split_by_custom_delimiter():
    """Test splitting by custom delimiter"""
    text = "Part 1|||Part 2|||Part 3"
    splitter = TextSplitterService()
    chunks = splitter.split_by_delimiter(text, "|||")
    
    assert len(chunks) == 3
    assert chunks[0].strip() == "Part 1"
```

### Integration Testing

**Framework**: pytest with test database

**Coverage Areas**:
- API endpoints with database
- Task processing workflows
- LLM provider integrations (with mocking)
- File upload and processing
- Export functionality

**Example**:
```python
# tests/test_api/test_projects.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_project():
    """Test project creation via API"""
    response = client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test Description"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data

def test_get_project():
    """Test retrieving project"""
    # Create project first
    create_response = client.post(
        "/api/projects",
        json={"name": "Test", "description": "Test"}
    )
    project_id = create_response.json()["id"]
    
    # Get project
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id
```

### Property-Based Testing

**Framework**: Hypothesis

**Coverage Areas**:
- Text processing with various inputs
- Chunk size and overlap calculations
- Export format validation
- Database query correctness

**Example**:
```python
# tests/test_properties/test_text_splitter.py
from hypothesis import given, strategies as st
from app.services.text_splitter import TextSplitterService

@given(
    text=st.text(min_size=100, max_size=10000),
    chunk_size=st.integers(min_value=50, max_value=500),
    overlap=st.integers(min_value=0, max_value=50)
)
def test_chunk_size_property(text, chunk_size, overlap):
    """
    Feature: js-to-python-conversion, Property 8: Chunk size configuration
    For any text and chunk configuration, chunks should respect size limits
    """
    splitter = TextSplitterService()
    chunks = splitter.split_with_overlap(text, chunk_size, overlap)
    
    for chunk in chunks:
        assert len(chunk) <= chunk_size + overlap

@given(
    text=st.text(min_size=10),
    delimiter=st.text(min_size=1, max_size=5)
)
def test_delimiter_splitting_property(text, delimiter):
    """
    Feature: js-to-python-conversion, Property 7: Custom delimiter splitting
    For any text and delimiter, splitting should occur at exact boundaries
    """
    # Insert delimiter at known positions
    parts = [text[:len(text)//2], text[len(text)//2:]]
    combined = delimiter.join(parts)
    
    splitter = TextSplitterService()
    chunks = splitter.split_by_delimiter(combined, delimiter)
    
    assert len(chunks) == 2
```

### End-to-End Testing

**Framework**: pytest with Playwright (for web UI)

**Coverage Areas**:
- Complete user workflows
- Desktop application functionality
- Multi-step processes (upload → process → generate → export)

**Example**:
```python
# tests/test_e2e/test_workflow.py
import pytest
from playwright.sync_api import Page

def test_complete_dataset_workflow(page: Page):
    """Test complete workflow from file upload to export"""
    # Login/start app
    page.goto("http://localhost:8000")
    
    # Create project
    page.click("text=New Project")
    page.fill("input[name=name]", "E2E Test Project")
    page.click("button:has-text('Create')")
    
    # Upload file
    page.set_input_files("input[type=file]", "test_data/sample.pdf")
    page.click("button:has-text('Upload')")
    
    # Wait for processing
    page.wait_for_selector("text=Processing complete")
    
    # Generate questions
    page.click("text=Generate Questions")
    page.wait_for_selector("text=Questions generated")
    
    # Generate answers
    page.click("text=Generate Answers")
    page.wait_for_selector("text=Answers generated")
    
    # Export dataset
    page.click("text=Export")
    page.click("text=JSON")
    
    # Verify download
    with page.expect_download() as download_info:
        page.click("button:has-text('Download')")
    download = download_info.value
    assert download.suggested_filename.endswith(".json")
```

### Performance Testing

**Framework**: locust

**Coverage Areas**:
- API endpoint throughput
- Concurrent task processing
- Large file handling
- Database query performance

**Example**:
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class EasyDatasetUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def list_projects(self):
        self.client.get("/api/projects")
    
    @task(1)
    def create_project(self):
        self.client.post("/api/projects", json={
            "name": "Load Test Project",
            "description": "Testing"
        })
    
    @task(2)
    def get_chunks(self):
        self.client.get("/api/chunks?project_id=test123")
```

## Technology Stack

### Backend

- **Web Framework**: FastAPI 0.104+
  - High performance async framework
  - Automatic API documentation (OpenAPI/Swagger)
  - Built-in request validation with Pydantic
  - WebSocket support for streaming

- **ORM**: SQLAlchemy 2.0+
  - Mature and feature-rich ORM
  - Async support
  - Type hints support
  - Migration support via Alembic

- **Database**: SQLite 3
  - Same as JavaScript version
  - File-based, no server required
  - Good performance for single-user applications

- **Task Queue**: 
  - Option 1: Celery + Redis (production)
  - Option 2: asyncio + database (lightweight)

- **Validation**: Pydantic 2.0+
  - Data validation and serialization
  - Type safety
  - JSON schema generation

### LLM Integration

- **OpenAI**: `openai` 1.0+
- **Ollama**: `ollama` or `httpx`
- **OpenRouter**: OpenAI-compatible client
- **LiteLLM**: `litellm` 1.0+
- **Gemini**: `google-generativeai` 0.3+
- **LangChain**: `langchain` 0.1+ (optional, for advanced features)

### File Processing

- **PDF**: `pypdf2`, `pdfplumber`, or `pymupdf`
- **DOCX**: `python-docx`
- **EPUB**: `ebooklib`
- **Markdown**: `markdown`, `mistune`
- **Text**: Built-in with `chardet` for encoding detection

### Desktop Application

- **Option 1**: PyQt6 or PySide6
  - Native Python GUI
  - Cross-platform
  - Embedded web view (QtWebEngine)

- **Option 2**: Electron + Python
  - Keep existing Electron frontend
  - Python backend as subprocess
  - Communication via HTTP/WebSocket

### Development Tools

- **Testing**: pytest, hypothesis, playwright
- **Linting**: ruff, mypy
- **Formatting**: black, isort
- **Documentation**: mkdocs, sphinx
- **Packaging**: poetry or pip-tools

### Deployment

- **Docker**: Multi-stage builds
- **Desktop**: PyInstaller or cx_Freeze
- **Web**: Uvicorn + Gunicorn

## Migration Strategy

### Phase 1: Backend Core (Weeks 1-2)
1. Set up project structure
2. Implement database models with SQLAlchemy
3. Create FastAPI application skeleton
4. Implement basic CRUD operations
5. Set up testing framework

### Phase 2: File Processing (Weeks 3-4)
1. Implement file upload handling
2. Create document processors for each format
3. Implement text splitting service
4. Add file processing tasks
5. Test with sample documents

### Phase 3: LLM Integration (Weeks 5-6)
1. Implement base LLM client
2. Create provider implementations (OpenAI, Ollama, etc.)
3. Add streaming support
4. Implement retry logic
5. Test with each provider

### Phase 4: Question & Answer Generation (Weeks 7-8)
1. Implement question generation service
2. Implement answer generation service
3. Add prompt template system
4. Implement batch processing
5. Add task tracking

### Phase 5: Dataset Management (Weeks 9-10)
1. Implement dataset CRUD operations
2. Add filtering and search
3. Implement export functionality
4. Support multiple export formats
5. Add image dataset support

### Phase 6: Frontend Integration (Weeks 11-12)
1. Ensure API endpoints match existing frontend expectations
2. Implement WebSocket for streaming (compatible with existing frontend)
3. Add CORS configuration
4. Test frontend integration with Python backend
5. Fix any API compatibility issues (frontend code remains unchanged)

### Phase 7: Desktop Application (Weeks 13-14)
1. Keep existing Electron frontend (no changes needed)
2. Update Electron to launch Python backend instead of Node.js backend
3. Integrate Python backend service as subprocess
4. Ensure auto-update functionality works with new backend
5. Test on all platforms (Windows, macOS, Linux)

### Phase 8: Testing & Polish (Weeks 15-16)
1. Complete unit test coverage
2. Add integration tests
3. Perform end-to-end testing
4. Fix bugs and issues
5. Performance optimization
6. Documentation

### Phase 9: Deployment (Week 17)
1. Create Docker images
2. Build desktop installers
3. Set up CI/CD
4. Create deployment documentation
5. Release beta version

## Dependencies Mapping

| JavaScript Library | Python Equivalent | Purpose |
|-------------------|-------------------|---------|
| Next.js | FastAPI | Web framework (backend only) |
| Prisma | SQLAlchemy | ORM |
| React | React (unchanged) | Frontend UI - NO CHANGES |
| Material-UI | Material-UI (unchanged) | UI components - NO CHANGES |
| Electron | Electron (unchanged) | Desktop app - frontend unchanged, backend converted |
| @opendocsg/pdf2md | pypdf2/pdfplumber | PDF processing |
| mammoth | python-docx | DOCX processing |
| turndown | markdown | Markdown processing |
| openai SDK | openai | OpenAI integration |
| ollama-ai-provider | ollama/httpx | Ollama integration |
| langchain | langchain | LLM utilities |
| i18next | babel/gettext | Internationalization |
| formidable | python-multipart | File uploads |
| nanoid | nanoid | ID generation |
| zod | pydantic | Validation |
| axios | httpx | HTTP client |

## Performance Considerations

### 1. Async/Await
- Use FastAPI's async capabilities for I/O operations
- Async database queries with SQLAlchemy
- Async LLM API calls
- Concurrent task processing

### 2. Caching
- Cache LLM responses for identical prompts
- Cache file processing results
- Use Redis for distributed caching (optional)

### 3. Database Optimization
- Add indexes on frequently queried fields
- Use connection pooling
- Implement pagination for large result sets
- Use database transactions efficiently

### 4. File Processing
- Stream large files instead of loading into memory
- Process files in chunks
- Use multiprocessing for CPU-intensive operations
- Implement progress tracking

### 5. LLM API Optimization
- Batch requests when possible
- Implement request queuing
- Use streaming for long responses
- Cache model lists and configurations

## Security Considerations

### 1. API Security
- Input validation with Pydantic
- SQL injection prevention via ORM
- Rate limiting on endpoints
- CORS configuration

### 2. File Upload Security
- File type validation
- File size limits
- Virus scanning (optional)
- Secure file storage

### 3. API Key Management
- Encrypt API keys in database
- Environment variable support
- Secure key storage in desktop app

### 4. Data Privacy
- Local-first architecture
- No data sent to external services (except LLM APIs)
- User control over data export

## Internationalization

### Implementation
- Use `babel` for message extraction
- Store translations in JSON/PO files
- Support language detection
- Provide language switcher in UI

### Supported Languages
- English (en)
- Simplified Chinese (zh-CN)
- Turkish (tr)

### Translation Files Structure
```
locales/
├── en/
│   └── messages.json
├── zh-CN/
│   └── messages.json
└── tr/
    └── messages.json
```

## Monitoring and Logging

### Logging Strategy
- Use Python's `logging` module
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Separate logs for different components

### Metrics
- API request/response times
- Task processing duration
- LLM API call latency
- Database query performance
- Error rates

### Health Checks
- Database connectivity
- LLM provider availability
- Disk space
- Memory usage

## Documentation

### API Documentation
- Auto-generated with FastAPI (OpenAPI/Swagger)
- Interactive API explorer
- Request/response examples

### User Documentation
- Installation guide
- User manual
- Configuration guide
- Troubleshooting

### Developer Documentation
- Architecture overview
- API reference
- Contributing guide
- Development setup

## Conclusion

This design provides a comprehensive blueprint for converting the Easy Dataset application from JavaScript to Python. The Python version will maintain all existing functionality while leveraging Python's strengths in AI/ML, data processing, and scientific computing. The modular architecture ensures maintainability and extensibility, while the testing strategy ensures correctness and reliability.
