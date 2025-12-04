"""Base model class for all SQLAlchemy models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models.
    
    All models should inherit from this class to be part of the
    SQLAlchemy declarative system.
    """
    pass
