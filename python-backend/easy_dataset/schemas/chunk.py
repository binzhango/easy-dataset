"""Pydantic schemas for Chunks."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ChunkBase(BaseModel):
    """Base schema for Chunk with common fields."""
    
    name: str = Field(..., min_length=1, description="Chunk name/title")
    content: str = Field(..., min_length=1, description="The actual text content of the chunk")
    summary: str = Field(default="", description="Optional summary of the chunk content")
    size: int = Field(..., gt=0, description="Size of the chunk in characters")


class ChunkCreate(ChunkBase):
    """Schema for creating a new chunk."""
    
    project_id: str = Field(..., description="ID of the project this chunk belongs to")
    file_id: str = Field(..., description="ID of the source file")
    file_name: str = Field(..., description="Name of the source file")


class ChunkUpdate(BaseModel):
    """Schema for updating an existing chunk."""
    
    name: Optional[str] = Field(None, min_length=1, description="Chunk name/title")
    content: Optional[str] = Field(None, min_length=1, description="The actual text content")
    summary: Optional[str] = Field(None, description="Optional summary of the chunk content")


class ChunkResponse(ChunkBase):
    """Schema for chunk response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Chunk unique identifier")
    project_id: str = Field(..., description="ID of the project this chunk belongs to")
    file_id: str = Field(..., description="ID of the source file")
    file_name: str = Field(..., description="Name of the source file")
    create_at: datetime = Field(..., description="Creation timestamp")
    update_at: datetime = Field(..., description="Last update timestamp")
