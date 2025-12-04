"""Pydantic schemas for Datasets."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class DatasetBase(BaseModel):
    """Base schema for Dataset with common fields."""
    
    question: str = Field(..., min_length=1, description="The question text")
    answer: str = Field(..., min_length=1, description="The answer text")
    chunk_name: str = Field(..., description="Name of the source chunk")
    chunk_content: str = Field(..., description="Content of the source chunk")
    model: str = Field(..., description="Model used to generate the answer")
    question_label: str = Field(..., description="Label/category of the question")


class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset entry."""
    
    project_id: str = Field(..., description="ID of the project this entry belongs to")
    question_id: str = Field(..., description="ID of the source question")
    answer_type: str = Field(default="text", description="Type of answer (text, label, custom_format)")
    cot: str = Field(default="", description="Chain-of-thought reasoning")
    confirmed: bool = Field(default=False, description="Whether this entry has been confirmed by user")
    score: float = Field(default=0.0, ge=0.0, le=5.0, description="Quality score (0-5)")
    ai_evaluation: str = Field(default="", description="AI evaluation conclusion")
    tags: str = Field(default="", description="Comma-separated tags")
    note: str = Field(default="", description="User notes")
    other: str = Field(default="", description="JSON string for additional fields")


class DatasetUpdate(BaseModel):
    """Schema for updating an existing dataset entry."""
    
    question: Optional[str] = Field(None, min_length=1, description="The question text")
    answer: Optional[str] = Field(None, min_length=1, description="The answer text")
    answer_type: Optional[str] = Field(None, description="Type of answer")
    chunk_name: Optional[str] = Field(None, description="Name of the source chunk")
    chunk_content: Optional[str] = Field(None, description="Content of the source chunk")
    model: Optional[str] = Field(None, description="Model used to generate the answer")
    question_label: Optional[str] = Field(None, description="Label/category of the question")
    cot: Optional[str] = Field(None, description="Chain-of-thought reasoning")
    confirmed: Optional[bool] = Field(None, description="Whether this entry has been confirmed")
    score: Optional[float] = Field(None, ge=0.0, le=5.0, description="Quality score (0-5)")
    ai_evaluation: Optional[str] = Field(None, description="AI evaluation conclusion")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    note: Optional[str] = Field(None, description="User notes")
    other: Optional[str] = Field(None, description="JSON string for additional fields")


class DatasetResponse(DatasetBase):
    """Schema for dataset response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Dataset entry unique identifier")
    project_id: str = Field(..., description="ID of the project this entry belongs to")
    question_id: str = Field(..., description="ID of the source question")
    answer_type: str = Field(..., description="Type of answer")
    cot: str = Field(..., description="Chain-of-thought reasoning")
    confirmed: bool = Field(..., description="Whether this entry has been confirmed by user")
    score: float = Field(..., description="Quality score (0-5)")
    ai_evaluation: str = Field(..., description="AI evaluation conclusion")
    tags: str = Field(..., description="Comma-separated tags")
    note: str = Field(..., description="User notes")
    other: str = Field(..., description="JSON string for additional fields")
    create_at: datetime = Field(..., description="Creation timestamp")
    update_at: datetime = Field(..., description="Last update timestamp")
