"""Database connection and session management."""

import os
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from easy_dataset.database.base import Base

# Global engine and session factory cache
_engines: dict[str, Engine] = {}
_session_factories: dict[str, sessionmaker] = {}


def _enable_foreign_keys(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine(database_url: str | None = None) -> Engine:
    """Get or create the SQLAlchemy engine.
    
    Args:
        database_url: Database URL. If None, uses DATABASE_URL env var
                     or defaults to sqlite:///easy_dataset.db
    
    Returns:
        SQLAlchemy Engine instance
    """
    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///easy_dataset.db"
        )
    
    # Return cached engine if exists
    if database_url in _engines:
        return _engines[database_url]
    
    # Create engine with proper SQLite settings
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL query logging
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    )
    
    # Enable foreign keys for SQLite
    if database_url.startswith("sqlite"):
        event.listen(engine, "connect", _enable_foreign_keys)
    
    # Cache the engine
    _engines[database_url] = engine
    
    return engine


def get_session_factory(database_url: str | None = None) -> sessionmaker:
    """Get or create the session factory.
    
    Args:
        database_url: Database URL. If None, uses existing engine or creates new one
    
    Returns:
        SQLAlchemy sessionmaker instance
    """
    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///easy_dataset.db"
        )
    
    # Return cached session factory if exists
    if database_url in _session_factories:
        return _session_factories[database_url]
    
    engine = get_engine(database_url)
    session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    
    # Cache the session factory
    _session_factories[database_url] = session_factory
    
    return session_factory


def get_session(database_url: str | None = None) -> Generator[Session, None, None]:
    """Get a database session.
    
    This is a generator function that yields a session and ensures
    it's properly closed after use. Suitable for use with FastAPI Depends.
    
    Args:
        database_url: Database URL. If None, uses existing session factory
    
    Yields:
        SQLAlchemy Session instance
    
    Example:
        ```python
        from fastapi import Depends
        
        @app.get("/items")
        def get_items(db: Session = Depends(get_session)):
            return db.query(Item).all()
        ```
    """
    session_factory = get_session_factory(database_url)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def init_database(database_url: str | None = None, drop_all: bool = False) -> None:
    """Initialize the database by creating all tables.
    
    Args:
        database_url: Database URL. If None, uses existing engine or creates new one
        drop_all: If True, drops all existing tables before creating new ones
    
    Example:
        ```python
        from easy_dataset.database import init_database
        
        # Initialize database with default URL
        init_database()
        
        # Initialize with custom URL
        init_database("sqlite:///my_database.db")
        
        # Reset database (drop and recreate all tables)
        init_database(drop_all=True)
        ```
    """
    # Import all models to ensure they're registered with Base.metadata
    # This must be done before creating tables
    import easy_dataset.models  # noqa: F401
    
    engine = get_engine(database_url)
    
    if drop_all:
        Base.metadata.drop_all(bind=engine)
    
    Base.metadata.create_all(bind=engine)


def reset_engine(database_url: str | None = None) -> None:
    """Reset the engine and session factory for a specific database URL.
    
    This is useful for testing or when switching databases.
    
    Args:
        database_url: Database URL to reset. If None, resets all cached engines.
    """
    if database_url is None:
        # Reset all engines
        for engine in _engines.values():
            engine.dispose()
        _engines.clear()
        _session_factories.clear()
    else:
        # Reset specific engine
        if database_url in _engines:
            _engines[database_url].dispose()
            del _engines[database_url]
        if database_url in _session_factories:
            del _session_factories[database_url]
