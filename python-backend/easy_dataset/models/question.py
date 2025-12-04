"""Questions model - Generated questions from chunks."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects
    from easy_dataset.models.chunk import Chunks
    from easy_dataset.models.ga_pair import GaPairs


class Questions(Base):
    """
    Questions model - Generated questions from chunks.
    
    Stores questions generated from text chunks using LLM.
    Questions can be linked to chunks and optionally to genre-audience pairs.
    
    Attributes:
        id: Unique question identifier (nanoid)
        project_id: ID of the project this question belongs to
        chunk_id: ID of the source chunk
        ga_pair_id: Optional ID of the genre-audience pair that generated this
        question: The question text
        label: Question label/category
        answered: Whether this question has been answered
        image_id: Optional ID for image-based questions
        image_name: Optional name for image-based questions
        template_id: Optional ID linking to question template
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this question belongs to
        chunk: The source chunk for this question
        ga_pair: The genre-audience pair that generated this (if any)
    """
    
    __tablename__ = "questions"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate
    )
    
    # Foreign keys
    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    chunk_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("chunks.id"),
        nullable=False
    )
    
    ga_pair_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("ga_pairs.id"),
        nullable=True
    )
    
    # Question content
    question: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    answered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Optional image-related fields
    image_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    image_name: Mapped[str | None] = mapped_column(String, nullable=True)
    template_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    
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
        back_populates="questions"
    )
    
    chunk: Mapped["Chunks"] = relationship(
        "Chunks",
        back_populates="questions"
    )
    
    ga_pair: Mapped["GaPairs | None"] = relationship(
        "GaPairs",
        back_populates="questions"
    )
    
    def __repr__(self) -> str:
        return f"<Questions(id={self.id}, question={self.question[:50]}...)>"
