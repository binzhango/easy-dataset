"""Images model - Uploaded images for vision tasks."""

from datetime import datetime
from typing import TYPE_CHECKING, List

from nanoid import generate
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects
    from easy_dataset.models.image_dataset import ImageDatasets


class Images(Base):
    """
    Images model - Uploaded images for vision tasks.
    
    Stores metadata about images uploaded for vision-language tasks.
    
    Attributes:
        id: Unique image identifier (nanoid)
        project_id: ID of the project this image belongs to
        image_name: Image file name
        path: Storage path for the image
        size: File size in bytes
        width: Image width in pixels (optional)
        height: Image height in pixels (optional)
        create_at: Upload timestamp
        update_at: Last update timestamp
    
    Relationships:
        project: The project this image belongs to
        image_datasets: Dataset entries using this image
    """
    
    __tablename__ = "images"
    
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
    
    # Image metadata
    image_name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
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
        back_populates="images"
    )
    
    image_datasets: Mapped[List["ImageDatasets"]] = relationship(
        "ImageDatasets",
        back_populates="image",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "image_name",
            name="uq_images_project_name"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Images(id={self.id}, image_name={self.image_name})>"
