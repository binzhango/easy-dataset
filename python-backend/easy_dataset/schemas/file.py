"""Pydantic schemas for UploadFiles."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UploadFileBase(BaseModel):
    """Base schema for UploadFile with common fields."""
    
    file_name: str = Field(..., min_length=1, description="Original file name")
    file_ext: str = Field(..., description="File extension")
    path: str = Field(..., description="Storage path for the file")
    size: int = Field(..., gt=0, description="File size in bytes")
    md5: str = Field(..., min_length=32, max_length=32, description="MD5 hash of file content")


class UploadFileCreate(UploadFileBase):
    """Schema for creating a new upload file record."""
    
    project_id: str = Field(..., description="ID of the project this file belongs to")


class UploadFileResponse(UploadFileBase):
    """Schema for upload file response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="File unique identifier")
    project_id: str = Field(..., description="ID of the project this file belongs to")
    create_at: datetime = Field(..., description="Upload timestamp")
    update_at: datetime = Field(..., description="Last update timestamp")
