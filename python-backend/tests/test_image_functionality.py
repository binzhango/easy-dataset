"""Basic tests for image dataset functionality."""

import io
import json
import pytest
from pathlib import Path
from PIL import Image as PILImage

from easy_dataset.models.image import Images
from easy_dataset.models.image_dataset import ImageDatasets
from easy_dataset.models.project import Projects
from easy_dataset.services.image_service import ImageService
from easy_dataset.services.image_dataset_service import ImageDatasetService


@pytest.fixture
def test_project(db_session):
    """Create a test project."""
    project = Projects(
        name="Test Project",
        description="Test project for image functionality"
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_image_data():
    """Create test image data."""
    # Create a simple test image
    img = PILImage.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def image_service(db_session, tmp_path):
    """Create image service with temp storage."""
    return ImageService(db_session, storage_path=str(tmp_path / "images"))


@pytest.fixture
def dataset_service(db_session):
    """Create image dataset service."""
    return ImageDatasetService(db_session)


class TestImageService:
    """Test image service functionality."""
    
    def test_validate_image_format(self, image_service):
        """Test image format validation."""
        assert image_service.validate_image_format("test.jpg") is True
        assert image_service.validate_image_format("test.jpeg") is True
        assert image_service.validate_image_format("test.png") is True
        assert image_service.validate_image_format("test.webp") is True
        assert image_service.validate_image_format("test.gif") is False
        assert image_service.validate_image_format("test.bmp") is False
    
    def test_validate_image_size(self, image_service):
        """Test image size validation."""
        assert image_service.validate_image_size(1024) is True
        assert image_service.validate_image_size(50 * 1024 * 1024) is True
        assert image_service.validate_image_size(100 * 1024 * 1024) is True
        assert image_service.validate_image_size(101 * 1024 * 1024) is False
    
    def test_extract_image_dimensions(self, image_service, test_image_data):
        """Test image dimension extraction."""
        width, height = image_service.extract_image_dimensions(test_image_data)
        assert width == 100
        assert height == 100
    
    @pytest.mark.asyncio
    async def test_upload_image(self, image_service, test_project, test_image_data):
        """Test image upload."""
        image = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        assert image is not None
        assert image.project_id == test_project.id
        assert image.image_name == "test.jpg"
        assert image.width == 100
        assert image.height == 100
        assert image.size > 0
    
    @pytest.mark.asyncio
    async def test_upload_invalid_format(self, image_service, test_project):
        """Test upload with invalid format."""
        invalid_data = io.BytesIO(b"not an image")
        
        with pytest.raises(ValueError, match="Unsupported image format"):
            await image_service.upload_image(
                project_id=test_project.id,
                image_name="test.txt",
                image_data=invalid_data
            )
    
    @pytest.mark.asyncio
    async def test_get_image(self, image_service, test_project, test_image_data):
        """Test getting image by ID."""
        uploaded = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        retrieved = image_service.get_image(uploaded.id)
        assert retrieved is not None
        assert retrieved.id == uploaded.id
        assert retrieved.image_name == "test.jpg"
    
    @pytest.mark.asyncio
    async def test_list_images(self, image_service, test_project, test_image_data):
        """Test listing images."""
        # Upload multiple images
        for i in range(3):
            test_image_data.seek(0)
            await image_service.upload_image(
                project_id=test_project.id,
                image_name=f"test{i}.jpg",
                image_data=test_image_data
            )
        
        images = image_service.list_images(test_project.id)
        assert len(images) == 3
    
    @pytest.mark.asyncio
    async def test_delete_image(self, image_service, test_project, test_image_data):
        """Test deleting image."""
        uploaded = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        result = image_service.delete_image(uploaded.id)
        assert result is True
        
        # Verify deleted
        retrieved = image_service.get_image(uploaded.id)
        assert retrieved is None


class TestImageDatasetService:
    """Test image dataset service functionality."""
    
    @pytest.mark.asyncio
    async def test_create_dataset_entry(
        self,
        dataset_service,
        image_service,
        test_project,
        test_image_data
    ):
        """Test creating dataset entry."""
        # Upload image first
        image = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        # Create dataset entry
        entry = dataset_service.create_dataset_entry(
            project_id=test_project.id,
            image_id=image.id,
            question="What is in this image?",
            answer="A red square",
            model="gpt-4o",
            answer_type="text"
        )
        
        assert entry is not None
        assert entry.project_id == test_project.id
        assert entry.image_id == image.id
        assert entry.question == "What is in this image?"
        assert entry.answer == "A red square"
        assert entry.answer_type == "text"
    
    def test_validate_answer_type(self, dataset_service):
        """Test answer type validation."""
        assert dataset_service.validate_answer_type("text") is True
        assert dataset_service.validate_answer_type("label") is True
        assert dataset_service.validate_answer_type("custom_format") is True
        assert dataset_service.validate_answer_type("invalid") is False
    
    def test_format_label_answer(self, dataset_service):
        """Test label answer formatting."""
        labels = ["cat", "animal", "pet"]
        formatted = dataset_service.format_label_answer(labels)
        
        assert isinstance(formatted, str)
        parsed = json.loads(formatted)
        assert parsed == labels
    
    def test_parse_label_answer(self, dataset_service):
        """Test label answer parsing."""
        json_str = '["cat", "animal", "pet"]'
        labels = dataset_service.parse_label_answer(json_str)
        
        assert labels == ["cat", "animal", "pet"]
    
    @pytest.mark.asyncio
    async def test_list_dataset_entries(
        self,
        dataset_service,
        image_service,
        test_project,
        test_image_data
    ):
        """Test listing dataset entries."""
        # Upload image
        image = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        # Create multiple entries
        for i in range(3):
            dataset_service.create_dataset_entry(
                project_id=test_project.id,
                image_id=image.id,
                question=f"Question {i}?",
                answer=f"Answer {i}",
                model="gpt-4o"
            )
        
        entries = dataset_service.list_dataset_entries(test_project.id)
        assert len(entries) == 3
    
    @pytest.mark.asyncio
    async def test_update_dataset_entry(
        self,
        dataset_service,
        image_service,
        test_project,
        test_image_data
    ):
        """Test updating dataset entry."""
        # Create entry
        image = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        entry = dataset_service.create_dataset_entry(
            project_id=test_project.id,
            image_id=image.id,
            question="Original question?",
            answer="Original answer",
            model="gpt-4o"
        )
        
        # Update entry
        updated = dataset_service.update_dataset_entry(
            entry.id,
            answer="Updated answer",
            score=4.5
        )
        
        assert updated is not None
        assert updated.answer == "Updated answer"
        assert updated.score == 4.5
    
    @pytest.mark.asyncio
    async def test_confirm_entry(
        self,
        dataset_service,
        image_service,
        test_project,
        test_image_data
    ):
        """Test confirming dataset entry."""
        image = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        entry = dataset_service.create_dataset_entry(
            project_id=test_project.id,
            image_id=image.id,
            question="Question?",
            answer="Answer",
            model="gpt-4o"
        )
        
        assert entry.confirmed is False
        
        confirmed = dataset_service.confirm_entry(entry.id, True)
        assert confirmed.confirmed is True
    
    @pytest.mark.asyncio
    async def test_rate_entry(
        self,
        dataset_service,
        image_service,
        test_project,
        test_image_data
    ):
        """Test rating dataset entry."""
        image = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        entry = dataset_service.create_dataset_entry(
            project_id=test_project.id,
            image_id=image.id,
            question="Question?",
            answer="Answer",
            model="gpt-4o"
        )
        
        rated = dataset_service.rate_entry(entry.id, 4.5)
        assert rated.score == 4.5
        
        # Test invalid score
        with pytest.raises(ValueError, match="Score must be between 0 and 5"):
            dataset_service.rate_entry(entry.id, 6.0)
    
    @pytest.mark.asyncio
    async def test_get_dataset_stats(
        self,
        dataset_service,
        image_service,
        test_project,
        test_image_data
    ):
        """Test getting dataset statistics."""
        image = await image_service.upload_image(
            project_id=test_project.id,
            image_name="test.jpg",
            image_data=test_image_data
        )
        
        # Create entries with different properties
        dataset_service.create_dataset_entry(
            project_id=test_project.id,
            image_id=image.id,
            question="Q1?",
            answer="A1",
            model="gpt-4o",
            confirmed=True,
            score=4.0
        )
        
        dataset_service.create_dataset_entry(
            project_id=test_project.id,
            image_id=image.id,
            question="Q2?",
            answer="A2",
            model="gpt-4o",
            answer_type="label",
            score=5.0
        )
        
        stats = dataset_service.get_dataset_stats(test_project.id)
        
        assert stats["total_entries"] == 2
        assert stats["confirmed_entries"] == 1
        assert stats["unconfirmed_entries"] == 1
        assert stats["average_score"] == 4.5
        assert stats["by_answer_type"]["text"] == 1
        assert stats["by_answer_type"]["label"] == 1
        assert stats["unique_images"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
