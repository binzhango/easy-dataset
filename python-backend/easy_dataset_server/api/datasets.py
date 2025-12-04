"""
Dataset API endpoints.

This module provides REST API endpoints for dataset management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from easy_dataset.models import Datasets, Projects
from easy_dataset.schemas import DatasetCreate, DatasetResponse, DatasetUpdate
from easy_dataset_server.dependencies import get_db

router = APIRouter()


@router.post("/datasets", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db),
) -> DatasetResponse:
    """
    Create a new dataset entry.
    
    Args:
        dataset: Dataset creation data
        db: Database session
    
    Returns:
        Created dataset entry
    
    Raises:
        HTTPException: If project not found or dataset creation fails
    """
    # Verify project exists
    project = db.query(Projects).filter(Projects.id == dataset.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {dataset.project_id} not found",
        )
    
    try:
        db_dataset = Datasets(
            project_id=dataset.project_id,
            question_id=dataset.question_id,
            question=dataset.question,
            answer=dataset.answer,
            answer_type=dataset.answer_type,
            chunk_name=dataset.chunk_name,
            chunk_content=dataset.chunk_content,
            model=dataset.model,
            question_label=dataset.question_label,
            cot=dataset.cot,
            confirmed=dataset.confirmed,
            score=dataset.score,
            ai_evaluation=dataset.ai_evaluation,
            tags=dataset.tags,
            note=dataset.note,
            other=dataset.other,
        )
        
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        
        return DatasetResponse.model_validate(db_dataset)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dataset entry: {str(e)}",
        )


@router.get("/datasets", response_model=List[DatasetResponse])
def list_datasets(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    confirmed: Optional[bool] = Query(None, description="Filter by confirmed status"),
    min_score: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum score filter"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    search: Optional[str] = Query(None, description="Search in question or answer text"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> List[DatasetResponse]:
    """
    List datasets with optional filtering.
    
    Supports filtering by:
    - project_id: Filter by project
    - confirmed: Filter by confirmation status
    - min_score: Filter by minimum quality score
    - tags: Filter by tags (matches if any tag in the filter is present)
    - search: Search in question or answer text
    
    Args:
        project_id: Optional project ID filter
        confirmed: Optional confirmed status filter
        min_score: Optional minimum score filter
        tags: Optional tags filter (comma-separated)
        search: Optional search text
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of dataset entries
    """
    query = db.query(Datasets)
    
    # Apply filters
    if project_id:
        query = query.filter(Datasets.project_id == project_id)
    
    if confirmed is not None:
        query = query.filter(Datasets.confirmed == confirmed)
    
    if min_score is not None:
        query = query.filter(Datasets.score >= min_score)
    
    if tags:
        # Filter by tags - match if any of the provided tags are present
        tag_list = [tag.strip() for tag in tags.split(",")]
        # Use OR condition to match any tag
        tag_filters = [Datasets.tags.contains(tag) for tag in tag_list]
        if tag_filters:
            from sqlalchemy import or_
            query = query.filter(or_(*tag_filters))
    
    if search:
        # Search in question or answer text
        from sqlalchemy import or_
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Datasets.question.ilike(search_pattern),
                Datasets.answer.ilike(search_pattern)
            )
        )
    
    # Apply pagination
    datasets = query.offset(skip).limit(limit).all()
    return [DatasetResponse.model_validate(d) for d in datasets]


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
) -> DatasetResponse:
    """
    Get dataset entry details by ID.
    
    Args:
        dataset_id: Dataset entry ID
        db: Database session
    
    Returns:
        Dataset entry details
    
    Raises:
        HTTPException: If dataset entry not found
    """
    dataset = db.query(Datasets).filter(Datasets.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset entry with id {dataset_id} not found",
        )
    
    return DatasetResponse.model_validate(dataset)


@router.put("/datasets/{dataset_id}", response_model=DatasetResponse)
def update_dataset(
    dataset_id: str,
    dataset_update: DatasetUpdate,
    db: Session = Depends(get_db),
) -> DatasetResponse:
    """
    Update dataset entry details.
    
    Args:
        dataset_id: Dataset entry ID
        dataset_update: Dataset update data
        db: Database session
    
    Returns:
        Updated dataset entry
    
    Raises:
        HTTPException: If dataset entry not found or update fails
    """
    db_dataset = db.query(Datasets).filter(Datasets.id == dataset_id).first()
    
    if not db_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset entry with id {dataset_id} not found",
        )
    
    try:
        # Update only provided fields
        update_data = dataset_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dataset, field, value)
        
        db.commit()
        db.refresh(db_dataset)
        
        return DatasetResponse.model_validate(db_dataset)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dataset entry: {str(e)}",
        )


@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a dataset entry.
    
    This operation only deletes the dataset entry itself. The source question
    and chunk remain unaffected in the database (Property 20: Dataset entry
    deletion isolation).
    
    Args:
        dataset_id: Dataset entry ID
        db: Database session
    
    Raises:
        HTTPException: If dataset entry not found or deletion fails
    """
    db_dataset = db.query(Datasets).filter(Datasets.id == dataset_id).first()
    
    if not db_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset entry with id {dataset_id} not found",
        )
    
    try:
        db.delete(db_dataset)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataset entry: {str(e)}",
        )
