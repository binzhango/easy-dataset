"""Pydantic schemas for ModelConfig."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ModelConfigBase(BaseModel):
    """Base schema for ModelConfig with common fields."""
    
    provider_id: str = Field(..., description="ID of the LLM provider")
    provider_name: str = Field(..., description="Name of the LLM provider")
    endpoint: str = Field(..., description="API endpoint URL")
    api_key: str = Field(..., description="API key for authentication")
    model_id: str = Field(..., description="Model identifier")
    model_name: str = Field(..., description="Human-readable model name")
    type: str = Field(..., description="Configuration type")
    temperature: float = Field(..., ge=0.0, le=2.0, description="Temperature parameter for generation")
    max_tokens: int = Field(..., gt=0, description="Maximum tokens to generate")
    top_p: float = Field(..., ge=0.0, le=1.0, description="Top-p sampling parameter")
    top_k: float = Field(..., ge=0.0, description="Top-k sampling parameter")


class ModelConfigCreate(ModelConfigBase):
    """Schema for creating a new model configuration."""
    
    project_id: str = Field(..., description="ID of the project this configuration belongs to")
    status: int = Field(default=1, description="Configuration status")


class ModelConfigUpdate(BaseModel):
    """Schema for updating an existing model configuration."""
    
    provider_id: Optional[str] = Field(None, description="ID of the LLM provider")
    provider_name: Optional[str] = Field(None, description="Name of the LLM provider")
    endpoint: Optional[str] = Field(None, description="API endpoint URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    model_id: Optional[str] = Field(None, description="Model identifier")
    model_name: Optional[str] = Field(None, description="Human-readable model name")
    type: Optional[str] = Field(None, description="Configuration type")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature parameter")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling parameter")
    top_k: Optional[float] = Field(None, ge=0.0, description="Top-k sampling parameter")
    status: Optional[int] = Field(None, description="Configuration status")


class ModelConfigResponse(ModelConfigBase):
    """Schema for model configuration response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Configuration unique identifier")
    project_id: str = Field(..., description="ID of the project this configuration belongs to")
    status: int = Field(..., description="Configuration status")
    create_at: datetime = Field(..., description="Creation timestamp")
    update_at: datetime = Field(..., description="Last update timestamp")
