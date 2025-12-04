"""
API endpoints for backend updates.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel

from easy_dataset.utils.updater import (
    BackendUpdater,
    check_for_backend_updates,
    download_backend_update,
    install_backend_update,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class UpdateCheckResponse(BaseModel):
    """Response model for update check."""

    update_available: bool
    current_version: str
    latest_version: Optional[str] = None
    download_url: Optional[str] = None
    release_notes: Optional[str] = None
    published_at: Optional[str] = None
    size: Optional[int] = None


class UpdateDownloadRequest(BaseModel):
    """Request model for update download."""

    download_url: str


class UpdateDownloadResponse(BaseModel):
    """Response model for update download."""

    success: bool
    message: str
    file_path: Optional[str] = None


class UpdateInstallRequest(BaseModel):
    """Request model for update installation."""

    update_file: str


class UpdateInstallResponse(BaseModel):
    """Response model for update installation."""

    success: bool
    message: str


@router.get("/check", response_model=UpdateCheckResponse)
async def check_updates(current_version: str = "2.0.0") -> UpdateCheckResponse:
    """Check if backend updates are available.

    Args:
        current_version: Current version of the backend

    Returns:
        Update information
    """
    try:
        logger.info(f"Checking for updates (current version: {current_version})")

        update_info = check_for_backend_updates(current_version)

        if update_info:
            return UpdateCheckResponse(
                update_available=True,
                current_version=current_version,
                latest_version=update_info["version"],
                download_url=update_info["download_url"],
                release_notes=update_info["release_notes"],
                published_at=update_info["published_at"],
                size=update_info.get("size"),
            )
        else:
            return UpdateCheckResponse(
                update_available=False,
                current_version=current_version,
            )

    except Exception as e:
        logger.error(f"Failed to check for updates: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check for updates: {str(e)}",
        )


@router.post("/download", response_model=UpdateDownloadResponse)
async def download_update(
    request: UpdateDownloadRequest,
    background_tasks: BackgroundTasks,
) -> UpdateDownloadResponse:
    """Download a backend update.

    Args:
        request: Download request with URL
        background_tasks: FastAPI background tasks

    Returns:
        Download result
    """
    try:
        logger.info(f"Downloading update from {request.download_url}")

        # Download in background
        update_file = download_backend_update(request.download_url)

        if update_file:
            return UpdateDownloadResponse(
                success=True,
                message="Update downloaded successfully",
                file_path=str(update_file),
            )
        else:
            return UpdateDownloadResponse(
                success=False,
                message="Failed to download update",
            )

    except Exception as e:
        logger.error(f"Failed to download update: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download update: {str(e)}",
        )


@router.post("/install", response_model=UpdateInstallResponse)
async def install_update(request: UpdateInstallRequest) -> UpdateInstallResponse:
    """Install a backend update.

    Note: This will require restarting the backend service.

    Args:
        request: Install request with file path

    Returns:
        Installation result
    """
    try:
        logger.info(f"Installing update from {request.update_file}")

        update_file = Path(request.update_file)

        if not update_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Update file not found",
            )

        success = install_backend_update(update_file)

        if success:
            return UpdateInstallResponse(
                success=True,
                message="Update installed successfully. Please restart the application.",
            )
        else:
            return UpdateInstallResponse(
                success=False,
                message="Failed to install update",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to install update: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to install update: {str(e)}",
        )


@router.get("/version")
async def get_version() -> dict:
    """Get current backend version.

    Returns:
        Version information
    """
    from easy_dataset_server.config import settings

    return {
        "version": settings.app_version,
        "name": settings.app_name,
    }
