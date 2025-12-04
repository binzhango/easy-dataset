"""Tags model - Hierarchical tagging system."""

from typing import TYPE_CHECKING, List

from nanoid import generate
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from easy_dataset.database.base import Base

if TYPE_CHECKING:
    from easy_dataset.models.project import Projects


class Tags(Base):
    """
    Tags model - Hierarchical tagging system.
    
    Supports hierarchical tags with parent-child relationships,
    allowing for organized categorization of content.
    
    Attributes:
        id: Unique tag identifier (nanoid)
        label: Tag label/name
        project_id: ID of the project this tag belongs to
        parent_id: ID of the parent tag (None for root tags)
    
    Relationships:
        project: The project this tag belongs to
        parent: The parent tag (if any)
        children: Child tags under this tag
    """
    
    __tablename__ = "tags"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate
    )
    
    # Basic fields
    label: Mapped[str] = mapped_column(String, nullable=False)
    
    # Foreign keys
    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    parent_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("tags.id"),
        nullable=True
    )
    
    # Relationships
    project: Mapped["Projects"] = relationship(
        "Projects",
        back_populates="tags"
    )
    
    # Self-referential relationship for hierarchy
    parent: Mapped["Tags | None"] = relationship(
        "Tags",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id]
    )
    
    children: Mapped[List["Tags"]] = relationship(
        "Tags",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    
    def __repr__(self) -> str:
        return f"<Tags(id={self.id}, label={self.label}, parent_id={self.parent_id})>"
