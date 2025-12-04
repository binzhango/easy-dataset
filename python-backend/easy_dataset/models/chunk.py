"""Chunks model - Segmented text from documents."""

from datetime import datetime
from typing import TYPE_CHECKING, List

from nanoid import generate
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects
    from easy_dataset.models.question import Questions


class Chunks(Base):
    """
    Chunks model - Segmented text from documents.
    
    Stores text chunks created from processing uploaded documents.
    Each chunk represents a logical segment of text that can be used
    for question generation.
    
    Attributes:
        id: Unique chunk identifier (nanoid)
        name: Chunk name/title
        project_id: ID of the project this chunk belongs to
        file_id: ID of the source file
        file_name: Name of the source file
        content: The actual text content of the chunk
        summary: Optional summary of the chunk content
        size: Size of the chunk in characters
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this chunk belongs to
        questions: Questions generated from this chunk
    """
    
    __tablename__ = "chunks"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate
    )
    
    # Basic fields
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Foreign key
    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # File reference
    file_id: Mapped[str] = mapped_column(String, nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    
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
        back_populates="chunks"
    )
    
    questions: Mapped[List["Questions"]] = relationship(
        "Questions",
        back_populates="chunk",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Chunks(id={self.id}, name={self.name}, size={self.size})>"
