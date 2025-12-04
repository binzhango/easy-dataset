"""
Database backup API endpoints.

This module provides REST API endpoints for database backup and export.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from easy_dataset.database.backup import (
    DatabaseBackup,
    create_backup,
    create_optimized_backup,
    export_database_sql,
    get_database_info,
)
from easy_dataset_server.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class BackupResponse(BaseModel):
    """Backup operation response."""
    
    success: bool
    message: str
    backup_path: str
    size_bytes: int


class DatabaseInfoResponse(BaseModel):
    """Database information response."""
    
    path: str
    size_bytes: int
    size_mb: float
    table_count: int
    total_rows: int
    tables: Dict[str, int]


class BackupListItem(BaseModel):
    """Backup list item."""
    
    path: str
    filename: str
    size_bytes: int
    created: str


@router.post("/backup", response_model=BackupResponse)
async def create_database_backup(
    optimized: bool = Query(False, description="Create optimized backup with VACUUM")
) -> BackupResponse:
    """
    Create a database backup.
    
    Args:
        optimized: Whether to create optimized backup with VACUUM
    
    Returns:
        Backup operation result
    
    Raises:
        HTTPException: If backup fails
    """
    try:
        if optimized:
            backup_path = create_optimized_backup(settings.database_url)
        else:
            backup_path = create_backup(settings.database_url)
        
        # Get backup file size
        import os
        size_bytes = os.path.getsize(backup_path)
        
        return BackupResponse(
            success=True,
            message="Database backup created successfully",
            backup_path=backup_path,
            size_bytes=size_bytes
        )
    
    except Exception as e:
        logger.error(f"Failed to create backup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create backup: {str(e)}"
        )


@router.post("/backup/export-sql", response_model=BackupResponse)
async def export_database_to_sql() -> BackupResponse:
    """
    Export database as SQL dump.
    
    Returns:
        Export operation result
    
    Raises:
        HTTPException: If export fails
    """
    try:
        export_path = export_database_sql(settings.database_url)
        
        # Get export file size
        import os
        size_bytes = os.path.getsize(export_path)
        
        return BackupResponse(
            success=True,
            message="Database exported to SQL successfully",
            backup_path=export_path,
            size_bytes=size_bytes
        )
    
    except Exception as e:
        logger.error(f"Failed to export database: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export database: {str(e)}"
        )


@router.get("/backup/info", response_model=DatabaseInfoResponse)
async def get_database_information() -> DatabaseInfoResponse:
    """
    Get database information.
    
    Returns:
        Database information
    
    Raises:
        HTTPException: If operation fails
    """
    try:
        info = get_database_info(settings.database_url)
        return DatabaseInfoResponse(**info)
    
    except Exception as e:
        logger.error(f"Failed to get database info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database info: {str(e)}"
        )


@router.get("/backup/list", response_model=List[BackupListItem])
async def list_database_backups() -> List[BackupListItem]:
    """
    List available database backups.
    
    Returns:
        List of backup files
    
    Raises:
        HTTPException: If operation fails
    """
    try:
        backup_manager = DatabaseBackup(settings.database_url)
        backups = backup_manager.list_backups()
        return [BackupListItem(**backup) for backup in backups]
    
    except Exception as e:
        logger.error(f"Failed to list backups: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list backups: {str(e)}"
        )


@router.get("/backup/download/{filename}")
async def download_backup(filename: str):
    """
    Download a backup file.
    
    Args:
        filename: Backup filename
    
    Returns:
        Backup file
    
    Raises:
        HTTPException: If file not found or download fails
    """
    try:
        backup_manager = DatabaseBackup(settings.database_url)
        backups = backup_manager.list_backups()
        
        # Find backup by filename
        backup = next((b for b in backups if b["filename"] == filename), None)
        
        if not backup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backup file not found: {filename}"
            )
        
        return FileResponse(
            path=backup["path"],
            filename=filename,
            media_type="application/octet-stream"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download backup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download backup: {str(e)}"
        )


@router.post("/backup/restore")
async def restore_database_backup(
    backup_path: str = Query(..., description="Path to backup file"),
    overwrite: bool = Query(False, description="Overwrite existing database")
) -> Dict[str, Any]:
    """
    Restore database from backup.
    
    WARNING: This will replace the current database!
    
    Args:
        backup_path: Path to backup file
        overwrite: Whether to overwrite existing database
    
    Returns:
        Restore operation result
    
    Raises:
        HTTPException: If restore fails
    """
    try:
        backup_manager = DatabaseBackup(settings.database_url)
        backup_manager.restore(backup_path, overwrite=overwrite)
        
        return {
            "success": True,
            "message": "Database restored successfully",
            "backup_path": backup_path
        }
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except FileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to restore backup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore backup: {str(e)}"
        )
