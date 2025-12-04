"""
File upload API endpoints.

This module provides REST API endpoints for file upload and management.
"""

import hashlib
import os
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from easy_dataset.models import Projects, UploadFiles
from easy_dataset.schemas import UploadFileCreate, UploadFileResponse
from easy_dataset_server.config import settings
from easy_dataset_server.dependencies import get_db

router = APIRouter()


def calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        MD5 hash as hex string
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


@router.post("/files/upload", response_model=UploadFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    project_id: str = Form(..., description="Project ID"),
    file: UploadFile = File(..., description="File to upload"),
    db: Session = Depends(get_db),
) -> UploadFileResponse:
    """
    Upload a file to a project.
    
    Args:
        project_id: Project ID
        file: File to upload
        db: Database session
    
    Returns:
        Uploaded file metadata
    
    Raises:
        HTTPException: If project not found or upload fails
    """
    # Verify project exists
    project = db.query(Projects).filter(Projects.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size} bytes",
        )
    
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.upload_dir) / project_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Calculate MD5
        md5 = calculate_md5(str(file_path))
        
        # Create database record
        db_file = UploadFiles(
            project_id=project_id,
            file_name=file.filename,
            path=str(file_path),
            size=file_size,
            md5=md5,
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return UploadFileResponse.model_validate(db_file)
    except Exception as e:
        db.rollback()
        # Clean up file if database operation fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get("/files", response_model=List[UploadFileResponse])
def list_files(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> List[UploadFileResponse]:
    """
    List uploaded files with optional filtering.
    
    Args:
        project_id: Optional project ID filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of uploaded files
    """
    query = db.query(UploadFiles)
    
    if project_id:
        query = query.filter(UploadFiles.project_id == project_id)
    
    files = query.offset(skip).limit(limit).all()
    return [UploadFileResponse.model_validate(f) for f in files]


@router.get("/files/{file_id}", response_model=UploadFileResponse)
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
) -> UploadFileResponse:
    """
    Get file details by ID.
    
    Args:
        file_id: File ID
        db: Database session
    
    Returns:
        File details
    
    Raises:
        HTTPException: If file not found
    """
    file = db.query(UploadFiles).filter(UploadFiles.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found",
        )
    
    return UploadFileResponse.model_validate(file)


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete an uploaded file.
    
    Args:
        file_id: File ID
        db: Database session
    
    Raises:
        HTTPException: If file not found or deletion fails
    """
    db_file = db.query(UploadFiles).filter(UploadFiles.id == file_id).first()
    
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found",
        )
    
    try:
        # Delete physical file
        file_path = Path(db_file.path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete database record
        db.delete(db_file)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )

