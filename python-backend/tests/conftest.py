"""
Pytest configuration and fixtures.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from easy_dataset.database.base import Base
# Import all models to ensure they're registered with Base
from easy_dataset.models import (
    Projects, Datasets, Chunks, Questions, UploadFiles, Tags,
    DatasetConversations, GaPairs, Images, ImageDatasets,
    LlmModels, LlmProviders, ModelConfig, CustomPrompts,
    QuestionTemplates, Task
)


@pytest.fixture
def sample_project_data() -> dict:
    """Provide sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for unit tests",
    }


@pytest.fixture
def sample_chunk_data() -> dict:
    """Provide sample chunk data for testing."""
    return {
        "content": "This is a sample text chunk for testing purposes.",
        "size": 50,
    }


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    return engine


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create a session factory for tests."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session(test_engine, test_session_factory) -> Generator:
    """Create a test database session."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = test_session_factory()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


# Additional fixtures will be added as needed in later tasks
