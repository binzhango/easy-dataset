"""Pydantic schemas for Task."""

from datetime import datetime
from typing import Optional
from enum import IntEnum

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(IntEnum):
    """Task status enumeration."""
    
    PROCESSING = 0
    COMPLETED = 1
    FAILED = 2
    INTERRUPTED = 3


class TaskType(str):
    """Task type constants."""
    
    TEXT_PROCESSING = "text-processing"
    QUESTION_GENERATION = "question-generation"
    ANSWER_GENERATION = "answer-generation"
    DATA_DISTILLATION = "data-distillation"
    DATASET_EVALUATION = "dataset-evaluation"
    MULTI_TURN_GENERATION = "multi-turn-generation"
    IMAGE_QUESTION_GENERATION = "image-question-generation"
    IMAGE_DATASET_GENERATION = "image-dataset-generation"


class TaskBase(BaseModel):
    """Base schema for Task with common fields."""
    
    task_type: str = Field(..., description="Type of task being performed")
    model_info: str = Field(..., description="JSON string containing model information")
    language: str = Field(default="zh-CN", description="Language for generation")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    
    project_id: str = Field(..., description="ID of the project this task belongs to")
    status: int = Field(default=TaskStatus.PROCESSING, description="Task status")
    total_count: int = Field(default=0, ge=0, description="Total number of items to process")
    detail: str = Field(default="", description="Task details")
    note: str = Field(default="", description="Task notes/error messages")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    
    status: Optional[int] = Field(None, description="Task status")
    completed_count: Optional[int] = Field(None, ge=0, description="Number of items completed")
    total_count: Optional[int] = Field(None, ge=0, description="Total number of items to process")
    end_time: Optional[datetime] = Field(None, description="Task end timestamp")
    detail: Optional[str] = Field(None, description="Task details")
    note: Optional[str] = Field(None, description="Task notes/error messages")


class TaskResponse(TaskBase):
    """Schema for task response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Task unique identifier")
    project_id: str = Field(..., description="ID of the project this task belongs to")
    status: int = Field(..., description="Task status (0=processing, 1=completed, 2=failed, 3=interrupted)")
    start_time: datetime = Field(..., description="Task start timestamp")
    end_time: Optional[datetime] = Field(None, description="Task end timestamp")
    completed_count: int = Field(..., description="Number of items completed")
    total_count: int = Field(..., description="Total number of items to process")
    detail: str = Field(..., description="Task details")
    note: str = Field(..., description="Task notes/error messages")
    create_at: datetime = Field(..., description="Creation timestamp")
    update_at: datetime = Field(..., description="Last update timestamp")
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.completed_count / self.total_count) * 100
    
    @property
    def is_running(self) -> bool:
        """Check if task is currently running."""
        return self.status == TaskStatus.PROCESSING
    
    @property
    def is_completed(self) -> bool:
        """Check if task completed successfully."""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == TaskStatus.FAILED
    
    @property
    def is_interrupted(self) -> bool:
        """Check if task was interrupted/canceled."""
        return self.status == TaskStatus.INTERRUPTED
