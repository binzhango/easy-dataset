"""Test Pydantic schemas integration with SQLAlchemy models."""

import pytest
from datetime import datetime

from easy_dataset.models import (
    Projects,
    UploadFiles,
    Chunks,
    Questions,
    Datasets,
    Task,
    ModelConfig,
)
from easy_dataset.schemas import (
    ProjectResponse,
    UploadFileResponse,
    ChunkResponse,
    QuestionResponse,
    DatasetResponse,
    TaskResponse,
    ModelConfigResponse,
)


class TestProjectORMIntegration:
    """Test Projects model to Pydantic schema conversion."""
    
    def test_project_to_schema(self):
        """Test converting Projects model to ProjectResponse schema."""
        project = Projects(
            id="proj123",
            name="Test Project",
            description="Test Description",
            global_prompt="Global",
            question_prompt="Question",
            answer_prompt="Answer",
            label_prompt="Label",
            domain_tree_prompt="Domain",
            clean_prompt="Clean",
            test="test",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        project_response = ProjectResponse.model_validate(project)
        
        assert project_response.id == "proj123"
        assert project_response.name == "Test Project"
        assert project_response.description == "Test Description"
        assert project_response.global_prompt == "Global"
        assert isinstance(project_response.create_at, datetime)


class TestFileORMIntegration:
    """Test UploadFiles model to Pydantic schema conversion."""
    
    def test_upload_file_to_schema(self):
        """Test converting UploadFiles model to UploadFileResponse schema."""
        upload_file = UploadFiles(
            id="file123",
            project_id="proj123",
            file_name="test.pdf",
            file_ext=".pdf",
            path="/uploads/test.pdf",
            size=1024,
            md5="d41d8cd98f00b204e9800998ecf8427e",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        file_response = UploadFileResponse.model_validate(upload_file)
        
        assert file_response.id == "file123"
        assert file_response.file_name == "test.pdf"
        assert file_response.size == 1024
        assert file_response.md5 == "d41d8cd98f00b204e9800998ecf8427e"


class TestChunkORMIntegration:
    """Test Chunks model to Pydantic schema conversion."""
    
    def test_chunk_to_schema(self):
        """Test converting Chunks model to ChunkResponse schema."""
        chunk = Chunks(
            id="chunk123",
            project_id="proj123",
            file_id="file123",
            file_name="test.pdf",
            name="Chunk 1",
            content="Test content",
            summary="Summary",
            size=100,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        chunk_response = ChunkResponse.model_validate(chunk)
        
        assert chunk_response.id == "chunk123"
        assert chunk_response.name == "Chunk 1"
        assert chunk_response.content == "Test content"
        assert chunk_response.size == 100


class TestQuestionORMIntegration:
    """Test Questions model to Pydantic schema conversion."""
    
    def test_question_to_schema(self):
        """Test converting Questions model to QuestionResponse schema."""
        question = Questions(
            id="q123",
            project_id="proj123",
            chunk_id="chunk123",
            question="What is this?",
            label="general",
            answered=False,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        question_response = QuestionResponse.model_validate(question)
        
        assert question_response.id == "q123"
        assert question_response.question == "What is this?"
        assert question_response.label == "general"
        assert question_response.answered is False
    
    def test_question_with_image_to_schema(self):
        """Test converting Questions with image to schema."""
        question = Questions(
            id="q123",
            project_id="proj123",
            chunk_id="chunk123",
            question="What's in this image?",
            label="vision",
            answered=False,
            image_id="img123",
            image_name="test.jpg",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        question_response = QuestionResponse.model_validate(question)
        
        assert question_response.image_id == "img123"
        assert question_response.image_name == "test.jpg"


class TestDatasetORMIntegration:
    """Test Datasets model to Pydantic schema conversion."""
    
    def test_dataset_to_schema(self):
        """Test converting Datasets model to DatasetResponse schema."""
        dataset = Datasets(
            id="ds123",
            project_id="proj123",
            question_id="q123",
            question="What is AI?",
            answer="AI is artificial intelligence",
            answer_type="text",
            chunk_name="Chunk 1",
            chunk_content="Content",
            model="gpt-4",
            question_label="general",
            cot="",
            confirmed=False,
            score=4.5,
            ai_evaluation="",
            tags="",
            note="",
            other="",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        dataset_response = DatasetResponse.model_validate(dataset)
        
        assert dataset_response.id == "ds123"
        assert dataset_response.question == "What is AI?"
        assert dataset_response.answer == "AI is artificial intelligence"
        assert dataset_response.score == 4.5
        assert dataset_response.confirmed is False


class TestTaskORMIntegration:
    """Test Task model to Pydantic schema conversion."""
    
    def test_task_to_schema(self):
        """Test converting Task model to TaskResponse schema."""
        task = Task(
            id="task123",
            project_id="proj123",
            task_type="question-generation",
            status=0,
            start_time=datetime.now(),
            completed_count=50,
            total_count=100,
            model_info='{"model": "gpt-4"}',
            language="en",
            detail="",
            note="",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        task_response = TaskResponse.model_validate(task)
        
        assert task_response.id == "task123"
        assert task_response.task_type == "question-generation"
        assert task_response.status == 0
        assert task_response.completed_count == 50
        assert task_response.total_count == 100
    
    def test_task_computed_properties(self):
        """Test Task computed properties."""
        task = Task(
            id="task123",
            project_id="proj123",
            task_type="question-generation",
            status=0,
            start_time=datetime.now(),
            completed_count=50,
            total_count=100,
            model_info='{"model": "gpt-4"}',
            language="en",
            detail="",
            note="",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        task_response = TaskResponse.model_validate(task)
        
        # Test progress percentage
        assert task_response.progress_percentage == 50.0
        
        # Test status properties
        assert task_response.is_running is True
        assert task_response.is_completed is False
        assert task_response.is_failed is False
        assert task_response.is_interrupted is False
    
    def test_task_completed_status(self):
        """Test Task with completed status."""
        task = Task(
            id="task123",
            project_id="proj123",
            task_type="question-generation",
            status=1,  # COMPLETED
            start_time=datetime.now(),
            end_time=datetime.now(),
            completed_count=100,
            total_count=100,
            model_info='{"model": "gpt-4"}',
            language="en",
            detail="",
            note="",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        task_response = TaskResponse.model_validate(task)
        
        assert task_response.progress_percentage == 100.0
        assert task_response.is_running is False
        assert task_response.is_completed is True


class TestModelConfigORMIntegration:
    """Test ModelConfig model to Pydantic schema conversion."""
    
    def test_config_to_schema(self):
        """Test converting ModelConfig model to ModelConfigResponse schema."""
        config = ModelConfig(
            id="cfg123",
            project_id="proj123",
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
            status=1,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        config_response = ModelConfigResponse.model_validate(config)
        
        assert config_response.id == "cfg123"
        assert config_response.provider_name == "OpenAI"
        assert config_response.model_name == "GPT-4"
        assert config_response.temperature == 0.7
        assert config_response.max_tokens == 2048
        assert config_response.top_p == 1.0
        assert config_response.top_k == 0.0


class TestSchemaORMRoundTrip:
    """Test round-trip conversion between models and schemas."""
    
    def test_project_round_trip(self):
        """Test Projects model -> schema -> dict -> schema."""
        project = Projects(
            id="proj123",
            name="Test Project",
            description="Test Description",
            global_prompt="Global",
            question_prompt="Question",
            answer_prompt="Answer",
            label_prompt="Label",
            domain_tree_prompt="Domain",
            clean_prompt="Clean",
            test="test",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        # Model -> Schema
        schema1 = ProjectResponse.model_validate(project)
        
        # Schema -> Dict -> Schema
        schema2 = ProjectResponse(**schema1.model_dump())
        
        assert schema1.id == schema2.id
        assert schema1.name == schema2.name
        assert schema1.description == schema2.description
    
    def test_task_round_trip_with_properties(self):
        """Test Task round-trip preserves computed properties."""
        task = Task(
            id="task123",
            project_id="proj123",
            task_type="question-generation",
            status=0,
            start_time=datetime.now(),
            completed_count=75,
            total_count=100,
            model_info='{"model": "gpt-4"}',
            language="en",
            detail="",
            note="",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        
        # Model -> Schema
        schema1 = TaskResponse.model_validate(task)
        
        # Schema -> Dict -> Schema
        schema2 = TaskResponse(**schema1.model_dump())
        
        # Computed properties should work on both
        assert schema1.progress_percentage == schema2.progress_percentage
        assert schema1.is_running == schema2.is_running
        assert schema1.progress_percentage == 75.0
