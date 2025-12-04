"""QuestionTemplates model - Reusable question templates."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects


class QuestionTemplates(Base):
    """
    QuestionTemplates model - Reusable question templates.
    
    Stores reusable question templates that can be applied to different
    data sources (images or text).
    
    Source Types:
        - image: Template for image-based questions
        - text: Template for text-based questions
    
    Answer Types:
        - text: Free-form text answer
        - label: Multiple choice with predefined labels
        - custom_format: Custom JSON format answer
    
    Attributes:
        id: Unique template identifier (nanoid)
        project_id: ID of the project this template belongs to
        question: Question template content
        source_type: Data source type (image, text)
        answer_type: Expected answer type (text, label, custom_format)
        description: Template description
        labels: JSON array of label options (for answer_type='label')
        custom_format: Custom format definition (for answer_type='custom_format')
        order: Display order
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this template belongs to
    """
    
    __tablename__ = "question_templates"
    
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
    
    # Template content
    question: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    answer_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    
    # Answer configuration
    labels: Mapped[str] = mapped_column(Text, default="", nullable=False)
    custom_format: Mapped[str] = mapped_column(Text, default="", nullable=False)
    
    # Display order
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
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
        back_populates="question_templates"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_question_templates_project_source", "project_id", "source_type"),
    )
    
    def __repr__(self) -> str:
        return f"<QuestionTemplates(id={self.id}, source_type={self.source_type}, answer_type={self.answer_type})>"
