"""
Error handling middleware and utilities.

This module provides comprehensive error handling with user-friendly
error messages and proper HTTP status codes.
"""

import logging
import traceback
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    field: Optional[str] = None
    message: str
    code: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    error: str
    details: List[ErrorDetail]
    request_id: str
    timestamp: Optional[str] = None


class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[List[ErrorDetail]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(self.message)


class ValidationException(AppException):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class NotFoundException(AppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class ConflictException(AppException):
    """Resource conflict exception."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT
        )


class DatabaseException(AppException):
    """Database operation exception."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = []
        if original_error:
            details.append(ErrorDetail(
                message=str(original_error),
                code="DATABASE_ERROR",
                type=type(original_error).__name__
            ))
        
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceException(AppException):
    """External service error exception."""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} error: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY
        )


class FileProcessingException(AppException):
    """File processing error exception."""
    
    def __init__(self, message: str, file_name: Optional[str] = None):
        details = []
        if file_name:
            details.append(ErrorDetail(
                field="file",
                message=f"Error processing file: {file_name}",
                code="FILE_PROCESSING_ERROR"
            ))
        
        super().__init__(
            message=message,
            code="FILE_PROCESSING_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class TaskException(AppException):
    """Task processing error exception."""
    
    def __init__(self, task_id: str, message: str):
        super().__init__(
            message=f"Task {task_id} error: {message}",
            code="TASK_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def format_validation_errors(errors: List[Dict[str, Any]]) -> List[ErrorDetail]:
    """
    Format Pydantic validation errors into ErrorDetail objects.
    
    Args:
        errors: List of Pydantic validation errors
    
    Returns:
        List of ErrorDetail objects
    """
    formatted_errors = []
    
    for error in errors:
        # Get field path
        field = ".".join(str(loc) for loc in error.get("loc", []))
        
        # Get error message
        message = error.get("msg", "Validation error")
        
        # Get error type
        error_type = error.get("type", "value_error")
        
        formatted_errors.append(ErrorDetail(
            field=field if field else None,
            message=message,
            code="VALIDATION_ERROR",
            type=error_type
        ))
    
    return formatted_errors


def create_error_response(
    error: str,
    details: List[ErrorDetail],
    request_id: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        error: Error message
        details: List of error details
        request_id: Request ID for tracking
        status_code: HTTP status code
    
    Returns:
        JSONResponse with error information
    """
    from datetime import datetime
    
    response = ErrorResponse(
        error=error,
        details=details,
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat()
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle application exceptions.
    
    Args:
        request: FastAPI request
        exc: Application exception
    
    Returns:
        JSONResponse with error information
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Application error [{request_id}]: {exc.message}",
        exc_info=True
    )
    
    return create_error_response(
        error=exc.message,
        details=exc.details,
        request_id=request_id,
        status_code=exc.status_code
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
    
    Returns:
        JSONResponse with error information
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(
        f"HTTP exception [{request_id}]: {exc.status_code} - {exc.detail}"
    )
    
    details = [ErrorDetail(
        message=str(exc.detail),
        code=f"HTTP_{exc.status_code}"
    )]
    
    return create_error_response(
        error="Request failed",
        details=details,
        request_id=request_id,
        status_code=exc.status_code
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation error
    
    Returns:
        JSONResponse with validation error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Format validation errors
    details = format_validation_errors(exc.errors())
    
    logger.warning(
        f"Validation error [{request_id}]: {len(details)} validation errors"
    )
    
    return create_error_response(
        error="Validation failed",
        details=details,
        request_id=request_id,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.
    
    Args:
        request: FastAPI request
        exc: SQLAlchemy error
    
    Returns:
        JSONResponse with error information
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Database error [{request_id}]: {str(exc)}",
        exc_info=True
    )
    
    # Determine error type and message
    if isinstance(exc, IntegrityError):
        error_message = "Database integrity constraint violated"
        code = "INTEGRITY_ERROR"
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, OperationalError):
        error_message = "Database operation failed"
        code = "OPERATIONAL_ERROR"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        error_message = "Database error occurred"
        code = "DATABASE_ERROR"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    details = [ErrorDetail(
        message=error_message,
        code=code,
        type=type(exc).__name__
    )]
    
    return create_error_response(
        error=error_message,
        details=details,
        request_id=request_id,
        status_code=status_code
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
    
    Returns:
        JSONResponse with error information
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Unhandled exception [{request_id}]: {str(exc)}",
        exc_info=True
    )
    
    # In production, don't expose internal error details
    details = [ErrorDetail(
        message="An unexpected error occurred. Please try again later.",
        code="INTERNAL_ERROR",
        type=type(exc).__name__
    )]
    
    return create_error_response(
        error="Internal server error",
        details=details,
        request_id=request_id,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered")


# Utility functions for raising common errors

def raise_not_found(resource: str, identifier: str):
    """Raise a not found exception."""
    raise NotFoundException(resource, identifier)


def raise_validation_error(message: str, field: Optional[str] = None):
    """Raise a validation exception."""
    details = [ErrorDetail(
        field=field,
        message=message,
        code="VALIDATION_ERROR"
    )]
    raise ValidationException(message, details)


def raise_conflict(message: str):
    """Raise a conflict exception."""
    raise ConflictException(message)


def raise_database_error(message: str, original_error: Optional[Exception] = None):
    """Raise a database exception."""
    raise DatabaseException(message, original_error)


def raise_external_service_error(service: str, message: str):
    """Raise an external service exception."""
    raise ExternalServiceException(service, message)


def raise_file_processing_error(message: str, file_name: Optional[str] = None):
    """Raise a file processing exception."""
    raise FileProcessingException(message, file_name)


def raise_task_error(task_id: str, message: str):
    """Raise a task exception."""
    raise TaskException(task_id, message)
