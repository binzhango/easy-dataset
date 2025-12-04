"""Projects model - Container for all user work."""

from datetime import datetime
from typing import List

from nanoid import generate
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base


class Projects(Base):
    """
    Projects model - Container for all user work.
    
    A project contains all related documents, chunks, questions, and datasets.
    It allows users to organize their work and maintain separate configurations
    for different use cases.
    
    Attributes:
        id: Unique project identifier (12-character nanoid)
        name: Project name
        description: Project description
        global_prompt: Global prompt template for all generations
        question_prompt: Prompt template for question generation
        answer_prompt: Prompt template for answer generation
        label_prompt: Prompt template for label generation
        domain_tree_prompt: Prompt template for domain tree generation
        clean_prompt: Prompt template for data cleaning
        default_model_config_id: Default LLM model configuration ID
        test: Test field (for future use)
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        questions: Questions generated in this project
        datasets: Dataset entries in this project
        dataset_conversations: Multi-turn conversations in this project
        chunks: Text chunks in this project
        model_config: LLM model configurations for this project
        upload_files: Files uploaded to this project
        tags: Tags used in this project
        task: Background tasks for this project
        ga_pairs: Genre-audience pairs for this project
        custom_prompts: Custom prompts for this project
        images: Images uploaded to this project
        image_datasets: Image datasets in this project
        question_templates: Question templates for this project
    """
    
    __tablename__ = "projects"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(12),
        primary_key=True,
        default=lambda: generate(size=12)
    )
    
    # Basic fields
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Prompt templates
    global_prompt: Mapped[str] = mapped_column(Text, default="")
    question_prompt: Mapped[str] = mapped_column(Text, default="")
    answer_prompt: Mapped[str] = mapped_column(Text, default="")
    label_prompt: Mapped[str] = mapped_column(Text, default="")
    domain_tree_prompt: Mapped[str] = mapped_column(Text, default="")
    clean_prompt: Mapped[str] = mapped_column(Text, default="")
    
    # Configuration
    default_model_config_id: Mapped[str | None] = mapped_column(String, nullable=True)
    test: Mapped[str] = mapped_column(String, default="")
    
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
    
    # Relationships (will be populated as we create other models)
    # Note: Using string references to avoid circular imports
    chunks: Mapped[List["Chunks"]] = relationship(
        "Chunks",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    upload_files: Mapped[List["UploadFiles"]] = relationship(
        "UploadFiles",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    tags: Mapped[List["Tags"]] = relationship(
        "Tags",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    questions: Mapped[List["Questions"]] = relationship(
        "Questions",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    datasets: Mapped[List["Datasets"]] = relationship(
        "Datasets",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    dataset_conversations: Mapped[List["DatasetConversations"]] = relationship(
        "DatasetConversations",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    task: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    model_config: Mapped[List["ModelConfig"]] = relationship(
        "ModelConfig",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    custom_prompts: Mapped[List["CustomPrompts"]] = relationship(
        "CustomPrompts",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    images: Mapped[List["Images"]] = relationship(
        "Images",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    image_datasets: Mapped[List["ImageDatasets"]] = relationship(
        "ImageDatasets",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    question_templates: Mapped[List["QuestionTemplates"]] = relationship(
        "QuestionTemplates",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    ga_pairs: Mapped[List["GaPairs"]] = relationship(
        "GaPairs",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Projects(id={self.id}, name={self.name})>"
