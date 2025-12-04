"""
FastAPI application entry point.

This module initializes the FastAPI application with middleware,
error handlers, and routes.
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

from easy_dataset.database.connection import init_database
from easy_dataset_server.config import settings
from easy_dataset_server.middleware.error_handler import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Easy Dataset API server...")
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Easy Dataset API server...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="API for creating LLM fine-tuning datasets",
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug,
)

# Register exception handlers
register_exception_handlers(app)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    logger.info(
        f"Request started: {request.method} {request.url.path} "
        f"[{request_id}]"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"[{request_id}] - Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"[{request_id}] - Error: {str(e)} - Time: {process_time:.3f}s",
            exc_info=True,
        )
        raise


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Import and include routers
from easy_dataset_server.api import backup, chunks, datasets, files, projects, questions, websocket

app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(chunks.router, prefix="/api", tags=["chunks"])
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(datasets.router, prefix="/api", tags=["datasets"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])
app.include_router(backup.router, prefix="/api", tags=["backup"])

