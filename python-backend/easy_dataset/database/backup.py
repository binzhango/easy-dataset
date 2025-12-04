"""
Database backup and export utilities.

This module provides functionality for backing up and exporting
the SQLite database.
"""

import logging
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Database backup manager."""
    
    def __init__(self, database_url: str):
        """
        Initialize database backup manager.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.database_path = self._extract_database_path(database_url)
    
    def _extract_database_path(self, database_url: str) -> str:
        """
        Extract file path from SQLite database URL.
        
        Args:
            database_url: SQLAlchemy database URL
        
        Returns:
            Path to database file
        
        Raises:
            ValueError: If URL is not a SQLite URL
        """
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Only SQLite databases are supported for backup")
        
        # Remove sqlite:/// prefix
        path = database_url.replace("sqlite:///", "")
        
        # Handle relative paths
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        
        return path
    
    def backup(
        self,
        backup_path: Optional[str] = None,
        include_timestamp: bool = True
    ) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for backup file (optional)
            include_timestamp: Whether to include timestamp in filename
        
        Returns:
            Path to backup file
        
        Raises:
            FileNotFoundError: If database file doesn't exist
            IOError: If backup fails
        """
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database file not found: {self.database_path}")
        
        # Generate backup filename
        if backup_path is None:
            db_dir = os.path.dirname(self.database_path)
            db_name = os.path.basename(self.database_path)
            name, ext = os.path.splitext(db_name)
            
            if include_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{name}_backup_{timestamp}{ext}"
            else:
                backup_filename = f"{name}_backup{ext}"
            
            backup_path = os.path.join(db_dir, backup_filename)
        
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.dirname(backup_path)
            if backup_dir:
                os.makedirs(backup_dir, exist_ok=True)
            
            # Copy database file
            shutil.copy2(self.database_path, backup_path)
            
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            raise IOError(f"Failed to backup database: {e}")
    
    def backup_with_vacuum(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup with VACUUM to optimize and compact the database.
        
        This method creates a clean, optimized copy of the database.
        
        Args:
            backup_path: Path for backup file (optional)
        
        Returns:
            Path to backup file
        
        Raises:
            FileNotFoundError: If database file doesn't exist
            IOError: If backup fails
        """
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database file not found: {self.database_path}")
        
        # Generate backup filename
        if backup_path is None:
            db_dir = os.path.dirname(self.database_path)
            db_name = os.path.basename(self.database_path)
            name, ext = os.path.splitext(db_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name}_backup_vacuum_{timestamp}{ext}"
            backup_path = os.path.join(db_dir, backup_filename)
        
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.dirname(backup_path)
            if backup_dir:
                os.makedirs(backup_dir, exist_ok=True)
            
            # Connect to source database
            source_conn = sqlite3.connect(self.database_path)
            
            # Create backup database with VACUUM
            backup_conn = sqlite3.connect(backup_path)
            
            # Use backup API to copy database
            source_conn.backup(backup_conn)
            
            # VACUUM the backup to optimize
            backup_conn.execute("VACUUM")
            
            # Close connections
            backup_conn.close()
            source_conn.close()
            
            logger.info(f"Database backed up with VACUUM to: {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Failed to backup database with VACUUM: {e}")
            raise IOError(f"Failed to backup database with VACUUM: {e}")
    
    def export_sql(self, export_path: Optional[str] = None) -> str:
        """
        Export database as SQL dump.
        
        Args:
            export_path: Path for SQL dump file (optional)
        
        Returns:
            Path to SQL dump file
        
        Raises:
            FileNotFoundError: If database file doesn't exist
            IOError: If export fails
        """
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database file not found: {self.database_path}")
        
        # Generate export filename
        if export_path is None:
            db_dir = os.path.dirname(self.database_path)
            db_name = os.path.basename(self.database_path)
            name, _ = os.path.splitext(db_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"{name}_export_{timestamp}.sql"
            export_path = os.path.join(db_dir, export_filename)
        
        try:
            # Create export directory if it doesn't exist
            export_dir = os.path.dirname(export_path)
            if export_dir:
                os.makedirs(export_dir, exist_ok=True)
            
            # Connect to database
            conn = sqlite3.connect(self.database_path)
            
            # Export as SQL
            with open(export_path, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f"{line}\n")
            
            conn.close()
            
            logger.info(f"Database exported to SQL: {export_path}")
            return export_path
        
        except Exception as e:
            logger.error(f"Failed to export database to SQL: {e}")
            raise IOError(f"Failed to export database to SQL: {e}")
    
    def restore(self, backup_path: str, overwrite: bool = False) -> None:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            overwrite: Whether to overwrite existing database
        
        Raises:
            FileNotFoundError: If backup file doesn't exist
            FileExistsError: If database exists and overwrite is False
            IOError: If restore fails
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        if os.path.exists(self.database_path) and not overwrite:
            raise FileExistsError(
                f"Database already exists: {self.database_path}. "
                "Set overwrite=True to replace it."
            )
        
        try:
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(self.database_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
            # Copy backup to database location
            shutil.copy2(backup_path, self.database_path)
            
            logger.info(f"Database restored from: {backup_path}")
        
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            raise IOError(f"Failed to restore database: {e}")
    
    def get_database_size(self) -> int:
        """
        Get size of database file in bytes.
        
        Returns:
            Size in bytes
        
        Raises:
            FileNotFoundError: If database file doesn't exist
        """
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database file not found: {self.database_path}")
        
        return os.path.getsize(self.database_path)
    
    def get_database_info(self) -> dict:
        """
        Get information about the database.
        
        Returns:
            Dictionary with database information
        
        Raises:
            FileNotFoundError: If database file doesn't exist
        """
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database file not found: {self.database_path}")
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            )
            table_count = cursor.fetchone()[0]
            
            # Get table names and row counts
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = cursor.fetchall()
            
            table_info = {}
            total_rows = 0
            for (table_name,) in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                table_info[table_name] = row_count
                total_rows += row_count
            
            conn.close()
            
            return {
                "path": self.database_path,
                "size_bytes": self.get_database_size(),
                "size_mb": round(self.get_database_size() / (1024 * 1024), 2),
                "table_count": table_count,
                "total_rows": total_rows,
                "tables": table_info
            }
        
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            raise IOError(f"Failed to get database info: {e}")
    
    def list_backups(self, backup_dir: Optional[str] = None) -> list:
        """
        List available backup files.
        
        Args:
            backup_dir: Directory to search for backups (optional)
        
        Returns:
            List of backup file paths
        """
        if backup_dir is None:
            backup_dir = os.path.dirname(self.database_path)
        
        if not os.path.exists(backup_dir):
            return []
        
        # Find backup files
        db_name = os.path.basename(self.database_path)
        name, ext = os.path.splitext(db_name)
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith(f"{name}_backup") and filename.endswith(ext):
                backup_path = os.path.join(backup_dir, filename)
                backups.append({
                    "path": backup_path,
                    "filename": filename,
                    "size_bytes": os.path.getsize(backup_path),
                    "created": datetime.fromtimestamp(
                        os.path.getctime(backup_path)
                    ).isoformat()
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups


def create_backup(database_url: str, backup_path: Optional[str] = None) -> str:
    """
    Convenience function to create a database backup.
    
    Args:
        database_url: SQLAlchemy database URL
        backup_path: Path for backup file (optional)
    
    Returns:
        Path to backup file
    """
    backup_manager = DatabaseBackup(database_url)
    return backup_manager.backup(backup_path)


def create_optimized_backup(
    database_url: str,
    backup_path: Optional[str] = None
) -> str:
    """
    Convenience function to create an optimized database backup.
    
    Args:
        database_url: SQLAlchemy database URL
        backup_path: Path for backup file (optional)
    
    Returns:
        Path to backup file
    """
    backup_manager = DatabaseBackup(database_url)
    return backup_manager.backup_with_vacuum(backup_path)


def export_database_sql(
    database_url: str,
    export_path: Optional[str] = None
) -> str:
    """
    Convenience function to export database as SQL.
    
    Args:
        database_url: SQLAlchemy database URL
        export_path: Path for SQL dump file (optional)
    
    Returns:
        Path to SQL dump file
    """
    backup_manager = DatabaseBackup(database_url)
    return backup_manager.export_sql(export_path)


def get_database_info(database_url: str) -> dict:
    """
    Convenience function to get database information.
    
    Args:
        database_url: SQLAlchemy database URL
    
    Returns:
        Dictionary with database information
    """
    backup_manager = DatabaseBackup(database_url)
    return backup_manager.get_database_info()
