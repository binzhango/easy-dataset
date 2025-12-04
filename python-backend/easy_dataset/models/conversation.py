"""DatasetConversations model - Multi-turn dialogues."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects


class DatasetConversations(Base):
    """
    DatasetConversations model - Multi-turn dialogues.
    
    Stores multi-turn conversations for chat model training.
    Conversations are stored in ShareGPT format for compatibility.
    
    Attributes:
        id: Unique conversation identifier (nanoid)
        project_id: ID of the project this conversation belongs to
        question_id: ID of the initial question
        question: The initial question text
        chunk_id: ID of the source chunk
        model: Model used to generate the conversation
        question_label: Label/category of the initial question
        score: Quality score (0-5)
        ai_evaluation: AI evaluation conclusion
        tags: Comma-separated tags
        note: User notes
        scenario: Conversation scenario (teaching, consulting, discussion, etc.)
        role_a: Role A definition
        role_b: Role B definition
        turn_count: Actual number of turns in the conversation
        max_turns: Maximum turns configured for generation
        raw_messages: JSON string storing complete conversation in ShareGPT format
        confirmed: Whether this conversation has been confirmed by user
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this conversation belongs to
    """
    
    __tablename__ = "dataset_conversations"
    
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
    
    # Initial question and source
    question_id: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_id: Mapped[str] = mapped_column(String, nullable=False)
    
    # Model and metadata
    model: Mapped[str] = mapped_column(String, nullable=False)
    question_label: Mapped[str] = mapped_column(String, nullable=False)
    
    # Quality and confirmation
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ai_evaluation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tags: Mapped[str] = mapped_column(Text, default="", nullable=False)
    note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    
    # Conversation configuration
    scenario: Mapped[str] = mapped_column(String, nullable=False)
    role_a: Mapped[str] = mapped_column(String, nullable=False)
    role_b: Mapped[str] = mapped_column(String, nullable=False)
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False)
    max_turns: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Conversation content (ShareGPT format)
    raw_messages: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Confirmation
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
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
        back_populates="dataset_conversations"
    )
    
    def __repr__(self) -> str:
        return f"<DatasetConversations(id={self.id}, scenario={self.scenario}, turns={self.turn_count})>"
