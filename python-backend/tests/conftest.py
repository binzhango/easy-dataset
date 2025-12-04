"""
Pytest configuration and fixtures.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
from typing import Generator


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


# Additional fixtures will be added as needed in later tasks
