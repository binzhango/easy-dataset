"""
Query utilities for filtering, pagination, and sorting.

This module provides utilities for building database queries with
filtering, pagination, and sorting capabilities.
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import asc, desc, or_, and_
from sqlalchemy.orm import Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    limit: int = Field(default=50, ge=1, le=1000, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    
    @property
    def page(self) -> int:
        """Calculate page number from offset."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1


class SortParams(BaseModel):
    """Sorting parameters."""
    
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", description="Sort order: asc or desc")
    
    def validate_sort_order(self) -> str:
        """Validate and normalize sort order."""
        order = self.sort_order.lower()
        if order not in ["asc", "desc"]:
            return "asc"
        return order


class FilterParams(BaseModel):
    """Generic filter parameters."""
    
    search: Optional[str] = Field(default=None, description="Search term")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Field filters")


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    
    items: List[Any]
    total: int
    limit: int
    offset: int
    page: int
    total_pages: int
    has_next: bool
    has_prev: bool


def apply_pagination(
    query: Query,
    pagination: PaginationParams
) -> Query:
    """
    Apply pagination to a query.
    
    Args:
        query: SQLAlchemy query
        pagination: Pagination parameters
    
    Returns:
        Query with pagination applied
    """
    return query.limit(pagination.limit).offset(pagination.offset)


def apply_sorting(
    query: Query,
    sort_params: SortParams,
    model: Type[T],
    allowed_fields: Optional[List[str]] = None
) -> Query:
    """
    Apply sorting to a query.
    
    Args:
        query: SQLAlchemy query
        sort_params: Sort parameters
        model: SQLAlchemy model class
        allowed_fields: List of allowed field names for sorting
    
    Returns:
        Query with sorting applied
    """
    if not sort_params.sort_by:
        return query
    
    # Validate field name
    if allowed_fields and sort_params.sort_by not in allowed_fields:
        logger.warning(f"Invalid sort field: {sort_params.sort_by}")
        return query
    
    # Check if field exists on model
    if not hasattr(model, sort_params.sort_by):
        logger.warning(f"Field {sort_params.sort_by} not found on model {model.__name__}")
        return query
    
    # Get field
    field = getattr(model, sort_params.sort_by)
    
    # Apply sort order
    order = sort_params.validate_sort_order()
    if order == "desc":
        query = query.order_by(desc(field))
    else:
        query = query.order_by(asc(field))
    
    return query


def apply_filters(
    query: Query,
    filters: Dict[str, Any],
    model: Type[T],
    allowed_fields: Optional[List[str]] = None
) -> Query:
    """
    Apply filters to a query.
    
    Supports:
    - Exact match: {"field": "value"}
    - IN clause: {"field": ["value1", "value2"]}
    - Range: {"field__gte": 10, "field__lte": 20}
    - Like: {"field__like": "%search%"}
    - Null check: {"field__isnull": True}
    
    Args:
        query: SQLAlchemy query
        filters: Dictionary of filters
        model: SQLAlchemy model class
        allowed_fields: List of allowed field names for filtering
    
    Returns:
        Query with filters applied
    """
    for key, value in filters.items():
        # Skip None values
        if value is None:
            continue
        
        # Parse field name and operator
        if "__" in key:
            field_name, operator = key.rsplit("__", 1)
        else:
            field_name = key
            operator = "eq"
        
        # Validate field name
        if allowed_fields and field_name not in allowed_fields:
            logger.warning(f"Invalid filter field: {field_name}")
            continue
        
        # Check if field exists on model
        if not hasattr(model, field_name):
            logger.warning(f"Field {field_name} not found on model {model.__name__}")
            continue
        
        # Get field
        field = getattr(model, field_name)
        
        # Apply operator
        try:
            if operator == "eq":
                if isinstance(value, list):
                    query = query.filter(field.in_(value))
                else:
                    query = query.filter(field == value)
            elif operator == "ne":
                query = query.filter(field != value)
            elif operator == "gt":
                query = query.filter(field > value)
            elif operator == "gte":
                query = query.filter(field >= value)
            elif operator == "lt":
                query = query.filter(field < value)
            elif operator == "lte":
                query = query.filter(field <= value)
            elif operator == "like":
                query = query.filter(field.like(value))
            elif operator == "ilike":
                query = query.filter(field.ilike(value))
            elif operator == "in":
                if isinstance(value, list):
                    query = query.filter(field.in_(value))
            elif operator == "notin":
                if isinstance(value, list):
                    query = query.filter(~field.in_(value))
            elif operator == "isnull":
                if value:
                    query = query.filter(field.is_(None))
                else:
                    query = query.filter(field.isnot(None))
            elif operator == "contains":
                query = query.filter(field.contains(value))
            else:
                logger.warning(f"Unknown operator: {operator}")
        except Exception as e:
            logger.error(f"Error applying filter {key}={value}: {e}")
    
    return query


def apply_search(
    query: Query,
    search_term: str,
    search_fields: List[str],
    model: Type[T]
) -> Query:
    """
    Apply search across multiple fields.
    
    Args:
        query: SQLAlchemy query
        search_term: Search term
        search_fields: List of field names to search
        model: SQLAlchemy model class
    
    Returns:
        Query with search applied
    """
    if not search_term or not search_fields:
        return query
    
    # Build OR conditions for all search fields
    conditions = []
    for field_name in search_fields:
        if hasattr(model, field_name):
            field = getattr(model, field_name)
            # Use case-insensitive LIKE
            conditions.append(field.ilike(f"%{search_term}%"))
    
    if conditions:
        query = query.filter(or_(*conditions))
    
    return query


def paginate(
    query: Query,
    pagination: PaginationParams
) -> PaginatedResponse:
    """
    Execute a query with pagination and return paginated response.
    
    Args:
        query: SQLAlchemy query
        pagination: Pagination parameters
    
    Returns:
        PaginatedResponse with items and metadata
    """
    # Get total count
    total = query.count()
    
    # Apply pagination
    items = query.limit(pagination.limit).offset(pagination.offset).all()
    
    # Calculate metadata
    total_pages = (total + pagination.limit - 1) // pagination.limit if pagination.limit > 0 else 1
    page = pagination.page
    has_next = page < total_pages
    has_prev = page > 1
    
    return PaginatedResponse(
        items=items,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        page=page,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


def build_query(
    base_query: Query,
    model: Type[T],
    pagination: Optional[PaginationParams] = None,
    sort_params: Optional[SortParams] = None,
    filters: Optional[Dict[str, Any]] = None,
    search_term: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
    allowed_filter_fields: Optional[List[str]] = None,
    allowed_sort_fields: Optional[List[str]] = None
) -> Query:
    """
    Build a complete query with filtering, sorting, and pagination.
    
    Args:
        base_query: Base SQLAlchemy query
        model: SQLAlchemy model class
        pagination: Pagination parameters
        sort_params: Sort parameters
        filters: Filter dictionary
        search_term: Search term
        search_fields: Fields to search
        allowed_filter_fields: Allowed fields for filtering
        allowed_sort_fields: Allowed fields for sorting
    
    Returns:
        Complete query with all parameters applied
    """
    query = base_query
    
    # Apply filters
    if filters:
        query = apply_filters(query, filters, model, allowed_filter_fields)
    
    # Apply search
    if search_term and search_fields:
        query = apply_search(query, search_term, search_fields, model)
    
    # Apply sorting
    if sort_params:
        query = apply_sorting(query, sort_params, model, allowed_sort_fields)
    
    # Apply pagination
    if pagination:
        query = apply_pagination(query, pagination)
    
    return query


def create_paginated_response(
    query: Query,
    pagination: PaginationParams,
    response_model: Optional[Type[BaseModel]] = None
) -> Dict[str, Any]:
    """
    Create a paginated response from a query.
    
    Args:
        query: SQLAlchemy query
        pagination: Pagination parameters
        response_model: Optional Pydantic model for serialization
    
    Returns:
        Dictionary with paginated data
    """
    result = paginate(query, pagination)
    
    # Convert items to response model if provided
    if response_model:
        items = [response_model.model_validate(item) for item in result.items]
    else:
        items = result.items
    
    return {
        "items": items,
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
        "page": result.page,
        "total_pages": result.total_pages,
        "has_next": result.has_next,
        "has_prev": result.has_prev
    }
