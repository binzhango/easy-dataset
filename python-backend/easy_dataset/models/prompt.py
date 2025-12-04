"""CustomPrompts model - User-defined prompts."""

from datetime import datetime
from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects


class CustomPrompts(Base):
    """
    CustomPrompts model - User-defined prompts.
    
    Allows users to customize prompts for different generation tasks
    and languages.
    
    Prompt Types:
        - question: Question generation prompts
        - answer: Answer generation prompts
        - label: Label generation prompts
        - dataClean: Data cleaning prompts
        - datasetEvaluation: Dataset evaluation prompts
        - distillQuestions: Question distillation prompts
        - distillTags: Tag distillation prompts
        - enhancedAnswer: Enhanced answer generation prompts
        - ga-generation: Genre-audience generation prompts
        - imageAnswer: Image answer generation prompts
        - imageQuestion: Image question generation prompts
        - labelRevise: Label revision prompts
        - multiTurnConversation: Multi-turn conversation prompts
        - newAnswer: New answer generation prompts
        - optimizeCot: Chain-of-thought optimization prompts
    
    Attributes:
        id: Unique prompt identifier (nanoid)
        project_id: ID of the project this prompt belongs to
        prompt_type: Type of prompt (corresponds to lib/llm/prompts files)
        prompt_key: Key name in the prompt module (e.g., QUESTION_PROMPT, QUESTION_PROMPT_EN)
        language: Language code (zh-CN, en, tr)
        content: Custom prompt content
        is_active: Whether this prompt is currently active
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this prompt belongs to
    """
    
    __tablename__ = "custom_prompts"
    
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
    
    # Prompt identification
    prompt_type: Mapped[str] = mapped_column(String, nullable=False)
    prompt_key: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    
    # Prompt content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
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
        back_populates="custom_prompts"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "prompt_type",
            "prompt_key",
            "language",
            name="uq_custom_prompts_project_type_key_lang"
        ),
        Index("idx_custom_prompts_project_type", "project_id", "prompt_type"),
        Index("idx_custom_prompts_project_lang", "project_id", "language"),
    )
    
    def __repr__(self) -> str:
        return f"<CustomPrompts(id={self.id}, type={self.prompt_type}, key={self.prompt_key}, lang={self.language})>"
