"""
Tests for dataset API endpoints.

This module tests the dataset CRUD operations via the API.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from easy_dataset.database.base import Base
# Import all models to ensure they're registered with Base BEFORE creating tables
from easy_dataset.models import (
    Projects, Datasets, Chunks, Questions, UploadFiles, Tags,
    DatasetConversations, GaPairs, Images, ImageDatasets,
    LlmModels, LlmProviders, ModelConfig, CustomPrompts,
    QuestionTemplates, Task
)
from easy_dataset_server.app import app
from easy_dataset_server.dependencies import get_db


# Create test database - use file-based to avoid SQLite :memory: connection issues
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dataset_api.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables after models are imported
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency BEFORE creating test client
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Clean database before each test."""
    yield
    # Clean up all tables after each test using SQLAlchemy 2.0 syntax
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture(scope="module", autouse=True)
def cleanup_test_db():
    """Remove test database file after all tests."""
    yield
    import os
    if os.path.exists("./test_dataset_api.db"):
        os.remove("./test_dataset_api.db")


@pytest.fixture
def test_project():
    """Create a test project."""
    response = client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test Description",
        }
    )
    assert response.status_code == 201
    return response.json()


def test_create_dataset(test_project):
    """Test creating a dataset entry."""
    response = client.post(
        "/api/datasets",
        json={
            "project_id": test_project["id"],
            "question_id": "test_question_id",
            "question": "What is the capital of France?",
            "answer": "The capital of France is Paris.",
            "chunk_name": "Geography Chunk",
            "chunk_content": "France is a country in Europe. Its capital is Paris.",
            "model": "gpt-4",
            "question_label": "geography",
            "cot": "First, I identify the country. Then I recall its capital.",
            "confirmed": True,
            "score": 4.5,
            "tags": "geography,europe",
            "note": "Good quality answer",
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["question"] == "What is the capital of France?"
    assert data["answer"] == "The capital of France is Paris."
    assert data["project_id"] == test_project["id"]
    assert data["confirmed"] is True
    assert data["score"] == 4.5
    assert "id" in data
    assert "create_at" in data


def test_create_dataset_invalid_project():
    """Test creating a dataset with invalid project ID."""
    response = client.post(
        "/api/datasets",
        json={
            "project_id": "invalid_project_id",
            "question_id": "test_question_id",
            "question": "Test question?",
            "answer": "Test answer.",
            "chunk_name": "Test Chunk",
            "chunk_content": "Test content.",
            "model": "gpt-4",
            "question_label": "test",
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_datasets(test_project):
    """Test listing datasets."""
    # Create multiple dataset entries
    for i in range(3):
        client.post(
            "/api/datasets",
            json={
                "project_id": test_project["id"],
                "question_id": f"question_{i}",
                "question": f"Question {i}?",
                "answer": f"Answer {i}.",
                "chunk_name": f"Chunk {i}",
                "chunk_content": f"Content {i}.",
                "model": "gpt-4",
                "question_label": "test",
                "score": float(i),
            }
        )
    
    # List all datasets
    response = client.get("/api/datasets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_datasets_with_filters(test_project):
    """Test listing datasets with filters."""
    # Create dataset entries with different properties
    client.post(
        "/api/datasets",
        json={
            "project_id": test_project["id"],
            "question_id": "q1",
            "question": "Question 1?",
            "answer": "Answer 1.",
            "chunk_name": "Chunk 1",
            "chunk_content": "Content 1.",
            "model": "gpt-4",
            "question_label": "test",
            "confirmed": True,
            "score": 4.5,
            "tags": "geography,europe",
        }
    )
    
    client.post(
        "/api/datasets",
        json={
            "project_id": test_project["id"],
            "question_id": "q2",
            "question": "Question 2?",
            "answer": "Answer 2.",
            "chunk_name": "Chunk 2",
            "chunk_content": "Content 2.",
            "model": "gpt-4",
            "question_label": "test",
            "confirmed": False,
            "score": 2.0,
            "tags": "history",
        }
    )
    
    # Filter by confirmed status
    response = client.get("/api/datasets?confirmed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["confirmed"] is True
    
    # Filter by minimum score
    response = client.get("/api/datasets?min_score=4.0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["score"] >= 4.0
    
    # Filter by tags
    response = client.get("/api/datasets?tags=geography")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "geography" in data[0]["tags"]
    
    # Search in question/answer
    response = client.get("/api/datasets?search=Question 1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "Question 1" in data[0]["question"]


def test_get_dataset(test_project):
    """Test getting a specific dataset entry."""
    # Create a dataset entry
    create_response = client.post(
        "/api/datasets",
        json={
            "project_id": test_project["id"],
            "question_id": "test_question",
            "question": "Test question?",
            "answer": "Test answer.",
            "chunk_name": "Test Chunk",
            "chunk_content": "Test content.",
            "model": "gpt-4",
            "question_label": "test",
        }
    )
    dataset_id = create_response.json()["id"]
    
    # Get the dataset entry
    response = client.get(f"/api/datasets/{dataset_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dataset_id
    assert data["question"] == "Test question?"


def test_get_dataset_not_found():
    """Test getting a non-existent dataset entry."""
    response = client.get("/api/datasets/nonexistent_id")
    assert response.status_code == 404


def test_update_dataset(test_project):
    """Test updating a dataset entry."""
    # Create a dataset entry
    create_response = client.post(
        "/api/datasets",
        json={
            "project_id": test_project["id"],
            "question_id": "test_question",
            "question": "Original question?",
            "answer": "Original answer.",
            "chunk_name": "Test Chunk",
            "chunk_content": "Test content.",
            "model": "gpt-4",
            "question_label": "test",
            "score": 3.0,
        }
    )
    dataset_id = create_response.json()["id"]
    
    # Update the dataset entry
    response = client.put(
        f"/api/datasets/{dataset_id}",
        json={
            "question": "Updated question?",
            "answer": "Updated answer.",
            "score": 5.0,
            "confirmed": True,
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Updated question?"
    assert data["answer"] == "Updated answer."
    assert data["score"] == 5.0
    assert data["confirmed"] is True
    # Original fields should remain unchanged
    assert data["model"] == "gpt-4"


def test_update_dataset_not_found():
    """Test updating a non-existent dataset entry."""
    response = client.put(
        "/api/datasets/nonexistent_id",
        json={"question": "Updated question?"}
    )
    assert response.status_code == 404


def test_delete_dataset(test_project):
    """Test deleting a dataset entry."""
    # Create a dataset entry
    create_response = client.post(
        "/api/datasets",
        json={
            "project_id": test_project["id"],
            "question_id": "test_question",
            "question": "Test question?",
            "answer": "Test answer.",
            "chunk_name": "Test Chunk",
            "chunk_content": "Test content.",
            "model": "gpt-4",
            "question_label": "test",
        }
    )
    dataset_id = create_response.json()["id"]
    
    # Delete the dataset entry
    response = client.delete(f"/api/datasets/{dataset_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(f"/api/datasets/{dataset_id}")
    assert response.status_code == 404


def test_delete_dataset_not_found():
    """Test deleting a non-existent dataset entry."""
    response = client.delete("/api/datasets/nonexistent_id")
    assert response.status_code == 404


def test_dataset_pagination(test_project):
    """Test dataset pagination."""
    # Create 10 dataset entries
    for i in range(10):
        client.post(
            "/api/datasets",
            json={
                "project_id": test_project["id"],
                "question_id": f"question_{i}",
                "question": f"Question {i}?",
                "answer": f"Answer {i}.",
                "chunk_name": f"Chunk {i}",
                "chunk_content": f"Content {i}.",
                "model": "gpt-4",
                "question_label": "test",
            }
        )
    
    # Get first page
    response = client.get("/api/datasets?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    
    # Get second page
    response = client.get("/api/datasets?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
