"""ImageDatasets model - Image QA pairs."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects
    from easy_dataset.models.image import Images


class ImageDatasets(Base):
    """
    ImageDatasets model - Image QA pairs.
    
    Stores question-answer pairs for images, supporting multiple answer types
    including text, labels, and custom formats.
    
    Answer Types:
        - text: Free-form text answer
        - label: JSON array of label selections
        - custom_format: Custom JSON format answer
    
    Attributes:
        id: Unique dataset entry identifier (nanoid)
        project_id: ID of the project this entry belongs to
        image_id: ID of the source image
        image_name: Name of the source image
        question_id: Optional ID linking to Questions table
        question: The question text
        answer: The answer (format depends on answer_type)
        answer_type: Type of answer (text, label, custom_format)
        model: Model used to generate the answer
        confirmed: Whether this entry has been confirmed by user
        score: Quality score (0-5)
        tags: Comma-separated tags
        note: User notes
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this dataset entry belongs to
        image: The source image for this entry
    """
    
    __tablename__ = "image_datasets"
    
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
    
    image_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("images.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Image reference
    image_name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Question reference (optional)
    question_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    
    # Question and answer
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[str] = mapped_column(String, default="text", nullable=False)
    
    # Model and metadata
    model: Mapped[str] = mapped_column(String, nullable=False)
    
    # Quality and confirmation
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Tags and notes
    tags: Mapped[str] = mapped_column(Text, default="", nullable=False)
    note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    
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
        back_populates="image_datasets"
    )
    
    image: Mapped["Images"] = relationship(
        "Images",
        back_populates="image_datasets"
    )
    
    def __repr__(self) -> str:
        return f"<ImageDatasets(id={self.id}, image_name={self.image_name}, question={self.question[:30]}...)>"
