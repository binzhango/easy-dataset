"""ModelConfig model - LLM provider settings."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects


class ModelConfig(Base):
    """
    ModelConfig model - LLM provider settings.
    
    Stores configuration for LLM providers including API keys,
    endpoints, and model parameters.
    
    Attributes:
        id: Unique configuration identifier (nanoid)
        project_id: ID of the project this configuration belongs to
        provider_id: ID of the LLM provider
        provider_name: Name of the LLM provider
        endpoint: API endpoint URL
        api_key: API key for authentication
        model_id: Model identifier
        model_name: Human-readable model name
        type: Configuration type
        temperature: Temperature parameter for generation
        max_tokens: Maximum tokens to generate
        top_p: Top-p sampling parameter
        top_k: Top-k sampling parameter
        status: Configuration status
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this configuration belongs to
    """
    
    __tablename__ = "model_config"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate
    )
    
    # Foreign key
    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Provider information
    provider_id: Mapped[str] = mapped_column(String, nullable=False)
    provider_name: Mapped[str] = mapped_column(String, nullable=False)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    api_key: Mapped[str] = mapped_column(String, nullable=False)
    
    # Model information
    model_id: Mapped[str] = mapped_column(String, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    
    # Generation parameters
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    top_p: Mapped[float] = mapped_column(Float, nullable=False)
    top_k: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Status
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    
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
    project: Mapped["Projects"] = relationship(
        "Projects",
        back_populates="model_config"
    )
    
    def __repr__(self) -> str:
        return f"<ModelConfig(id={self.id}, provider={self.provider_name}, model={self.model_name})>"
