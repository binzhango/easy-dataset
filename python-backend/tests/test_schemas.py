"""Unit tests for Pydantic schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from easy_dataset.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    UploadFileCreate,
    UploadFileResponse,
    ChunkCreate,
    ChunkUpdate,
    ChunkResponse,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatus,
    TaskType,
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse,
)


class TestProjectSchemas:
    """Test project schemas."""
    
    def test_project_create_valid(self):
        """Test creating a valid project."""
        project = ProjectCreate(
            name="Test Project",
            description="Test Description",
            global_prompt="Global prompt",
            question_prompt="Question prompt",
            answer_prompt="Answer prompt",
        )
        assert project.name == "Test Project"
        assert project.description == "Test Description"
        assert project.global_prompt == "Global prompt"
    
    def test_project_create_with_defaults(self):
        """Test project creation with default values."""
        project = ProjectCreate(
            name="Test Project",
            description="Test Description",
        )
        assert project.global_prompt == ""
        assert project.question_prompt == ""
        assert project.answer_prompt == ""
        assert project.default_model_config_id is None
    
    def test_project_create_empty_name_fails(self):
        """Test that empty project name fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(
                name="",
                description="Test Description",
            )
        assert "name" in str(exc_info.value)
    
    def test_project_update_partial(self):
        """Test partial project update."""
        update = ProjectUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.description is None
        assert update.global_prompt is None
    
    def test_project_response_from_dict(self):
        """Test creating project response from dict."""
        data = {
            "id": "proj123",
            "name": "Test Project",
            "description": "Test Description",
            "global_prompt": "Global",
            "question_prompt": "Question",
            "answer_prompt": "Answer",
            "label_prompt": "Label",
            "domain_tree_prompt": "Domain",
            "clean_prompt": "Clean",
            "test": "test",
            "create_at": datetime.now(),
            "update_at": datetime.now(),
        }
        response = ProjectResponse(**data)
        assert response.id == "proj123"
        assert response.name == "Test Project"


class TestFileSchemas:
    """Test file schemas."""
    
    def test_upload_file_create_valid(self):
        """Test creating a valid upload file."""
        file = UploadFileCreate(
            file_name="test.pdf",
            file_ext=".pdf",
            path="/uploads/test.pdf",
            size=1024,
            md5="d41d8cd98f00b204e9800998ecf8427e",
            project_id="proj123",
        )
        assert file.file_name == "test.pdf"
        assert file.size == 1024
        assert len(file.md5) == 32
    
    def test_upload_file_invalid_size(self):
        """Test that zero or negative size fails validation."""
        with pytest.raises(ValidationError):
            UploadFileCreate(
                file_name="test.pdf",
                file_ext=".pdf",
                path="/uploads/test.pdf",
                size=0,  # Invalid
                md5="d41d8cd98f00b204e9800998ecf8427e",
                project_id="proj123",
            )
    
    def test_upload_file_invalid_md5(self):
        """Test that invalid MD5 length fails validation."""
        with pytest.raises(ValidationError):
            UploadFileCreate(
                file_name="test.pdf",
                file_ext=".pdf",
                path="/uploads/test.pdf",
                size=1024,
                md5="short",  # Invalid: not 32 chars
                project_id="proj123",
            )


class TestChunkSchemas:
    """Test chunk schemas."""
    
    def test_chunk_create_valid(self):
        """Test creating a valid chunk."""
        chunk = ChunkCreate(
            name="Chunk 1",
            content="This is test content",
            summary="Test summary",
            size=20,
            project_id="proj123",
            file_id="file123",
            file_name="test.pdf",
        )
        assert chunk.name == "Chunk 1"
        assert chunk.size == 20
        assert chunk.content == "This is test content"
    
    def test_chunk_create_empty_content_fails(self):
        """Test that empty content fails validation."""
        with pytest.raises(ValidationError):
            ChunkCreate(
                name="Chunk 1",
                content="",  # Invalid
                summary="Test summary",
                size=20,
                project_id="proj123",
                file_id="file123",
                file_name="test.pdf",
            )
    
    def test_chunk_update_partial(self):
        """Test partial chunk update."""
        update = ChunkUpdate(content="Updated content")
        assert update.content == "Updated content"
        assert update.name is None
        assert update.summary is None


class TestQuestionSchemas:
    """Test question schemas."""
    
    def test_question_create_valid(self):
        """Test creating a valid question."""
        question = QuestionCreate(
            question="What is this?",
            label="general",
            project_id="proj123",
            chunk_id="chunk123",
            answered=False,
        )
        assert question.question == "What is this?"
        assert question.answered is False
        assert question.image_id is None
    
    def test_question_create_with_image(self):
        """Test creating a question with image."""
        question = QuestionCreate(
            question="What's in this image?",
            label="vision",
            project_id="proj123",
            chunk_id="chunk123",
            image_id="img123",
            image_name="test.jpg",
        )
        assert question.image_id == "img123"
        assert question.image_name == "test.jpg"
    
    def test_question_update_answered(self):
        """Test updating question answered status."""
        update = QuestionUpdate(answered=True)
        assert update.answered is True
        assert update.question is None


class TestDatasetSchemas:
    """Test dataset schemas."""
    
    def test_dataset_create_valid(self):
        """Test creating a valid dataset entry."""
        dataset = DatasetCreate(
            question="What is AI?",
            answer="AI is artificial intelligence",
            chunk_name="Chunk 1",
            chunk_content="Content about AI",
            model="gpt-4",
            question_label="general",
            project_id="proj123",
            question_id="q123",
            score=4.5,
            confirmed=True,
        )
        assert dataset.question == "What is AI?"
        assert dataset.score == 4.5
        assert dataset.confirmed is True
    
    def test_dataset_create_with_defaults(self):
        """Test dataset creation with default values."""
        dataset = DatasetCreate(
            question="What is AI?",
            answer="AI is artificial intelligence",
            chunk_name="Chunk 1",
            chunk_content="Content about AI",
            model="gpt-4",
            question_label="general",
            project_id="proj123",
            question_id="q123",
        )
        assert dataset.answer_type == "text"
        assert dataset.cot == ""
        assert dataset.confirmed is False
        assert dataset.score == 0.0
    
    def test_dataset_invalid_score_high(self):
        """Test that score > 5.0 fails validation."""
        with pytest.raises(ValidationError):
            DatasetCreate(
                question="What is AI?",
                answer="AI is artificial intelligence",
                chunk_name="Chunk 1",
                chunk_content="Content about AI",
                model="gpt-4",
                question_label="general",
                project_id="proj123",
                question_id="q123",
                score=6.0,  # Invalid: > 5.0
            )
    
    def test_dataset_invalid_score_negative(self):
        """Test that negative score fails validation."""
        with pytest.raises(ValidationError):
            DatasetCreate(
                question="What is AI?",
                answer="AI is artificial intelligence",
                chunk_name="Chunk 1",
                chunk_content="Content about AI",
                model="gpt-4",
                question_label="general",
                project_id="proj123",
                question_id="q123",
                score=-1.0,  # Invalid: < 0.0
            )
    
    def test_dataset_update_partial(self):
        """Test partial dataset update."""
        update = DatasetUpdate(score=5.0, confirmed=True)
        assert update.score == 5.0
        assert update.confirmed is True
        assert update.question is None


class TestTaskSchemas:
    """Test task schemas."""
    
    def test_task_create_valid(self):
        """Test creating a valid task."""
        task = TaskCreate(
            task_type="question-generation",
            model_info='{"model": "gpt-4"}',
            language="en",
            project_id="proj123",
            status=TaskStatus.PROCESSING,
            total_count=100,
        )
        assert task.task_type == "question-generation"
        assert task.status == TaskStatus.PROCESSING
        assert task.total_count == 100
    
    def test_task_create_with_defaults(self):
        """Test task creation with default values."""
        task = TaskCreate(
            task_type="question-generation",
            model_info='{"model": "gpt-4"}',
            project_id="proj123",
        )
        assert task.language == "zh-CN"
        assert task.status == TaskStatus.PROCESSING
        assert task.total_count == 0
        assert task.detail == ""
        assert task.note == ""
    
    def test_task_status_enum(self):
        """Test task status enum values."""
        assert TaskStatus.PROCESSING == 0
        assert TaskStatus.COMPLETED == 1
        assert TaskStatus.FAILED == 2
        assert TaskStatus.INTERRUPTED == 3
    
    def test_task_type_constants(self):
        """Test task type constants."""
        assert TaskType.TEXT_PROCESSING == "text-processing"
        assert TaskType.QUESTION_GENERATION == "question-generation"
        assert TaskType.ANSWER_GENERATION == "answer-generation"
    
    def test_task_update_partial(self):
        """Test partial task update."""
        update = TaskUpdate(
            status=TaskStatus.COMPLETED,
            completed_count=100,
        )
        assert update.status == TaskStatus.COMPLETED
        assert update.completed_count == 100
        assert update.total_count is None
    
    def test_task_response_progress_percentage(self):
        """Test task response progress calculation."""
        data = {
            "id": "task123",
            "project_id": "proj123",
            "task_type": "question-generation",
            "status": 0,
            "start_time": datetime.now(),
            "completed_count": 50,
            "total_count": 100,
            "model_info": '{"model": "gpt-4"}',
            "language": "en",
            "detail": "",
            "note": "",
            "create_at": datetime.now(),
            "update_at": datetime.now(),
        }
        response = TaskResponse(**data)
        assert response.progress_percentage == 50.0
    
    def test_task_response_progress_zero_total(self):
        """Test progress calculation with zero total."""
        data = {
            "id": "task123",
            "project_id": "proj123",
            "task_type": "question-generation",
            "status": 0,
            "start_time": datetime.now(),
            "completed_count": 0,
            "total_count": 0,
            "model_info": '{"model": "gpt-4"}',
            "language": "en",
            "detail": "",
            "note": "",
            "create_at": datetime.now(),
            "update_at": datetime.now(),
        }
        response = TaskResponse(**data)
        assert response.progress_percentage == 0.0
    
    def test_task_response_status_properties(self):
        """Test task response status check properties."""
        data = {
            "id": "task123",
            "project_id": "proj123",
            "task_type": "question-generation",
            "status": TaskStatus.PROCESSING,
            "start_time": datetime.now(),
            "completed_count": 50,
            "total_count": 100,
            "model_info": '{"model": "gpt-4"}',
            "language": "en",
            "detail": "",
            "note": "",
            "create_at": datetime.now(),
            "update_at": datetime.now(),
        }
        response = TaskResponse(**data)
        assert response.is_running is True
        assert response.is_completed is False
        assert response.is_failed is False
        assert response.is_interrupted is False
        
        # Test completed status
        data["status"] = TaskStatus.COMPLETED
        response = TaskResponse(**data)
        assert response.is_running is False
        assert response.is_completed is True


class TestModelConfigSchemas:
    """Test model config schemas."""
    
    def test_config_create_valid(self):
        """Test creating a valid model config."""
        config = ModelConfigCreate(
            provider_id="openai",
            provider_name="OpenAI",
            endpoint="https://api.openai.com/v1",
            api_key="sk-test",
            model_id="gpt-4",
            model_name="GPT-4",
            type="chat",
            temperature=0.7,
            max_tokens=2048,
            top_p=1.0,
            top_k=0.0,
            project_id="proj123",
        )
        assert config.provider_name == "OpenAI"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
    
    def test_config_create_with_defaults(self):
        """Test config creation with default status."""
        config = ModelConfigCreate(
            provider_id="openai",
            provider_name="OpenAI",
            endpoint="https://api.openai.com/v1",
            api_key="sk-test",
            model_id="gpt-4",
            model_name="GPT-4",
            type="chat",
            temperature=0.7,
            max_tokens=2048,
            top_p=1.0,
            top_k=0.0,
            project_id="proj123",
        )
        assert config.status == 1
    
    def test_config_invalid_temperature_high(self):
        """Test that temperature > 2.0 fails validation."""
        with pytest.raises(ValidationError):
            ModelConfigCreate(
                provider_id="openai",
                provider_name="OpenAI",
                endpoint="https://api.openai.com/v1",
                api_key="sk-test",
                model_id="gpt-4",
                model_name="GPT-4",
                type="chat",
                temperature=3.0,  # Invalid: > 2.0
                max_tokens=2048,
                top_p=1.0,
                top_k=0.0,
                project_id="proj123",
            )
    
    def test_config_invalid_temperature_negative(self):
        """Test that negative temperature fails validation."""
        with pytest.raises(ValidationError):
            ModelConfigCreate(
                provider_id="openai",
                provider_name="OpenAI",
                endpoint="https://api.openai.com/v1",
                api_key="sk-test",
                model_id="gpt-4",
                model_name="GPT-4",
                type="chat",
                temperature=-0.1,  # Invalid: < 0.0
                max_tokens=2048,
                top_p=1.0,
                top_k=0.0,
                project_id="proj123",
            )
    
    def test_config_invalid_top_p(self):
        """Test that top_p > 1.0 fails validation."""
        with pytest.raises(ValidationError):
            ModelConfigCreate(
                provider_id="openai",
                provider_name="OpenAI",
                endpoint="https://api.openai.com/v1",
                api_key="sk-test",
                model_id="gpt-4",
                model_name="GPT-4",
                type="chat",
                temperature=0.7,
                max_tokens=2048,
                top_p=1.5,  # Invalid: > 1.0
                top_k=0.0,
                project_id="proj123",
            )
    
    def test_config_invalid_max_tokens(self):
        """Test that zero or negative max_tokens fails validation."""
        with pytest.raises(ValidationError):
            ModelConfigCreate(
                provider_id="openai",
                provider_name="OpenAI",
                endpoint="https://api.openai.com/v1",
                api_key="sk-test",
                model_id="gpt-4",
                model_name="GPT-4",
                type="chat",
                temperature=0.7,
                max_tokens=0,  # Invalid: must be > 0
                top_p=1.0,
                top_k=0.0,
                project_id="proj123",
            )
    
    def test_config_update_partial(self):
        """Test partial config update."""
        update = ModelConfigUpdate(temperature=0.8, max_tokens=4096)
        assert update.temperature == 0.8
        assert update.max_tokens == 4096
        assert update.provider_name is None
