# Task System Implementation Summary

## Overview

This document summarizes the implementation of the task system for background jobs in the Easy Dataset Python backend. The task system provides a database-backed queue for managing long-running asynchronous operations.

## Components Implemented

### 1. Core Task Service (`easy_dataset/services/task_service.py`)

The `TaskService` class provides the main interface for managing background tasks:

**Key Features:**
- Create tasks with status tracking
- Update task progress in real-time
- Complete or fail tasks with error handling
- Cancel running tasks
- Recover interrupted tasks (e.g., after server restart)
- Track running asyncio tasks

**Main Methods:**
- `create_task()` - Create a new task record
- `get_task()` - Retrieve task by ID
- `list_tasks()` - List tasks with filtering
- `update_task_progress()` - Update progress percentage
- `complete_task()` - Mark task as completed
- `fail_task()` - Mark task as failed with error message
- `cancel_task()` - Cancel a running task
- `run_task_async()` - Execute task function asynchronously
- `start_task_async()` - Start and track an async task
- `recover_interrupted_tasks()` - Recover tasks after restart

### 2. Task Handlers (`easy_dataset/services/tasks/`)

Implemented task handlers for different types of background operations:

#### File Processing (`file_processing.py`)
- Extracts text from uploaded files using appropriate processors
- Splits text into chunks based on configuration
- Stores chunks in database
- Updates progress during processing

**Configuration:**
- `strategy`: 'markdown' | 'delimiter' | 'auto'
- `chunk_size`: Size of chunks (for auto strategy)
- `overlap`: Overlap between chunks
- `delimiter`: Custom delimiter (for delimiter strategy)

#### Question Generation (`question_generation.py`)
- Generates questions from text chunks using LLM
- Supports multiple languages (en, zh-CN, tr)
- Handles genre-audience pairs for specialized questioning
- Processes chunks in parallel batches
- Parses JSON responses from LLM

**Configuration:**
- `provider_config`: LLM provider configuration
- `language`: Language for generation
- `questions_per_chunk`: Number of questions to generate
- `parallelism`: Number of concurrent generations
- `active_ga_pair`: Optional genre-audience pair
- `custom_prompt`: Optional custom prompt template

#### Answer Generation (`answer_generation.py`)
- Generates answers for questions using LLM with chunk context
- Extracts chain-of-thought reasoning from responses
- Creates dataset entries with question-answer pairs
- Maintains question-answer pair integrity
- Processes questions in parallel batches

**Configuration:**
- `provider_config`: LLM provider configuration
- `language`: Language for generation
- `parallelism`: Number of concurrent generations
- `question_template`: Optional template for custom answer format
- `custom_prompt`: Optional custom prompt template
- `model_name`: Name of model used (for metadata)

#### Data Cleaning (`data_cleaning.py`)
- Normalizes whitespace in questions and answers
- Fixes formatting issues (punctuation, spacing)
- Removes duplicate entries (optional)
- Cleans text in all dataset entries

**Configuration:**
- `remove_duplicates`: Whether to remove duplicate entries
- `keep_first`: If removing duplicates, keep first occurrence

**Cleaning Operations:**
- Normalize whitespace
- Remove duplicate punctuation
- Fix spacing around punctuation
- Find and remove duplicate entries

#### Dataset Evaluation (`dataset_evaluation.py`)
- Evaluates dataset quality using LLM
- Generates AI evaluation scores (0-5)
- Stores evaluation conclusions
- Processes entries in parallel batches

**Configuration:**
- `provider_config`: LLM provider configuration
- `language`: Language for evaluation
- `parallelism`: Number of concurrent evaluations

**Evaluation Dimensions:**
- Question Quality (25%)
- Answer Quality (35%)
- Text Relevance (25%)
- Overall Consistency (15%)

#### Multi-turn Conversation Generation (`conversation_generation.py`)
- Generates multi-turn dialogues for chat model training
- Maintains context across turns
- Stores conversations in ShareGPT format
- Supports configurable scenarios and roles

**Configuration:**
- `provider_config`: LLM provider configuration
- `language`: Language for generation
- `scenario`: Conversation scenario
- `role_a`: Role A definition
- `role_b`: Role B definition
- `max_turns`: Maximum number of turns
- `parallelism`: Number of concurrent generations
- `model_name`: Name of model used (for metadata)

## Task Status Values

Tasks can have the following status values (defined in `TaskStatus` enum):

- `PROCESSING (0)`: Task is currently running
- `COMPLETED (1)`: Task completed successfully
- `FAILED (2)`: Task failed with error
- `INTERRUPTED (3)`: Task was canceled or interrupted

## Task Types

The following task types are supported:

- `text-processing`: File processing and chunking
- `question-generation`: Question generation from chunks
- `answer-generation`: Answer generation for questions
- `data-distillation`: Data cleaning and refinement
- `dataset-evaluation`: Dataset quality evaluation
- `multi-turn-generation`: Multi-turn conversation generation
- `image-question-generation`: Image question generation (to be implemented)
- `image-dataset-generation`: Image dataset generation (to be implemented)

## Usage Example

```python
from sqlalchemy.orm import Session
from easy_dataset.services import TaskService
from easy_dataset.services.tasks import process_question_generation_task

# Create task service
db: Session = get_db_session()
task_service = TaskService(db)

# Create a task
task = task_service.create_task(
    project_id="project123",
    task_type="question-generation",
    total_count=10,
    model_info={"provider": "openai", "model": "gpt-4"},
    language="en"
)

# Start task asynchronously
config = {
    "provider_config": {
        "provider": "openai",
        "api_key": "sk-...",
        "model": "gpt-4"
    },
    "language": "en",
    "questions_per_chunk": 3,
    "parallelism": 3
}

chunk_ids = ["chunk1", "chunk2", "chunk3"]

# Start the task
task_service.start_task_async(
    task.id,
    process_question_generation_task,
    db,
    "project123",
    chunk_ids,
    config
)

# Check task status
task = task_service.get_task(task.id)
print(f"Status: {task.status}, Progress: {task.progress_percentage}%")

# Cancel task if needed
task_service.cancel_task(task.id)
```

## Database Schema

Tasks are stored in the `task` table with the following fields:

- `id`: Unique task identifier (nanoid)
- `project_id`: ID of the project this task belongs to
- `task_type`: Type of task being performed
- `status`: Task status (0=processing, 1=completed, 2=failed, 3=interrupted)
- `start_time`: Task start timestamp
- `end_time`: Task end timestamp (None if still running)
- `completed_count`: Number of items completed
- `total_count`: Total number of items to process
- `model_info`: JSON string containing model information
- `language`: Language for generation
- `detail`: Task details
- `note`: Task notes/error messages
- `create_at`: Creation timestamp
- `update_at`: Last update timestamp

## Error Handling

All task handlers implement comprehensive error handling:

1. **Task-level errors**: Caught and stored in task.note, task marked as FAILED
2. **Item-level errors**: Logged but processing continues with other items
3. **Cancellation**: Properly handled with asyncio.CancelledError
4. **Recovery**: Interrupted tasks can be recovered after server restart

## Progress Tracking

Tasks update progress in real-time:

- Progress is calculated as `(completed_count / total_count) * 100`
- Progress updates are committed to database periodically
- Progress notes provide detailed status information

## Concurrency

Task handlers support configurable parallelism:

- Multiple items can be processed concurrently
- Default parallelism is 3 for most operations
- Parallelism can be adjusted based on system resources
- Uses `asyncio.gather()` for concurrent execution

## Integration with LLM Service

Task handlers integrate with the LLM service for AI-powered operations:

- Support for multiple LLM providers (OpenAI, Ollama, Gemini, etc.)
- Streaming and non-streaming responses
- Retry logic with exponential backoff
- Provider configuration from database

## Future Enhancements

Potential improvements for the task system:

1. **Task Scheduling**: Add support for scheduled/recurring tasks
2. **Task Dependencies**: Support task chains and dependencies
3. **Task Priorities**: Implement priority queue for task execution
4. **Resource Limits**: Add CPU/memory limits for tasks
5. **Task Monitoring**: Add metrics and monitoring dashboard
6. **Task Retry**: Automatic retry for failed tasks
7. **Task Notifications**: Notify users when tasks complete
8. **Distributed Tasks**: Support for distributed task execution with Celery

## Testing

The task system should be tested with:

1. **Unit Tests**: Test individual task service methods
2. **Integration Tests**: Test task handlers with database
3. **Property-Based Tests**: Test task system properties (see tasks.md)
4. **End-to-End Tests**: Test complete workflows

## Conclusion

The task system provides a robust foundation for managing background jobs in the Easy Dataset application. It supports all major operations including file processing, question/answer generation, data cleaning, evaluation, and conversation generation. The system is designed to be extensible, allowing new task types to be added easily.
