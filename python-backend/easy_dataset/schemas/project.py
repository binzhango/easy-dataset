"""Pydantic schemas for Projects."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    """Base schema for Project with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str = Field(..., description="Project description")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    
    global_prompt: str = Field(default="", description="Global prompt template")
    question_prompt: str = Field(default="", description="Question generation prompt")
    answer_prompt: str = Field(default="", description="Answer generation prompt")
    label_prompt: str = Field(default="", description="Label generation prompt")
    domain_tree_prompt: str = Field(default="", description="Domain tree prompt")
    clean_prompt: str = Field(default="", description="Data cleaning prompt")
    default_model_config_id: Optional[str] = Field(default=None, description="Default model config ID")


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    global_prompt: Optional[str] = Field(None, description="Global prompt template")
    question_prompt: Optional[str] = Field(None, description="Question generation prompt")
    answer_prompt: Optional[str] = Field(None, description="Answer generation prompt")
    label_prompt: Optional[str] = Field(None, description="Label generation prompt")
    domain_tree_prompt: Optional[str] = Field(None, description="Domain tree prompt")
    clean_prompt: Optional[str] = Field(None, description="Data cleaning prompt")
    default_model_config_id: Optional[str] = Field(None, description="Default model config ID")


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Project unique identifier")
    global_prompt: str = Field(..., description="Global prompt template")
    question_prompt: str = Field(..., description="Question generation prompt")
    answer_prompt: str = Field(..., description="Answer generation prompt")
    label_prompt: str = Field(..., description="Label generation prompt")
    domain_tree_prompt: str = Field(..., description="Domain tree prompt")
    clean_prompt: str = Field(..., description="Data cleaning prompt")
    default_model_config_id: Optional[str] = Field(None, description="Default model config ID")
    test: str = Field(..., description="Test field")
    create_at: datetime = Field(..., description="Creation timestamp")
    update_at: datetime = Field(..., description="Last update timestamp")
