"""Datasets model - Question-answer pairs for training."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects


class Datasets(Base):
    """
    Datasets model - Question-answer pairs for training.
    
    Stores complete question-answer pairs ready for export and use in
    LLM fine-tuning. Includes metadata like ratings, tags, and AI evaluations.
    
    Attributes:
        id: Unique dataset entry identifier (nanoid)
        project_id: ID of the project this entry belongs to
        question_id: ID of the source question
        question: The question text
        answer: The answer text
        answer_type: Type of answer (text, label, custom_format)
        chunk_name: Name of the source chunk
        chunk_content: Content of the source chunk
        model: Model used to generate the answer
        question_label: Label/category of the question
        cot: Chain-of-thought reasoning (if any)
        confirmed: Whether this entry has been confirmed by user
        score: Quality score (0-5)
        ai_evaluation: AI evaluation conclusion
        tags: Comma-separated tags
        note: User notes
        other: JSON string for additional fields
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this dataset entry belongs to
    """
    
    __tablename__ = "datasets"
    
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
        nullable=False,
        index=True
    )
    
    # Question and answer
    question_id: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[str] = mapped_column(String, default="text", nullable=True)
    
    # Source chunk information
    chunk_name: Mapped[str] = mapped_column(String, nullable=False)
    chunk_content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Model and metadata
    model: Mapped[str] = mapped_column(String, nullable=False)
    question_label: Mapped[str] = mapped_column(String, nullable=False)
    cot: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Quality and confirmation
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ai_evaluation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    
    # Tags and notes
    tags: Mapped[str] = mapped_column(Text, default="", nullable=False)
    note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    other: Mapped[str] = mapped_column(Text, default="", nullable=False)
    
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
        back_populates="datasets"
    )
    
    def __repr__(self) -> str:
        return f"<Datasets(id={self.id}, question={self.question[:30]}...)>"
