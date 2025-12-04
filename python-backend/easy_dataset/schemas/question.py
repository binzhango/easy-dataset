"""Pydantic schemas for Questions."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class QuestionBase(BaseModel):
    """Base schema for Question with common fields."""
    
    question: str = Field(..., min_length=1, description="The question text")
    label: str = Field(..., description="Question label/category")


class QuestionCreate(QuestionBase):
    """Schema for creating a new question."""
    
    project_id: str = Field(..., description="ID of the project this question belongs to")
    chunk_id: str = Field(..., description="ID of the source chunk")
    ga_pair_id: Optional[str] = Field(default=None, description="Optional genre-audience pair ID")
    answered: bool = Field(default=False, description="Whether this question has been answered")
    image_id: Optional[str] = Field(default=None, description="Optional image ID for image-based questions")
    image_name: Optional[str] = Field(default=None, description="Optional image name")
    template_id: Optional[str] = Field(default=None, description="Optional question template ID")


class QuestionUpdate(BaseModel):
    """Schema for updating an existing question."""
    
    question: Optional[str] = Field(None, min_length=1, description="The question text")
    label: Optional[str] = Field(None, description="Question label/category")
    answered: Optional[bool] = Field(None, description="Whether this question has been answered")
    image_id: Optional[str] = Field(None, description="Optional image ID")
    image_name: Optional[str] = Field(None, description="Optional image name")
    template_id: Optional[str] = Field(None, description="Optional question template ID")


class QuestionResponse(QuestionBase):
    """Schema for question response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Question unique identifier")
    project_id: str = Field(..., description="ID of the project this question belongs to")
    chunk_id: str = Field(..., description="ID of the source chunk")
    ga_pair_id: Optional[str] = Field(None, description="Optional genre-audience pair ID")
    answered: bool = Field(..., description="Whether this question has been answered")
    image_id: Optional[str] = Field(None, description="Optional image ID")
    image_name: Optional[str] = Field(None, description="Optional image name")
    template_id: Optional[str] = Field(None, description="Optional question template ID")
    create_at: datetime = Field(..., description="Creation timestamp")
    update_at: datetime = Field(..., description="Last update timestamp")
