"""LLM provider and model definitions."""

from datetime import datetime
from typing import List, TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    pass


class LlmProviders(Base):
    """
    LlmProviders model - LLM provider definitions.
    
    Stores information about available LLM providers.
    
    Attributes:
        id: Provider identifier (e.g., 'openai', 'ollama')
        name: Provider display name
        api_url: Default API URL for the provider
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        llm_models: Models available from this provider
    """
    
    __tablename__ = "llm_providers"
    
    # Primary key (not auto-generated, uses provider name)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Provider information
    name: Mapped[str] = mapped_column(String, nullable=False)
    api_url: Mapped[str] = mapped_column(String, nullable=False)
    
    # Timestamps
    create_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    update_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    llm_models: Mapped[List["LlmModels"]] = relationship(
        "LlmModels",
        back_populates="provider",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<LlmProviders(id={self.id}, name={self.name})>"


class LlmModels(Base):
    """
    LlmModels model - Available LLM models.
    
    Stores information about specific models available from providers.
    
    Attributes:
        id: Unique model record identifier (nanoid)
        model_id: Model identifier used in API calls
        model_name: Human-readable model name
        provider_id: ID of the provider offering this model
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        provider: The provider offering this model
    """
    
    __tablename__ = "llm_models"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate
    )
    
    # Model information
    model_id: Mapped[str] = mapped_column(String, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Foreign key
    provider_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("llm_providers.id"),
        nullable=False
    )
    
    # Timestamps
    create_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    update_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    provider: Mapped["LlmProviders"] = relationship(
        "LlmProviders",
        back_populates="llm_models"
    )
    
    def __repr__(self) -> str:
        return f"<LlmModels(id={self.id}, model_id={self.model_id}, model_name={self.model_name})>"
