"""GaPairs model - Genre-audience pairs for content generation."""

from datetime import datetime
from typing import TYPE_CHECKING, List

from nanoid import generate
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects
    from easy_dataset.models.file import UploadFiles
    from easy_dataset.models.question import Questions


class GaPairs(Base):
    """
    GaPairs model - Genre-audience pairs for content generation.
    
    Stores genre-audience pairs that can be used to generate targeted
    questions and content. Each file can have up to 5 pairs.
    
    Attributes:
        id: Unique pair identifier (nanoid)
        project_id: ID of the project this pair belongs to
        file_id: ID of the source file
        pair_number: Pair number (1-5) for this file
        genre_title: Genre name/title
        genre_desc: Genre description
        audience_title: Audience name/title
        audience_desc: Audience description
        is_active: Whether this pair is active for use
        create_at: Creation timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this pair belongs to
        upload_file: The source file for this pair
        questions: Questions generated using this pair
    """
    
    __tablename__ = "ga_pairs"
    
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
    
    file_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("upload_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Pair identification
    pair_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Genre information
    genre_title: Mapped[str] = mapped_column(String, nullable=False)
    genre_desc: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Audience information
    audience_title: Mapped[str] = mapped_column(String, nullable=False)
    audience_desc: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status
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
        back_populates="ga_pairs"
    )
    
    upload_file: Mapped["UploadFiles"] = relationship(
        "UploadFiles",
        back_populates="ga_pairs"
    )
    
    questions: Mapped[List["Questions"]] = relationship(
        "Questions",
        back_populates="ga_pair"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "file_id",
            "pair_number",
            name="uq_ga_pairs_file_number"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<GaPairs(id={self.id}, genre={self.genre_title}, audience={self.audience_title})>"
