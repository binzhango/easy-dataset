"""
Project API endpoints.

This module provides REST API endpoints for project management.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from easy_dataset.models import Projects
from easy_dataset.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from easy_dataset.utils.query import (
    PaginationParams,
    SortParams,
    build_query,
    create_paginated_response,
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


@router.get("/projects")
def list_projects(
    limit: int = Query(50, ge=1, le=1000, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    search: Optional[str] = Query(None, description="Search term"),
    name: Optional[str] = Query(None, description="Filter by name"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    List all projects with pagination, filtering, and sorting.
    
    Args:
        limit: Number of items per page
        offset: Number of items to skip
        sort_by: Field to sort by (name, create_at, update_at)
        sort_order: Sort order (asc or desc)
        search: Search term (searches in name and description)
        name: Filter by exact name match
        db: Database session
    
    Returns:
        Paginated list of projects with metadata
    """
    # Create pagination and sort params
    pagination = PaginationParams(limit=limit, offset=offset)
    sort_params = SortParams(sort_by=sort_by, sort_order=sort_order)
    
    # Build filters
    filters = {}
    if name:
        filters["name"] = name
    
    # Define allowed fields
    allowed_sort_fields = ["name", "create_at", "update_at"]
    allowed_filter_fields = ["name", "default_model_config_id"]
    search_fields = ["name", "description"]
    
    # Build query
    base_query = db.query(Projects)
    query = build_query(
        base_query=base_query,
        model=Projects,
        pagination=None,  # We'll apply pagination in create_paginated_response
        sort_params=sort_params,
        filters=filters,
        search_term=search,
        search_fields=search_fields,
        allowed_filter_fields=allowed_filter_fields,
        allowed_sort_fields=allowed_sort_fields
    )
    
    # Create paginated response
    return create_paginated_response(query, pagination, ProjectResponse)


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

