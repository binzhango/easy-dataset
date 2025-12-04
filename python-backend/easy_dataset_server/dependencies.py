"""
FastAPI dependencies.

This module provides dependency injection functions for FastAPI routes.
"""

from typing import Generator

from sqlalchemy.orm import Session

from easy_dataset.database.connection import get_session


def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency.
    
    This function is used with FastAPI's Depends to inject
    database sessions into route handlers.
    
    Yields:
        SQLAlchemy Session instance
    
    Example:
        ```python
        from fastapi import Depends
        from sqlalchemy.orm import Session
        
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    yield from get_session()

