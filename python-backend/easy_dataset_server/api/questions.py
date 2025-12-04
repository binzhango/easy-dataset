"""
Question API endpoints.

This module provides REST API endpoints for question management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from easy_dataset.models import Chunks, Projects, Questions
from easy_dataset.schemas import QuestionCreate, QuestionResponse, QuestionUpdate
from easy_dataset_server.dependencies import get_db

router = APIRouter()


@router.post("/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    """
    Create a new question.
    
    Args:
        question: Question creation data
        db: Database session
    
    Returns:
        Created question
    
    Raises:
        HTTPException: If project or chunk not found or question creation fails
    """
    # Verify project exists
    project = db.query(Projects).filter(Projects.id == question.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {question.project_id} not found",
        )
    
    # Verify chunk exists if provided
    if question.chunk_id:
        chunk = db.query(Chunks).filter(Chunks.id == question.chunk_id).first()
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk with id {question.chunk_id} not found",
            )
    
    try:
        db_question = Questions(
            project_id=question.project_id,
            chunk_id=question.chunk_id,
            question=question.question,
            label=question.label or "",
            answered=question.answered or False,
            ga_pair_id=question.ga_pair_id,
        )
        
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        return QuestionResponse.model_validate(db_question)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create question: {str(e)}",
        )


@router.get("/questions", response_model=List[QuestionResponse])
def list_questions(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    chunk_id: Optional[str] = Query(None, description="Filter by chunk ID"),
    answered: Optional[bool] = Query(None, description="Filter by answered status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> List[QuestionResponse]:
    """
    List questions with optional filtering.
    
    Args:
        project_id: Optional project ID filter
        chunk_id: Optional chunk ID filter
        answered: Optional answered status filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of questions
    """
    query = db.query(Questions)
    
    if project_id:
        query = query.filter(Questions.project_id == project_id)
    if chunk_id:
        query = query.filter(Questions.chunk_id == chunk_id)
    if answered is not None:
        query = query.filter(Questions.answered == answered)
    
    questions = query.offset(skip).limit(limit).all()
    return [QuestionResponse.model_validate(q) for q in questions]


@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: str,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    """
    Get question details by ID.
    
    Args:
        question_id: Question ID
        db: Database session
    
    Returns:
        Question details
    
    Raises:
        HTTPException: If question not found
    """
    question = db.query(Questions).filter(Questions.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found",
        )
    
    return QuestionResponse.model_validate(question)


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: str,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    """
    Update question details.
    
    Args:
        question_id: Question ID
        question_update: Question update data
        db: Database session
    
    Returns:
        Updated question
    
    Raises:
        HTTPException: If question not found or update fails
    """
    db_question = db.query(Questions).filter(Questions.id == question_id).first()
    
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found",
        )
    
    try:
        # Update only provided fields
        update_data = question_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_question, field, value)
        
        db.commit()
        db.refresh(db_question)
        
        return QuestionResponse.model_validate(db_question)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update question: {str(e)}",
        )


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a question.
    
    Args:
        question_id: Question ID
        db: Database session
    
    Raises:
        HTTPException: If question not found or deletion fails
    """
    db_question = db.query(Questions).filter(Questions.id == question_id).first()
    
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found",
        )
    
    try:
        db.delete(db_question)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete question: {str(e)}",
        )

