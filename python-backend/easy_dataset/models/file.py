"""UploadFiles model - Uploaded document metadata."""

from datetime import datetime
from typing import TYPE_CHECKING, List

from nanoid import generate
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects
    from easy_dataset.models.ga_pair import GaPairs


class UploadFiles(Base):
    """
    UploadFiles model - Uploaded document metadata.
    
    Stores metadata about files uploaded to a project, including file name,
    path, size, and MD5 hash for deduplication.
    
    Attributes:
        id: Unique file identifier (nanoid)
        project_id: ID of the project this file belongs to
        file_name: Original file name
        file_ext: File extension (e.g., 'pdf', 'docx')
        path: Storage path for the file
        size: File size in bytes
        md5: MD5 hash of file content (for deduplication)
        create_at: Upload timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this file belongs to
        ga_pairs: Genre-audience pairs generated from this file
    """
    
    __tablename__ = "upload_files"
    
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
    
    # File metadata
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_ext: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    md5: Mapped[str] = mapped_column(String, nullable=False)
    
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
        back_populates="upload_files"
    )
    
    ga_pairs: Mapped[List["GaPairs"]] = relationship(
        "GaPairs",
        back_populates="upload_file",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<UploadFiles(id={self.id}, file_name={self.file_name})>"
