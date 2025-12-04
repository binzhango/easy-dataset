# Implementation Plan

- [x] 1. Set up Python package structure and core infrastructure
  - Create package directory structure in python-backend/: easy_dataset/, easy_dataset_server/, tests/, examples/
  - Set up python-backend/pyproject.toml as installable package with optional dependencies
  - Configure python-backend/setup.py for package distribution
  - Create python-backend/MANIFEST.in for package files
  - Configure development tools (pytest, ruff, black, mypy) in python-backend/
  - Create python-backend/requirements.txt, python-backend/requirements-dev.txt
  - Set up package __init__.py files with public API exports in python-backend/
  - Initialize python-backend/.gitignore for Python
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Implement core EasyDataset class (main package interface)
- [x] 2.1 Create EasyDataset facade class in python-backend/easy_dataset/core/
  - Implement main EasyDataset class as entry point in python-backend/easy_dataset/core/easy_dataset.py
  - Add methods for project management (create, get, update, delete)
  - Add methods for file processing
  - Add methods for question/answer generation
  - Add methods for dataset export
  - Implement LLM configuration
  - Make class usable without web framework
  - _Requirements: 1.3, 12.1_

- [x] 3. Implement database models and ORM layer
- [x] 3.1 Create SQLAlchemy base configuration and database connection
  - Implement python-backend/easy_dataset/database/connection.py with SQLAlchemy engine and session management
  - Create Base model class in python-backend/easy_dataset/database/base.py for all models to inherit from
  - Set up Alembic for database migrations in python-backend/alembic/
  - Configure SQLite database connection with proper settings
  - Integrate database initialization into EasyDataset._init_database() method
  - _Requirements: 12.1, 12.3_

- [x] 3.2 Implement core data models (Projects, UploadFiles, Chunks, Tags)
  - Create Projects model in python-backend/easy_dataset/models/project.py matching Prisma schema exactly
  - Create UploadFiles model in python-backend/easy_dataset/models/file.py with file metadata
  - Create Chunks model in python-backend/easy_dataset/models/chunk.py with text content and relationships
  - Create Tags model in python-backend/easy_dataset/models/tag.py for hierarchical tagging (self-referential)
  - Define all relationships between models (one-to-many, many-to-one)
  - Add nanoid ID generation for primary keys (use nanoid library)
  - Ensure field names match Prisma schema (camelCase in DB, snake_case in Python)
  - _Requirements: 12.1, 2.1_

- [x] 3.3 Implement question and dataset models (Questions, Datasets, DatasetConversations)
  - Create Questions model in python-backend/easy_dataset/models/question.py with chunk and gaPair relationships
  - Create Datasets model in python-backend/easy_dataset/models/dataset.py for QA pairs with all metadata fields
  - Create DatasetConversations model in python-backend/easy_dataset/models/conversation.py for multi-turn dialogues
  - Include all fields from Prisma schema (score, aiEvaluation, tags, note, confirmed, etc.)
  - Support ShareGPT format storage in rawMessages field
  - _Requirements: 12.1, 15.1_

- [x] 3.4 Implement task and configuration models (Task, ModelConfig, CustomPrompts, LlmProviders, LlmModels)
  - Create Task model in python-backend/easy_dataset/models/task.py for background job tracking with status enum
  - Create ModelConfig model in python-backend/easy_dataset/models/config.py for LLM provider settings
  - Create CustomPrompts model in python-backend/easy_dataset/models/prompt.py for user-defined prompts
  - Create LlmProviders and LlmModels models in python-backend/easy_dataset/models/llm.py
  - Include all prompt types (globalPrompt, questionPrompt, answerPrompt, labelPrompt, domainTreePrompt, cleanPrompt)
  - _Requirements: 9.1, 4.1_

- [x] 3.5 Implement image and template models (Images, ImageDatasets, QuestionTemplates, GaPairs)
  - Create Images model in python-backend/easy_dataset/models/image.py for uploaded images with dimensions
  - Create ImageDatasets model in python-backend/easy_dataset/models/image_dataset.py for image QA pairs
  - Create QuestionTemplates model in python-backend/easy_dataset/models/template.py for reusable templates
  - Create GaPairs model in python-backend/easy_dataset/models/ga_pair.py for genre-audience pairs
  - Support multiple answer types (text, label, custom_format)
  - _Requirements: 14.1, 14.3_

- [ ]* 3.6 Write property tests for database models
  - **Property 37: Project unique identifiers**
  - **Validates: Requirements 12.1**

- [ ] 4. Create Pydantic schemas for API validation
- [x] 4.1 Create schemas for projects and files
  - Implement ProjectCreate, ProjectUpdate, ProjectResponse schemas in python-backend/easy_dataset/schemas/project.py
  - Implement UploadFileCreate, UploadFileResponse schemas in python-backend/easy_dataset/schemas/file.py
  - Add validation rules for required fields
  - _Requirements: 12.1_

- [x] 4.2 Create schemas for chunks and questions
  - Implement ChunkCreate, ChunkResponse schemas in python-backend/easy_dataset/schemas/chunk.py
  - Implement QuestionCreate, QuestionResponse schemas in python-backend/easy_dataset/schemas/question.py
  - Implement DatasetCreate, DatasetResponse schemas in python-backend/easy_dataset/schemas/dataset.py
  - _Requirements: 5.3, 6.3_

- [x] 4.3 Create schemas for tasks and configurations
  - Implement TaskCreate, TaskResponse, TaskUpdate schemas in python-backend/easy_dataset/schemas/task.py
  - Implement ModelConfigCreate, ModelConfigResponse schemas in python-backend/easy_dataset/schemas/config.py
  - Add status enums and validation
  - _Requirements: 9.1, 4.1_

- [-] 5. Implement FastAPI application and routing
- [x] 5.1 Create FastAPI application with middleware
  - Initialize FastAPI app in python-backend/easy_dataset_server/app.py with CORS middleware
  - Add error handling middleware
  - Configure request logging
  - Set up dependency injection for database sessions
  - _Requirements: 10.3, 10.4_

- [x] 5.2 Implement project API endpoints
  - Create python-backend/easy_dataset_server/api/projects.py
  - POST /api/projects - create project
  - GET /api/projects - list projects
  - GET /api/projects/{id} - get project details
  - PUT /api/projects/{id} - update project
  - DELETE /api/projects/{id} - delete project
  - _Requirements: 12.1_

- [ ]* 5.3 Write property tests for project endpoints
  - Create tests in python-backend/tests/test_projects.py
  - **Property 37: Project unique identifiers**
  - **Validates: Requirements 12.1**

- [x] 5.4 Implement file upload API endpoints
  - Create python-backend/easy_dataset_server/api/files.py
  - POST /api/files/upload - handle file uploads
  - GET /api/files - list uploaded files
  - DELETE /api/files/{id} - delete file
  - Implement multipart form data handling
  - _Requirements: 2.1, 2.6_

- [x] 5.5 Implement chunk API endpoints
  - Create python-backend/easy_dataset_server/api/chunks.py
  - GET /api/chunks - list chunks with filtering
  - GET /api/chunks/{id} - get chunk details
  - PUT /api/chunks/{id} - update chunk
  - DELETE /api/chunks/{id} - delete chunk
  - _Requirements: 3.1_

- [x] 5.6 Implement question API endpoints
  - Create python-backend/easy_dataset_server/api/questions.py
  - POST /api/questions - create question
  - GET /api/questions - list questions with filtering
  - PUT /api/questions/{id} - update question
  - DELETE /api/questions/{id} - delete question
  - _Requirements: 5.3_

- [ ]* 5.7 Write property tests for question endpoints
  - Create tests in python-backend/tests/test_questions.py
  - **Property 13: Question-chunk linkage**
  - **Validates: Requirements 5.3**

- [x] 5.8 Implement dataset API endpoints
  - Create python-backend/easy_dataset_server/api/datasets.py
  - POST /api/datasets - create dataset entry
  - GET /api/datasets - list datasets with filtering
  - PUT /api/datasets/{id} - update dataset entry
  - DELETE /api/datasets/{id} - delete dataset entry
  - _Requirements: 7.1, 7.3, 7.6_

- [ ]* 5.9 Write property tests for dataset endpoints
  - Create tests in python-backend/tests/test_datasets.py
  - **Property 20: Dataset entry deletion isolation**
  - **Validates: Requirements 7.6**
  - **Property 21: Dataset filtering correctness**
  - **Validates: Requirements 7.5**

- [x] 6. Implement file processing services
- [x] 6.1 Create base file processor interface
  - Define abstract FileProcessor base class in python-backend/easy_dataset/core/file_processor.py
  - Implement file type detection
  - Add file validation (size, format)
  - Create file storage utilities
  - _Requirements: 2.1_

- [x] 6.2 Implement PDF processor
  - Create python-backend/easy_dataset/core/processors/pdf_processor.py
  - Use pypdf2 or pdfplumber for text extraction
  - Extract text content from all pages
  - Handle PDF metadata extraction
  - Support image extraction from PDFs
  - _Requirements: 2.1, 14.5_

- [ ]* 6.3 Write property tests for PDF processor
  - Create tests in python-backend/tests/test_pdf_processor.py
  - **Property 1: PDF text extraction consistency**
  - **Validates: Requirements 2.1**
  - **Property 46: PDF image extraction**
  - **Validates: Requirements 14.5**

- [x] 6.4 Implement Markdown processor
  - Create python-backend/easy_dataset/core/processors/markdown_processor.py
  - Parse markdown with structure preservation
  - Extract headers and hierarchy
  - Handle code blocks and formatting
  - _Requirements: 2.2_

- [ ]* 6.5 Write property tests for Markdown processor
  - Create tests in python-backend/tests/test_markdown_processor.py
  - **Property 2: Markdown structure preservation**
  - **Validates: Requirements 2.2**

- [x] 6.6 Implement DOCX processor
  - Create python-backend/easy_dataset/core/processors/docx_processor.py
  - Use python-docx for document parsing
  - Extract text with formatting
  - Preserve paragraph structure
  - Handle tables and lists
  - _Requirements: 2.3_

- [ ]* 6.7 Write property tests for DOCX processor
  - Create tests in python-backend/tests/test_docx_processor.py
  - **Property 3: DOCX format preservation**
  - **Validates: Requirements 2.3**

- [x] 6.8 Implement EPUB processor
  - Create python-backend/easy_dataset/core/processors/epub_processor.py
  - Use ebooklib for EPUB parsing
  - Extract chapter content
  - Extract metadata (title, author, etc.)
  - Handle navigation structure
  - _Requirements: 2.4_

- [ ]* 6.9 Write property tests for EPUB processor
  - Create tests in python-backend/tests/test_epub_processor.py
  - **Property 4: EPUB chapter extraction**
  - **Validates: Requirements 2.4**

- [x] 6.10 Implement TXT processor
  - Create python-backend/easy_dataset/core/processors/txt_processor.py
  - Detect text encoding with chardet
  - Handle various encodings (UTF-8, Latin-1, etc.)
  - Preserve line breaks and formatting
  - _Requirements: 2.5_

- [ ]* 6.11 Write property tests for TXT processor
  - Create tests in python-backend/tests/test_txt_processor.py
  - **Property 5: Text encoding detection**
  - **Validates: Requirements 2.5**

- [x] 7. Implement text splitting service
- [x] 7.1 Create text splitter with multiple strategies
  - Create python-backend/easy_dataset/core/text_splitter.py
  - Implement split by markdown headers
  - Implement split by custom delimiters
  - Implement automatic chunking with overlap
  - Extract table of contents from documents
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 7.2 Write property tests for text splitter
  - Create tests in python-backend/tests/test_text_splitter.py
  - **Property 6: Markdown hierarchy preservation**
  - **Validates: Requirements 3.1**
  - **Property 7: Custom delimiter splitting**
  - **Validates: Requirements 3.2**
  - **Property 8: Chunk size configuration**
  - **Validates: Requirements 3.3**
  - **Property 9: Table of contents extraction**
  - **Validates: Requirements 3.4**

- [x] 7.3 Add UTF-8 and multilingual text handling
  - Ensure proper UTF-8 encoding throughout
  - Handle special characters and emojis
  - Support right-to-left languages
  - _Requirements: 3.5_

- [ ]* 7.4 Write property tests for UTF-8 handling
  - Create tests in python-backend/tests/test_utf8_handling.py
  - **Property 10: UTF-8 text handling**
  - **Validates: Requirements 3.5**

- [x] 8. Implement LLM integration layer
- [x] 8.1 Create base LLM provider interface
  - Define BaseLLMProvider abstract class in python-backend/easy_dataset/llm/base.py
  - Implement chat() method interface
  - Implement chat_stream() method interface
  - Implement vision_chat() method interface
  - Add retry logic with exponential backoff
  - _Requirements: 4.6, 4.7_

- [ ]* 8.2 Write property tests for LLM base functionality
  - Create tests in python-backend/tests/test_llm_base.py
  - **Property 11: Streaming and non-streaming parity**
  - **Validates: Requirements 4.6**
  - **Property 12: Retry with exponential backoff**
  - **Validates: Requirements 4.7**

- [x] 8.3 Implement OpenAI provider
  - Create python-backend/easy_dataset/llm/providers/openai_provider.py
  - Use official openai Python SDK
  - Support GPT-3.5, GPT-4, GPT-4o models
  - Implement streaming with async iteration
  - Support vision models (GPT-4V)
  - _Requirements: 4.1_

- [x] 8.4 Implement Ollama provider
  - Create python-backend/easy_dataset/llm/providers/ollama_provider.py
  - Use ollama Python library or httpx
  - Connect to local Ollama instance
  - List available models
  - Support streaming responses
  - _Requirements: 4.2_

- [x] 8.5 Implement OpenRouter provider
  - Create python-backend/easy_dataset/llm/providers/openrouter_provider.py
  - Use OpenAI-compatible API client
  - Configure OpenRouter endpoint
  - Support multiple models through unified interface
  - _Requirements: 4.3_

- [x] 8.6 Implement LiteLLM provider
  - Create python-backend/easy_dataset/llm/providers/litellm_provider.py
  - Use litellm Python library
  - Support 100+ models through proxy
  - Implement unified interface
  - Add fallback and load balancing
  - _Requirements: 4.4_

- [x] 8.7 Implement Gemini provider
  - Create python-backend/easy_dataset/llm/providers/gemini_provider.py
  - Use google-generativeai SDK
  - Support Gemini Pro and Gemini Pro Vision
  - Handle Google-specific authentication
  - Support multimodal inputs
  - _Requirements: 4.5_

- [x] 8.8 Create LLM service orchestrator
  - Implement LLMService class in python-backend/easy_dataset/llm/service.py to manage providers
  - Load provider configuration from database
  - Handle provider selection based on model config
  - Extract thinking chains and answers from responses
  - _Requirements: 4.1, 6.4_

- [x] 9. Implement prompt management system
- [x] 9.1 Create prompt templates for questions
  - Create python-backend/easy_dataset/llm/prompts/question_prompts.py
  - Define question generation prompts
  - Support multiple languages (en, zh-CN, tr)
  - Allow custom prompt templates
  - Implement template variable substitution
  - _Requirements: 5.2, 11.2_

- [ ]* 9.2 Write property tests for prompt templates
  - Create tests in python-backend/tests/test_prompts.py
  - **Property 14: Template i18n support**
  - **Validates: Requirements 5.2**
  - **Property 35: Language-specific prompts**
  - **Validates: Requirements 11.2**

- [x] 9.3 Create prompt templates for answers
  - Create python-backend/easy_dataset/llm/prompts/answer_prompts.py
  - Define answer generation prompts
  - Support chain-of-thought prompts
  - Support detailed explanation modes
  - Implement context injection (question + chunk)
  - _Requirements: 6.1, 6.2, 6.4_

- [ ]* 9.4 Write property tests for answer prompts
  - Create tests in python-backend/tests/test_answer_prompts.py
  - **Property 16: Answer context inclusion**
  - **Validates: Requirements 6.1**

- [x] 9.5 Create prompt templates for evaluation and cleaning
  - Create python-backend/easy_dataset/llm/prompts/eval_prompts.py
  - Define dataset evaluation prompts
  - Define data cleaning prompts
  - Support custom evaluation criteria
  - _Requirements: 6.2_

- [ ] 10. Implement task system for background jobs
- [ ] 10.1 Create task service with database-backed queue
  - Implement TaskService class in python-backend/easy_dataset/core/task_service.py
  - Create task with status tracking
  - Update task progress in real-time
  - Handle task completion and failure
  - Support task cancellation
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.6_

- [ ]* 10.2 Write property tests for task system
  - Create tests in python-backend/tests/test_task_service.py
  - **Property 27: Task creation with status**
  - **Validates: Requirements 9.1**
  - **Property 28: Task progress updates**
  - **Validates: Requirements 9.2**
  - **Property 29: Task completion status**
  - **Validates: Requirements 9.3**
  - **Property 30: Task failure handling**
  - **Validates: Requirements 9.4**
  - **Property 31: Task cancellation**
  - **Validates: Requirements 9.6**

- [ ] 10.3 Implement file processing task handler
  - Create python-backend/easy_dataset/core/tasks/file_processing.py
  - Process uploaded files asynchronously
  - Extract text using appropriate processor
  - Create chunks from extracted text
  - Update task progress during processing
  - _Requirements: 2.1, 9.2_

- [ ] 10.4 Implement question generation task handler
  - Create python-backend/easy_dataset/core/tasks/question_generation.py
  - Process chunks in batches
  - Call LLM provider for question generation
  - Store generated questions with chunk references
  - Support configurable parallelism
  - _Requirements: 5.1, 5.5_

- [ ]* 10.5 Write property tests for question generation
  - Create tests in python-backend/tests/test_question_generation.py
  - **Property 13: Question-chunk linkage**
  - **Validates: Requirements 5.3**
  - **Property 15: Batch processing concurrency**
  - **Validates: Requirements 5.5**

- [ ] 10.6 Implement answer generation task handler
  - Create python-backend/easy_dataset/core/tasks/answer_generation.py
  - Process questions in batches
  - Include question and chunk context in prompts
  - Store generated answers linked to questions
  - Maintain question-answer pair integrity
  - _Requirements: 6.1, 6.3, 6.5_

- [ ]* 10.7 Write property tests for answer generation
  - Create tests in python-backend/tests/test_answer_generation.py
  - **Property 17: Answer-question linkage**
  - **Validates: Requirements 6.3**
  - **Property 18: Question-answer pair integrity**
  - **Validates: Requirements 6.5**

- [ ] 10.8 Implement data cleaning task handler
  - Create python-backend/easy_dataset/core/tasks/data_cleaning.py
  - Clean and normalize dataset entries
  - Remove duplicates
  - Fix formatting issues
  - _Requirements: 7.3_

- [ ] 10.9 Implement dataset evaluation task handler
  - Create python-backend/easy_dataset/core/tasks/dataset_evaluation.py
  - Evaluate dataset quality using LLM
  - Generate AI evaluation scores
  - Store evaluation results
  - _Requirements: 7.4_

- [ ] 10.10 Implement multi-turn conversation generation task handler
  - Create python-backend/easy_dataset/core/tasks/conversation_generation.py
  - Generate multi-turn dialogues
  - Maintain context across turns
  - Support configurable turn count
  - Store in ShareGPT format
  - _Requirements: 15.1, 15.2_

- [ ]* 10.11 Write property tests for conversation generation
  - Create tests in python-backend/tests/test_conversation_generation.py
  - **Property 47: Multi-turn conversation support**
  - **Validates: Requirements 15.1**
  - **Property 48: Conversation context preservation**
  - **Validates: Requirements 15.2**

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement dataset export functionality
- [ ] 11.1 Create dataset exporter service
  - Implement DatasetExporterService class in python-backend/easy_dataset/core/exporter.py
  - Support multiple export formats
  - Handle large datasets with streaming
  - Show export progress
  - _Requirements: 8.1, 8.6_

- [ ] 11.2 Implement JSON export
  - Create python-backend/easy_dataset/core/exporters/json_exporter.py
  - Format data according to LLM training schemas
  - Support standard formats (Alpaca, ShareGPT, etc.)
  - Validate JSON structure
  - _Requirements: 8.1_

- [ ]* 11.3 Write property tests for JSON export
  - Create tests in python-backend/tests/test_json_export.py
  - **Property 22: JSON export schema compliance**
  - **Validates: Requirements 8.1**

- [ ] 11.4 Implement JSONL export
  - Create python-backend/easy_dataset/core/exporters/jsonl_exporter.py
  - Create one JSON object per line
  - Support streaming for large datasets
  - Validate JSONL format
  - _Requirements: 8.2_

- [ ]* 11.5 Write property tests for JSONL export
  - Create tests in python-backend/tests/test_jsonl_export.py
  - **Property 23: JSONL format correctness**
  - **Validates: Requirements 8.2**

- [ ] 11.6 Implement CSV export
  - Create python-backend/easy_dataset/core/exporters/csv_exporter.py
  - Properly escape special characters
  - Handle multiline content
  - Support custom delimiters
  - _Requirements: 8.3_

- [ ]* 11.7 Write property tests for CSV export
  - Create tests in python-backend/tests/test_csv_export.py
  - **Property 24: CSV special character escaping**
  - **Validates: Requirements 8.3**

- [ ] 11.8 Implement Hugging Face format export
  - Create python-backend/easy_dataset/core/exporters/huggingface_exporter.py
  - Format data compatible with datasets library
  - Create dataset_info.json
  - Support train/test splits
  - _Requirements: 8.4_

- [ ]* 11.9 Write property tests for Hugging Face export
  - Create tests in python-backend/tests/test_huggingface_export.py
  - **Property 25: Hugging Face format compatibility**
  - **Validates: Requirements 8.4**

- [ ] 11.10 Implement LLaMA Factory format export
  - Create python-backend/easy_dataset/core/exporters/llamafactory_exporter.py
  - Create configuration files
  - Format data in expected structure
  - Support different task types
  - _Requirements: 8.5_

- [ ]* 11.11 Write property tests for LLaMA Factory export
  - Create tests in python-backend/tests/test_llamafactory_export.py
  - **Property 26: LLaMA Factory format compliance**
  - **Validates: Requirements 8.5**

- [ ] 12. Implement image dataset functionality
- [ ] 12.1 Create image upload and storage service
  - Create python-backend/easy_dataset/core/image_service.py
  - Handle image uploads (JPEG, PNG, WebP)
  - Store images with metadata
  - Generate thumbnails (optional)
  - Extract image dimensions
  - _Requirements: 14.1_

- [ ]* 12.2 Write property tests for image upload
  - Create tests in python-backend/tests/test_image_service.py
  - **Property 42: Image format support**
  - **Validates: Requirements 14.1**

- [ ] 12.3 Implement image question generation
  - Create python-backend/easy_dataset/core/tasks/image_question_generation.py
  - Use vision-capable LLM models
  - Generate questions from images
  - Support custom question templates
  - _Requirements: 14.2_

- [ ]* 12.4 Write property tests for image questions
  - Create tests in python-backend/tests/test_image_questions.py
  - **Property 43: Vision model usage**
  - **Validates: Requirements 14.2**

- [ ] 12.5 Implement image dataset management
  - Create python-backend/easy_dataset/core/image_dataset_service.py
  - Create image datasets with QA pairs
  - Store image references and answers
  - Support different answer types (text, labels, custom)
  - _Requirements: 14.3_

- [ ]* 12.6 Write property tests for image datasets
  - Create tests in python-backend/tests/test_image_datasets.py
  - **Property 44: Image dataset storage**
  - **Validates: Requirements 14.3**

- [ ] 12.7 Implement image dataset export
  - Create python-backend/easy_dataset/core/exporters/image_exporter.py
  - Include image paths or base64 data
  - Support multiple export formats
  - Handle large image datasets
  - _Requirements: 14.4_

- [ ]* 12.8 Write property tests for image export
  - Create tests in python-backend/tests/test_image_export.py
  - **Property 45: Image export format**
  - **Validates: Requirements 14.4**

- [ ] 13. Implement internationalization (i18n)
- [ ] 13.1 Set up i18n infrastructure
  - Create python-backend/easy_dataset/utils/i18n.py
  - Configure babel for message extraction
  - Create translation file structure in python-backend/locales/
  - Implement language detection
  - Add language switcher support
  - _Requirements: 11.1, 11.4_

- [ ]* 13.2 Write property tests for i18n
  - Create tests in python-backend/tests/test_i18n.py
  - **Property 34: Language selection application**
  - **Validates: Requirements 11.1**
  - **Property 36: New language support**
  - **Validates: Requirements 11.4**

- [ ] 13.3 Create translations for English, Chinese, and Turkish
  - Create python-backend/locales/en/messages.json
  - Create python-backend/locales/zh-CN/messages.json
  - Create python-backend/locales/tr/messages.json
  - Translate all UI strings to English
  - Translate all UI strings to Chinese (zh-CN)
  - Translate all UI strings to Turkish (tr)
  - Translate LLM prompts for each language
  - _Requirements: 11.3_

- [ ] 14. Implement API features for frontend compatibility
- [ ] 14.1 Add WebSocket support for streaming
  - Create python-backend/easy_dataset_server/api/websocket.py
  - Implement WebSocket endpoint for LLM streaming
  - Stream task progress updates
  - Handle connection management
  - _Requirements: 4.6_

- [ ] 14.2 Implement query filtering and pagination
  - Create python-backend/easy_dataset/utils/query.py
  - Add filtering support to all list endpoints
  - Implement pagination with limit/offset
  - Support sorting by multiple fields
  - _Requirements: 12.4_

- [ ]* 14.3 Write property tests for query operations
  - Create tests in python-backend/tests/test_query.py
  - **Property 38: Query filtering and sorting**
  - **Validates: Requirements 12.4**

- [ ] 14.4 Add error handling and user feedback
  - Create python-backend/easy_dataset_server/middleware/error_handler.py
  - Return user-friendly error messages
  - Implement proper HTTP status codes
  - Add request validation errors
  - _Requirements: 10.4_

- [ ]* 14.5 Write property tests for error handling
  - Create tests in python-backend/tests/test_error_handling.py
  - **Property 33: Error message display**
  - **Validates: Requirements 10.4**

- [ ] 14.6 Implement database backup/export
  - Create python-backend/easy_dataset/database/backup.py
  - Export entire database to file
  - Support SQLite database file copy
  - Add backup scheduling (optional)
  - _Requirements: 12.5_

- [ ]* 14.7 Write property tests for database export
  - Create tests in python-backend/tests/test_database_backup.py
  - **Property 39: Database export completeness**
  - **Validates: Requirements 12.5**

- [ ] 15. Update Electron desktop application
- [ ] 15.1 Modify Electron main process to launch Python backend
  - Update electron/main.js to spawn Python process from python-backend/
  - Pass correct arguments to uvicorn
  - Handle backend startup and shutdown
  - Ensure graceful cleanup on exit
  - _Requirements: 13.1, 13.3_

- [ ]* 15.2 Write property tests for desktop shutdown
  - Create tests in python-backend/tests/test_desktop_integration.py
  - **Property 40: Desktop shutdown cleanup**
  - **Validates: Requirements 13.3**

- [ ] 15.3 Update Electron build configuration
  - Update electron-builder.yml to include python-backend/ in build
  - Package Python dependencies
  - Configure for Windows, macOS, Linux
  - Test installers on all platforms
  - _Requirements: 13.4_

- [ ] 15.4 Implement auto-update for Python backend
  - Create python-backend/easy_dataset/utils/updater.py
  - Check for backend updates
  - Download and install updates
  - Prompt user for update installation
  - _Requirements: 13.5_

- [ ]* 15.5 Write property tests for auto-update
  - Create tests in python-backend/tests/test_updater.py
  - **Property 41: Update check functionality**
  - **Validates: Requirements 13.5**

- [ ] 16. Create Docker deployment configuration
- [ ] 16.1 Create Dockerfile for Python backend
  - Use multi-stage build
  - Install Python dependencies
  - Copy application code
  - Configure uvicorn startup
  - _Requirements: 1.2_

- [ ] 16.2 Create docker-compose.yml
  - Define backend service
  - Configure volumes for data persistence
  - Set environment variables
  - Add health checks
  - _Requirements: 1.2_

- [ ] 16.3 Test Docker deployment
  - Build Docker image
  - Run container locally
  - Test all functionality
  - Verify data persistence
  - _Requirements: 1.2_

- [ ] 17. Implement CLI and usage examples
- [ ] 17.1 Create CLI interface
  - Implement click-based CLI commands
  - Add commands for project management (init, list, delete)
  - Add commands for file processing
  - Add commands for question/answer generation
  - Add command to start server
  - Add command for dataset export
  - _Requirements: 1.3_

- [ ] 17.2 Create usage examples
  - Write example for programmatic usage
  - Write example for standalone server
  - Write example for custom frontend integration
  - Write example for batch processing
  - Write Jupyter notebook examples
  - _Requirements: 1.3, 1.4_

- [ ] 18. Write comprehensive documentation
- [ ] 18.1 Create API documentation
  - Document all endpoints with examples
  - Add request/response schemas
  - Include authentication details
  - Use FastAPI's auto-generated docs
  - _Requirements: 1.4_

- [ ] 17.2 Create user documentation
  - Write installation guide
  - Create user manual
  - Document configuration options
  - Add troubleshooting section
  - _Requirements: 1.4_

- [ ] 17.3 Create developer documentation
  - Document architecture and design
  - Explain code organization
  - Add contribution guidelines
  - Document development setup
  - _Requirements: 1.3, 1.4_

- [ ] 18.4 Create package documentation
  - Write README with installation and usage
  - Document package API
  - Add examples and tutorials
  - Create changelog
  - _Requirements: 1.4_

- [ ] 19. Prepare package for distribution
- [ ] 19.1 Configure package metadata
  - Set up pyproject.toml with all metadata
  - Configure setup.py for backward compatibility
  - Create MANIFEST.in for package files
  - Add LICENSE file
  - _Requirements: 1.2_

- [ ] 19.2 Test package installation
  - Test pip install from source
  - Test with different Python versions (3.9, 3.10, 3.11, 3.12)
  - Test optional dependencies installation
  - Verify CLI commands work after install
  - _Requirements: 1.2_

- [ ] 19.3 Publish package to PyPI (optional)
  - Build distribution packages (wheel and sdist)
  - Test upload to TestPyPI
  - Upload to PyPI
  - Verify installation from PyPI
  - _Requirements: 1.2_

- [ ] 20. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 21. Performance optimization and final testing
- [ ] 21.1 Optimize database queries
  - Add indexes to frequently queried fields
  - Optimize N+1 query problems
  - Use eager loading where appropriate
  - _Requirements: 12.4_

- [ ] 21.2 Optimize file processing
  - Implement streaming for large files
  - Add progress tracking
  - Optimize memory usage
  - _Requirements: 2.6_

- [ ] 21.3 Optimize LLM API calls
  - Implement request caching
  - Add request queuing
  - Optimize batch processing
  - _Requirements: 5.5_

- [ ] 21.4 Perform end-to-end testing
  - Test complete workflows
  - Test with large datasets
  - Test on all platforms
  - Fix any discovered issues
  - _Requirements: 1.5_

- [ ] 21.5 Conduct performance testing
  - Load test API endpoints
  - Test concurrent task processing
  - Measure response times
  - Optimize bottlenecks
  - _Requirements: 2.6, 8.6_
