"""
Chunk API endpoints.

This module provides REST API endpoints for chunk management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from easy_dataset.models import Chunks, Projects
from easy_dataset.schemas import ChunkCreate, ChunkResponse, ChunkUpdate
from easy_dataset_server.dependencies import get_db

router = APIRouter()


@router.post("/chunks", response_model=ChunkResponse, status_code=status.HTTP_201_CREATED)
def create_chunk(
    chunk: ChunkCreate,
    db: Session = Depends(get_db),
) -> ChunkResponse:
    """
    Create a new chunk.
    
    Args:
        chunk: Chunk creation data
        db: Database session
    
    Returns:
        Created chunk
    
    Raises:
        HTTPException: If project not found or chunk creation fails
    """
    # Verify project exists
    project = db.query(Projects).filter(Projects.id == chunk.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {chunk.project_id} not found",
        )
    
    try:
        db_chunk = Chunks(
            project_id=chunk.project_id,
            file_id=chunk.file_id,
            content=chunk.content,
            summary=chunk.summary or "",
            size=chunk.size or len(chunk.content),
            index=chunk.index,
            tag_id=chunk.tag_id,
        )
        
        db.add(db_chunk)
        db.commit()
        db.refresh(db_chunk)
        
        return ChunkResponse.model_validate(db_chunk)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chunk: {str(e)}",
        )


@router.get("/chunks", response_model=List[ChunkResponse])
def list_chunks(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    file_id: Optional[str] = Query(None, description="Filter by file ID"),
    tag_id: Optional[str] = Query(None, description="Filter by tag ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> List[ChunkResponse]:
    """
    List chunks with optional filtering.
    
    Args:
        project_id: Optional project ID filter
        file_id: Optional file ID filter
        tag_id: Optional tag ID filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of chunks
    """
    query = db.query(Chunks)
    
    if project_id:
        query = query.filter(Chunks.project_id == project_id)
    if file_id:
        query = query.filter(Chunks.file_id == file_id)
    if tag_id:
        query = query.filter(Chunks.tag_id == tag_id)
    
    chunks = query.offset(skip).limit(limit).all()
    return [ChunkResponse.model_validate(c) for c in chunks]


@router.get("/chunks/{chunk_id}", response_model=ChunkResponse)
def get_chunk(
    chunk_id: str,
    db: Session = Depends(get_db),
) -> ChunkResponse:
    """
    Get chunk details by ID.
    
    Args:
        chunk_id: Chunk ID
        db: Database session
    
    Returns:
        Chunk details
    
    Raises:
        HTTPException: If chunk not found
    """
    chunk = db.query(Chunks).filter(Chunks.id == chunk_id).first()
    
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with id {chunk_id} not found",
        )
    
    return ChunkResponse.model_validate(chunk)


@router.put("/chunks/{chunk_id}", response_model=ChunkResponse)
def update_chunk(
    chunk_id: str,
    chunk_update: ChunkUpdate,
    db: Session = Depends(get_db),
) -> ChunkResponse:
    """
    Update chunk details.
    
    Args:
        chunk_id: Chunk ID
        chunk_update: Chunk update data
        db: Database session
    
    Returns:
        Updated chunk
    
    Raises:
        HTTPException: If chunk not found or update fails
    """
    db_chunk = db.query(Chunks).filter(Chunks.id == chunk_id).first()
    
    if not db_chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with id {chunk_id} not found",
        )
    
    try:
        # Update only provided fields
        update_data = chunk_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chunk, field, value)
        
        # Update size if content changed
        if "content" in update_data:
            db_chunk.size = len(db_chunk.content)
        
        db.commit()
        db.refresh(db_chunk)
        
        return ChunkResponse.model_validate(db_chunk)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chunk: {str(e)}",
        )


@router.delete("/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chunk(
    chunk_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a chunk.
    
    Args:
        chunk_id: Chunk ID
        db: Database session
    
    Raises:
        HTTPException: If chunk not found or deletion fails
    """
    db_chunk = db.query(Chunks).filter(Chunks.id == chunk_id).first()
    
    if not db_chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with id {chunk_id} not found",
        )
    
    try:
        db.delete(db_chunk)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chunk: {str(e)}",
        )

