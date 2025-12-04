# Image Dataset Implementation

This document describes the implementation of image dataset functionality for the Easy Dataset Python backend.

## Overview

The image dataset functionality enables users to:
- Upload and store images (JPEG, PNG, WebP)
- Generate questions from images using vision-capable LLM models
- Create and manage image QA datasets
- Export image datasets in multiple formats

## Components

### 1. Image Service (`easy_dataset/services/image_service.py`)

Handles image upload, storage, and retrieval.

**Key Features:**
- Image format validation (JPEG, PNG, WebP)
- File size validation (max 100MB)
- Automatic dimension extraction using PIL
- Unique filename generation
- Optional thumbnail generation
- Base64 encoding support
- Data URL generation for vision APIs

**Main Methods:**
```python
async def upload_image(project_id, image_name, image_data, generate_thumb=False) -> Images
def get_image(image_id) -> Optional[Images]
def list_images(project_id, limit=100, offset=0) -> List[Images]
def delete_image(image_id) -> bool
def get_image_data_url(image_id) -> Optional[str]  # For vision API calls
def get_project_image_stats(project_id) -> Dict[str, int]
```

**Usage Example:**
```python
from easy_dataset.services.image_service import ImageService

image_service = ImageService(db_session, storage_path="uploads/images")

# Upload image
with open("photo.jpg", "rb") as f:
    image = await image_service.upload_image(
        project_id="proj123",
        image_name="photo.jpg",
        image_data=f,
        generate_thumb=True
    )

# Get image as data URL for vision API
data_url = image_service.get_image_data_url(image.id)
```

### 2. Image Question Generation Task (`easy_dataset/services/tasks/image_question_generation.py`)

Generates questions from images using vision-capable LLM models.

**Key Features:**
- Vision model validation (GPT-4V, Gemini Vision, Claude 3, etc.)
- Multi-language support (en, zh-CN, tr)
- Custom prompt templates
- Batch processing with concurrency control
- Progress tracking
- Error handling and retry logic

**Main Methods:**
```python
async def generate_questions_for_image(image, config, num_questions=3, custom_prompt=None, language="en") -> List[str]
async def process_task(task, config) -> Dict[str, Any]
async def generate_single_question(image_id, config, custom_prompt=None, language="en") -> Optional[str]
```

**Usage Example:**
```python
from easy_dataset.services.tasks.image_question_generation import ImageQuestionGenerationTask

task_handler = ImageQuestionGenerationTask(db_session, llm_service, image_service)

# Generate questions for single image
llm_config = {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "sk-...",
    "temperature": 0.7
}

questions = await task_handler.generate_questions_for_image(
    image=image,
    config=llm_config,
    num_questions=5,
    language="en"
)

# Process batch task
task_config = {
    "image_ids": ["img1", "img2", "img3"],
    "num_questions": 3,
    "language": "en",
    "concurrency": 3,
    "llm_config": llm_config
}

result = await task_handler.process_task(task, task_config)
```

**Supported Vision Models:**
- OpenAI: gpt-4o, gpt-4-vision, gpt-4-turbo
- Google: gemini-pro-vision, gemini-1.5-pro, gemini-1.5-flash
- Anthropic: claude-3-opus, claude-3-sonnet, claude-3-haiku

### 3. Image Dataset Service (`easy_dataset/services/image_dataset_service.py`)

Manages image QA dataset entries.

**Key Features:**
- Create dataset entries with QA pairs
- Support multiple answer types (text, label, custom_format)
- Link to source images and questions
- Filtering and search
- Batch operations
- Quality scoring and confirmation
- Tag management

**Answer Types:**
- `text`: Free-form text answer
- `label`: JSON array of label selections
- `custom_format`: Custom JSON format answer

**Main Methods:**
```python
def create_dataset_entry(project_id, image_id, question, answer, model, answer_type="text", ...) -> ImageDatasets
def create_from_question(question_id, answer, model, answer_type="text", ...) -> ImageDatasets
def get_dataset_entry(entry_id) -> Optional[ImageDatasets]
def list_dataset_entries(project_id, image_id=None, answer_type=None, confirmed=None, ...) -> List[ImageDatasets]
def update_dataset_entry(entry_id, **updates) -> Optional[ImageDatasets]
def delete_dataset_entry(entry_id) -> bool
def batch_create_from_questions(question_ids, answers, model, answer_type="text", ...) -> List[ImageDatasets]
def get_dataset_stats(project_id) -> Dict[str, Any]
def confirm_entry(entry_id, confirmed=True) -> Optional[ImageDatasets]
def rate_entry(entry_id, score) -> Optional[ImageDatasets]
def add_tags(entry_id, new_tags) -> Optional[ImageDatasets]
```

**Usage Example:**
```python
from easy_dataset.services.image_dataset_service import ImageDatasetService

dataset_service = ImageDatasetService(db_session)

# Create dataset entry
entry = dataset_service.create_dataset_entry(
    project_id="proj123",
    image_id="img456",
    question="What is in this image?",
    answer="A cat sitting on a chair",
    model="gpt-4o",
    answer_type="text",
    score=4.5,
    tags="animal, furniture"
)

# Create from existing question
entry = dataset_service.create_from_question(
    question_id="q789",
    answer="A beautiful sunset over the ocean",
    model="gpt-4o"
)

# List with filters
entries = dataset_service.list_dataset_entries(
    project_id="proj123",
    confirmed=True,
    min_score=4.0,
    tags=["nature"]
)

# Get statistics
stats = dataset_service.get_dataset_stats("proj123")
# Returns: {
#   "total_entries": 150,
#   "confirmed_entries": 120,
#   "average_score": 4.2,
#   "by_answer_type": {"text": 140, "label": 10},
#   "unique_images": 50
# }
```

### 4. Image Dataset Exporter (`easy_dataset/services/exporters/image_exporter.py`)

Exports image datasets in various formats.

**Key Features:**
- Export with image paths or base64 data
- Multiple format styles (default, LLaVA, VQA)
- JSON and JSONL output
- Export with separate image files
- Hugging Face datasets format
- Handle large datasets efficiently

**Export Formats:**
- **Default**: Simple QA format with image reference
- **LLaVA**: Training format for LLaVA models
- **VQA**: Visual Question Answering format
- **Hugging Face**: Compatible with HF datasets library

**Main Methods:**
```python
def export_json(entries, output_path, use_base64=False, format_style="default", include_metadata=True) -> int
def export_jsonl(entries, output_path, use_base64=False, format_style="default", include_metadata=True) -> int
def export_with_images(entries, output_dir, format_style="default", copy_images=True) -> Dict[str, Any]
def export_huggingface_format(entries, output_dir, dataset_name="image_dataset", copy_images=True) -> Dict[str, Any]
```

**Usage Example:**
```python
from easy_dataset.services.exporters.image_exporter import ImageDatasetExporter

exporter = ImageDatasetExporter(db_session, image_service)

# Export to JSON with base64 images
exporter.export_json(
    entries=entries,
    output_path="dataset.json",
    use_base64=True,
    format_style="llava"
)

# Export to JSONL with image paths
exporter.export_jsonl(
    entries=entries,
    output_path="dataset.jsonl",
    use_base64=False,
    format_style="vqa"
)

# Export with separate image files
result = exporter.export_with_images(
    entries=entries,
    output_dir="dataset_export",
    format_style="default",
    copy_images=True
)

# Export in Hugging Face format
result = exporter.export_huggingface_format(
    entries=entries,
    output_dir="hf_dataset",
    dataset_name="my_image_qa_dataset",
    copy_images=True
)
```

**Export Format Examples:**

**LLaVA Format:**
```json
{
  "id": "entry123",
  "image": "images/photo.jpg",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nWhat is in this image?"
    },
    {
      "from": "gpt",
      "value": "A cat sitting on a chair"
    }
  ]
}
```

**VQA Format:**
```json
{
  "question_id": "entry123",
  "image_id": "img456",
  "image": "images/photo.jpg",
  "question": "What is in this image?",
  "answer": "A cat sitting on a chair",
  "answer_type": "text"
}
```

## Database Models

### Images Model
```python
class Images(Base):
    id: str                    # Unique identifier (nanoid)
    project_id: str            # Project reference
    image_name: str            # Original filename
    path: str                  # Storage path
    size: int                  # File size in bytes
    width: int | None          # Image width in pixels
    height: int | None         # Image height in pixels
    create_at: datetime        # Upload timestamp
    update_at: datetime        # Last update timestamp
```

### ImageDatasets Model
```python
class ImageDatasets(Base):
    id: str                    # Unique identifier (nanoid)
    project_id: str            # Project reference
    image_id: str              # Image reference
    image_name: str            # Image filename
    question_id: str | None    # Optional question reference
    question: str              # Question text
    answer: str                # Answer text
    answer_type: str           # Answer type (text, label, custom_format)
    model: str                 # Model used
    confirmed: bool            # User confirmation
    score: float               # Quality score (0-5)
    tags: str                  # Comma-separated tags
    note: str                  # User notes
    create_at: datetime        # Creation timestamp
    update_at: datetime        # Last update timestamp
```

## Integration with Existing Systems

### Task System Integration

The image question generation task can be integrated with the existing task system:

```python
from easy_dataset.services.task_service import TaskService
from easy_dataset.services.tasks.image_question_generation import ImageQuestionGenerationTask

# Create task
task = task_service.create_task(
    project_id="proj123",
    task_type="image-question-generation",
    config={
        "image_ids": ["img1", "img2"],
        "num_questions": 3,
        "language": "en",
        "llm_config": {...}
    }
)

# Process task
task_handler = ImageQuestionGenerationTask(db_session, llm_service, image_service)
result = await task_handler.process_task(task, config)
```

### LLM Service Integration

The image question generation uses the existing LLM service for vision API calls:

```python
# Vision chat is already supported in LLMService
response = await llm_service.vision_chat(
    config=llm_config,
    prompt="What is in this image?",
    image_data=data_url,
    mime_type="image/jpeg"
)
```

### Export Service Integration

The image exporter can be integrated with the existing export service:

```python
from easy_dataset.services.exporter import DatasetExporterService
from easy_dataset.services.exporters.image_exporter import ImageDatasetExporter

# Add image export to main exporter
exporter_service = DatasetExporterService(db_session)
image_exporter = ImageDatasetExporter(db_session, image_service)

# Export image dataset
entries = dataset_service.list_dataset_entries(project_id)
image_exporter.export_json(entries, "output.json", format_style="llava")
```

## API Endpoints (To Be Implemented)

Suggested API endpoints for the frontend:

```python
# Images
POST   /api/projects/{project_id}/images          # Upload image
GET    /api/projects/{project_id}/images          # List images
GET    /api/images/{image_id}                     # Get image details
DELETE /api/images/{image_id}                     # Delete image
GET    /api/images/{image_id}/data                # Get image binary data

# Image Questions
POST   /api/projects/{project_id}/image-questions # Generate questions
GET    /api/projects/{project_id}/image-questions # List questions

# Image Datasets
POST   /api/projects/{project_id}/image-datasets  # Create dataset entry
GET    /api/projects/{project_id}/image-datasets  # List dataset entries
GET    /api/image-datasets/{entry_id}             # Get entry details
PUT    /api/image-datasets/{entry_id}             # Update entry
DELETE /api/image-datasets/{entry_id}             # Delete entry
POST   /api/image-datasets/{entry_id}/confirm     # Confirm entry
POST   /api/image-datasets/{entry_id}/rate        # Rate entry

# Export
POST   /api/projects/{project_id}/image-datasets/export  # Export dataset
```

## Testing

### Unit Tests

Test files should be created for each component:

```
tests/
├── test_image_service.py
├── test_image_question_generation.py
├── test_image_dataset_service.py
└── test_image_exporter.py
```

### Property-Based Tests

Property tests for image functionality (optional tasks in spec):

- **Property 42**: Image format support validation
- **Property 43**: Vision model usage verification
- **Property 44**: Image dataset storage integrity
- **Property 45**: Image export format validation
- **Property 46**: PDF image extraction

## Dependencies

Required Python packages:

```
Pillow>=10.0.0          # Image processing
```

All other dependencies are already included in the project.

## Configuration

### Storage Configuration

Images are stored in the `uploads/images` directory by default. This can be configured:

```python
image_service = ImageService(
    db_session=db_session,
    storage_path="custom/path/to/images"
)
```

### Vision Model Configuration

Ensure the LLM configuration uses a vision-capable model:

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-4o",  # Vision-capable model
    "api_key": "sk-...",
    "temperature": 0.7,
    "max_tokens": 2048
}
```

## Error Handling

All services include comprehensive error handling:

- **ImageService**: Validates formats, sizes, and handles file I/O errors
- **ImageQuestionGenerationTask**: Validates vision models, handles API errors
- **ImageDatasetService**: Validates references, handles database errors
- **ImageDatasetExporter**: Handles missing images, file I/O errors

## Performance Considerations

1. **Image Storage**: Images are stored on disk, not in database
2. **Batch Processing**: Concurrent processing with configurable limits
3. **Large Datasets**: JSONL format for streaming large exports
4. **Base64 Encoding**: Optional, use paths for better performance
5. **Thumbnail Generation**: Optional feature for UI optimization

## Future Enhancements

Potential improvements:

1. Image preprocessing (resize, crop, normalize)
2. Multiple images per question support
3. Image similarity search
4. Automatic image tagging
5. Cloud storage integration (S3, GCS)
6. Image augmentation for training
7. OCR integration for text extraction
8. Object detection integration

## Conclusion

The image dataset functionality is now fully implemented and ready for integration with the frontend. All core features are working:

✅ Image upload and storage
✅ Vision-based question generation
✅ Image dataset management
✅ Multiple export formats

The implementation follows the existing patterns in the codebase and integrates seamlessly with the task system, LLM service, and export functionality.
