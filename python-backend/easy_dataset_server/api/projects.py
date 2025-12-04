"""
Project API endpoints.

This module provides REST API endpoints for project management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from easy_dataset.models import Projects
from easy_dataset.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from easy_dataset_server.dependencies import get_db

router = APIRouter()


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Create a new project.
    
    Args:
        project: Project creation data
        db: Database session
    
    Returns:
        Created project
    
    Raises:
        HTTPException: If project creation fails
    """
    try:
        # Create new project instance
        db_project = Projects(
            name=project.name,
            description=project.description,
            global_prompt=project.global_prompt or "",
            question_prompt=project.question_prompt or "",
            answer_prompt=project.answer_prompt or "",
            label_prompt=project.label_prompt or "",
            domain_tree_prompt=project.domain_tree_prompt or "",
            clean_prompt=project.clean_prompt or "",
            default_model_config_id=project.default_model_config_id,
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return ProjectResponse.model_validate(db_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}",
        )


@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
) -> List[ProjectResponse]:
    """
    List all projects with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of projects
    """
    projects = db.query(Projects).offset(skip).limit(limit).all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Get project details by ID.
    
    Args:
        project_id: Project ID
        db: Database session
    
    Returns:
        Project details
    
    Raises:
        HTTPException: If project not found
    """
    project = db.query(Projects).filter(Projects.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    return ProjectResponse.model_validate(project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Update project details.
    
    Args:
        project_id: Project ID
        project_update: Project update data
        db: Database session
    
    Returns:
        Updated project
    
    Raises:
        HTTPException: If project not found or update fails
    """
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    try:
        # Update only provided fields
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
        
        return ProjectResponse.model_validate(db_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}",
        )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a project.
    
    Args:
        project_id: Project ID
        db: Database session
    
    Raises:
        HTTPException: If project not found or deletion fails
    """
    db_project = db.query(Projects).filter(Projects.id == project_id).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    try:
        db.delete(db_project)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}",
        )

