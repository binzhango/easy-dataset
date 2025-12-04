"""Pydantic schemas for API validation."""

from easy_dataset.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from easy_dataset.schemas.file import (
    UploadFileBase,
    UploadFileCreate,
    UploadFileResponse,
)
from easy_dataset.schemas.chunk import (
    ChunkBase,
    ChunkCreate,
    ChunkUpdate,
    ChunkResponse,
)
from easy_dataset.schemas.question import (
    QuestionBase,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
)
from easy_dataset.schemas.dataset import (
    DatasetBase,
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
)
from easy_dataset.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatus,
    TaskType,
)
from easy_dataset.schemas.config import (
    ModelConfigBase,
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse,
)

__all__ = [
    # Project schemas
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    # File schemas
    "UploadFileBase",
    "UploadFileCreate",
    "UploadFileResponse",
    # Chunk schemas
    "ChunkBase",
    "ChunkCreate",
    "ChunkUpdate",
    "ChunkResponse",
    # Question schemas
    "QuestionBase",
    "QuestionCreate",
    "QuestionUpdate",
    "QuestionResponse",
    # Dataset schemas
    "DatasetBase",
    "DatasetCreate",
    "DatasetUpdate",
    "DatasetResponse",
    # Task schemas
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskStatus",
    "TaskType",
    # Config schemas
    "ModelConfigBase",
    "ModelConfigCreate",
    "ModelConfigUpdate",
    "ModelConfigResponse",
]
