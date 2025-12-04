"""Task model - Background job tracking."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects


class Task(Base):
    """
    Task model - Background job tracking.
    
    Tracks long-running background tasks like file processing,
    question generation, and answer generation.
    
    Task Status Values:
        0: Processing
        1: Completed
        2: Failed
        3: Interrupted/Canceled
    
    Task Types:
        - text-processing: File processing and chunking
        - question-generation: Question generation from chunks
        - answer-generation: Answer generation for questions
        - data-distillation: Data cleaning and refinement
        - dataset-evaluation: Dataset quality evaluation
        - multi-turn-generation: Multi-turn conversation generation
        - image-question-generation: Image question generation
        - image-dataset-generation: Image dataset generation
    
    Attributes:
        id: Unique task identifier (nanoid)
        project_id: ID of the project this task belongs to
        task_type: Type of task being performed
        status: Task status (0=processing, 1=completed, 2=failed, 3=interrupted)
        start_time: Task start timestamp
        end_time: Task end timestamp (None if still running)
        completed_count: Number of items completed
        total_count: Total number of items to process
        model_info: JSON string containing model information
        language: Language for generation (default: zh-CN)
        detail: Task details
        note: Task notes/error messages
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this task belongs to
    """
    
    __tablename__ = "task"
    
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
    
    # Task information
    task_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timing
    start_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Progress tracking
    completed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Configuration and metadata
    model_info: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String, default="zh-CN", nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="", nullable=False)
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
        back_populates="task"
    )
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.completed_count / self.total_count) * 100
    
    @property
    def is_running(self) -> bool:
        """Check if task is currently running."""
        return self.status == 0
    
    @property
    def is_completed(self) -> bool:
        """Check if task completed successfully."""
        return self.status == 1
    
    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == 2
    
    @property
    def is_interrupted(self) -> bool:
        """Check if task was interrupted/canceled."""
        return self.status == 3
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, type={self.task_type}, status={self.status})>"
