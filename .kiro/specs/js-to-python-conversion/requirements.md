# Requirements Document

## Introduction

This document specifies the requirements for converting the Easy Dataset application from JavaScript (Next.js/React/Electron) to Python. Easy Dataset is a comprehensive application for creating LLM fine-tuning datasets, featuring document processing, AI-powered question/answer generation, and dataset export capabilities. The conversion aims to maintain all existing functionality while leveraging Python's ecosystem for AI/ML applications.

## Glossary

- **Easy Dataset System**: The complete application being converted from JavaScript to Python
- **Frontend Application**: The web-based user interface component
- **Backend Service**: The server-side API and business logic component
- **Desktop Application**: The standalone desktop version of the application
- **LLM Provider**: External AI model service (OpenAI, Ollama, etc.)
- **Document Processor**: Component that extracts and processes text from various file formats
- **Task System**: Asynchronous job processing system for long-running operations
- **Data Model**: Database schema and ORM entities
- **Dataset**: Collection of question-answer pairs for LLM training
- **Chunk**: Segmented portion of processed document text
- **Project**: User workspace containing documents, questions, and datasets

## Requirements

### Requirement 1

**User Story:** As a developer, I want to understand the conversion scope and target architecture, so that I can plan the migration effectively.

#### Acceptance Criteria

1. WHEN analyzing the existing codebase THEN the system SHALL identify all JavaScript modules requiring conversion
2. WHEN selecting Python frameworks THEN the system SHALL choose equivalents that match or exceed current functionality
3. WHEN defining the target architecture THEN the system SHALL maintain the modular structure of the original application
4. WHEN documenting dependencies THEN the system SHALL map each JavaScript library to its Python equivalent
5. WHEN planning the conversion THEN the system SHALL identify components that can be converted independently

### Requirement 2

**User Story:** As a user, I want the Python version to support the same document formats, so that I can process my existing files without changes.

#### Acceptance Criteria

1. WHEN uploading a PDF file THEN the Document Processor SHALL extract text content with the same accuracy as the JavaScript version
2. WHEN uploading a Markdown file THEN the Document Processor SHALL parse structure and content correctly
3. WHEN uploading a DOCX file THEN the Document Processor SHALL extract formatted text and preserve structure
4. WHEN uploading an EPUB file THEN the Document Processor SHALL extract chapter content and metadata
5. WHEN uploading a TXT file THEN the Document Processor SHALL process plain text with proper encoding detection
6. WHEN processing any supported format THEN the Document Processor SHALL handle files up to 100MB in size

### Requirement 3

**User Story:** As a user, I want intelligent text chunking capabilities, so that I can split documents into meaningful segments for dataset creation.

#### Acceptance Criteria

1. WHEN splitting by markdown headers THEN the system SHALL preserve document hierarchy and create logical chunks
2. WHEN using custom delimiters THEN the system SHALL split text according to user-defined patterns
3. WHEN applying automatic chunking THEN the system SHALL create chunks of configurable size with overlap
4. WHEN extracting table of contents THEN the system SHALL identify document structure and navigation points
5. WHEN processing multilingual documents THEN the system SHALL handle UTF-8 encoded text correctly

### Requirement 4

**User Story:** As a user, I want to integrate with multiple AI model providers, so that I can use different LLMs for question and answer generation.

#### Acceptance Criteria

1. WHEN configuring OpenAI provider THEN the system SHALL support GPT-3.5, GPT-4, and newer models
2. WHEN configuring Ollama provider THEN the system SHALL connect to local Ollama instances and list available models
3. WHEN configuring OpenRouter provider THEN the system SHALL access multiple models through unified interface
4. WHEN configuring LiteLLM provider THEN the system SHALL support 100+ models through unified proxy interface
5. WHEN configuring Gemini provider THEN the system SHALL support Google Gemini models with proper authentication
6. WHEN generating content THEN the system SHALL support both streaming and non-streaming responses
7. WHEN an API call fails THEN the system SHALL implement exponential backoff retry logic up to 3 attempts

### Requirement 5

**User Story:** As a user, I want to generate questions from document chunks, so that I can create training data for my LLM.

#### Acceptance Criteria

1. WHEN selecting chunks for question generation THEN the system SHALL process them using the configured LLM Provider
2. WHEN generating questions THEN the system SHALL support customizable prompt templates with i18n
3. WHEN questions are generated THEN the system SHALL store them with references to source chunks
4. WHEN using question templates THEN the system SHALL support multiple question types and formats
5. WHEN batch processing THEN the system SHALL handle concurrent generation with configurable parallelism

### Requirement 6

**User Story:** As a user, I want to generate answers for questions, so that I can complete my training dataset.

#### Acceptance Criteria

1. WHEN generating answers THEN the system SHALL use the question and source chunk as context
2. WHEN using custom prompts THEN the system SHALL support user-defined answer generation templates
3. WHEN answers are generated THEN the system SHALL store them linked to their questions
4. WHEN enhancing answers THEN the system SHALL support chain-of-thought and detailed explanation modes
5. WHEN batch processing answers THEN the system SHALL maintain question-answer pair integrity

### Requirement 7

**User Story:** As a user, I want to manage and organize my datasets, so that I can prepare them for export and training.

#### Acceptance Criteria

1. WHEN creating a dataset THEN the system SHALL allow selection of question-answer pairs from the project
2. WHEN viewing datasets THEN the system SHALL display metadata including creation date, size, and tags
3. WHEN editing dataset entries THEN the system SHALL support inline editing of questions and answers
4. WHEN rating dataset quality THEN the system SHALL allow star ratings and notes for each entry
5. WHEN filtering datasets THEN the system SHALL support search by tags, ratings, and content
6. WHEN deleting dataset entries THEN the system SHALL remove them without affecting source questions

### Requirement 8

**User Story:** As a user, I want to export datasets in multiple formats, so that I can use them with different training frameworks.

#### Acceptance Criteria

1. WHEN exporting to JSON THEN the system SHALL format data according to common LLM training schemas
2. WHEN exporting to JSONL THEN the system SHALL create one JSON object per line for streaming processing
3. WHEN exporting to CSV THEN the system SHALL properly escape special characters and handle multiline content
4. WHEN exporting to Hugging Face THEN the system SHALL format data compatible with datasets library
5. WHEN exporting to LLaMA Factory THEN the system SHALL create configuration files and data in expected format
6. WHEN exporting large datasets THEN the system SHALL show progress and handle files over 10,000 entries

### Requirement 9

**User Story:** As a user, I want a task system for long-running operations, so that I can monitor progress and manage background jobs.

#### Acceptance Criteria

1. WHEN starting a file processing task THEN the Task System SHALL create a task record with pending status
2. WHEN a task is running THEN the Task System SHALL update progress percentage in real-time
3. WHEN a task completes THEN the Task System SHALL update status to completed and store results
4. WHEN a task fails THEN the Task System SHALL capture error details and allow retry
5. WHEN viewing tasks THEN the system SHALL display all tasks with status, progress, and timestamps
6. WHEN canceling a task THEN the Task System SHALL stop execution and mark as canceled

### Requirement 10

**User Story:** As a user, I want a web-based interface, so that I can access the application from my browser.

#### Acceptance Criteria

1. WHEN accessing the application THEN the Frontend Application SHALL display a responsive interface
2. WHEN navigating between pages THEN the Frontend Application SHALL maintain state and provide smooth transitions
3. WHEN performing actions THEN the Frontend Application SHALL provide immediate feedback and loading indicators
4. WHEN errors occur THEN the Frontend Application SHALL display user-friendly error messages
5. WHEN using on mobile devices THEN the Frontend Application SHALL adapt layout for smaller screens

### Requirement 11

**User Story:** As a user, I want multi-language support, so that I can use the application in my preferred language.

#### Acceptance Criteria

1. WHEN selecting a language THEN the system SHALL display all UI text in the chosen language
2. WHEN generating content THEN the system SHALL use language-appropriate prompts for the LLM Provider
3. WHEN the system supports a language THEN the system SHALL provide complete translations for English, Chinese, and Turkish
4. WHEN adding new languages THEN the system SHALL support i18n file-based translation management

### Requirement 12

**User Story:** As a user, I want data persistence with SQLite, so that my projects and datasets are saved locally.

#### Acceptance Criteria

1. WHEN creating a project THEN the system SHALL store it in the SQLite database with unique identifier
2. WHEN the application starts THEN the system SHALL initialize the database schema if not present
3. WHEN performing CRUD operations THEN the system SHALL use an ORM for type-safe database access
4. WHEN querying data THEN the system SHALL support filtering, sorting, and pagination
5. WHEN backing up data THEN the system SHALL allow export of the entire database file

### Requirement 13

**User Story:** As a developer, I want a desktop application version, so that users can run Easy Dataset without a web server.

#### Acceptance Criteria

1. WHEN launching the desktop application THEN the Desktop Application SHALL start a local backend service
2. WHEN the backend is ready THEN the Desktop Application SHALL open a window displaying the frontend
3. WHEN closing the window THEN the Desktop Application SHALL shut down the backend service gracefully
4. WHEN packaging for distribution THEN the system SHALL create installers for Windows, macOS, and Linux
5. WHEN auto-updating THEN the Desktop Application SHALL check for updates and prompt user to install

### Requirement 14

**User Story:** As a user, I want image dataset support, so that I can create vision-language training data.

#### Acceptance Criteria

1. WHEN uploading images THEN the system SHALL support JPEG, PNG, and WebP formats
2. WHEN generating image questions THEN the system SHALL use vision-capable LLM Provider models
3. WHEN creating image datasets THEN the system SHALL store image references and generated QA pairs
4. WHEN exporting image datasets THEN the system SHALL include image paths or base64 encoded data
5. WHEN processing PDF with images THEN the system SHALL extract images and associate with text chunks

### Requirement 15

**User Story:** As a user, I want multi-turn conversation dataset support, so that I can create dialogue training data.

#### Acceptance Criteria

1. WHEN creating a conversation THEN the system SHALL support multiple message turns with roles
2. WHEN generating conversations THEN the system SHALL maintain context across turns
3. WHEN editing conversations THEN the system SHALL allow modification of individual messages
4. WHEN exporting conversations THEN the system SHALL format data for chat model training
5. WHEN rating conversations THEN the system SHALL support quality assessment of entire dialogues
