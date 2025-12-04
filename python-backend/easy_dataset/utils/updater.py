"""
Auto-update functionality for Python backend.

This module provides functionality to check for and install updates
to the Python backend package.
"""

import hashlib
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import httpx

logger = logging.getLogger(__name__)


class BackendUpdater:
    """Handles checking and installing updates for the Python backend."""

    def __init__(
        self,
        update_server_url: str = "https://api.github.com/repos/ConardLi/easy-dataset/releases",
        current_version: str = "2.0.0",
    ):
        """Initialize the updater.

        Args:
            update_server_url: URL to check for updates
            current_version: Current version of the backend
        """
        self.update_server_url = update_server_url
        self.current_version = current_version
        self.client = httpx.Client(timeout=30.0)

    def check_for_updates(self) -> Optional[dict]:
        """Check if updates are available.

        Returns:
            Dictionary with update information if available, None otherwise.
            Format: {
                'version': '2.1.0',
                'download_url': 'https://...',
                'release_notes': 'What\'s new...',
                'published_at': '2024-01-01T00:00:00Z'
            }
        """
        try:
            logger.info(f"Checking for updates from {self.update_server_url}")

            response = self.client.get(self.update_server_url)
            response.raise_for_status()

            releases = response.json()

            if not releases:
                logger.info("No releases found")
                return None

            # Get the latest release
            latest_release = releases[0]
            latest_version = latest_release.get("tag_name", "").lstrip("v")

            logger.info(
                f"Latest version: {latest_version}, Current version: {self.current_version}"
            )

            # Compare versions
            if self._is_newer_version(latest_version, self.current_version):
                # Find Python backend asset
                assets = latest_release.get("assets", [])
                backend_asset = None

                for asset in assets:
                    if "python-backend" in asset.get("name", "").lower():
                        backend_asset = asset
                        break

                if not backend_asset:
                    logger.warning("No Python backend asset found in release")
                    return None

                return {
                    "version": latest_version,
                    "download_url": backend_asset.get("browser_download_url"),
                    "release_notes": latest_release.get("body", ""),
                    "published_at": latest_release.get("published_at"),
                    "size": backend_asset.get("size", 0),
                }

            logger.info("Already on the latest version")
            return None

        except httpx.HTTPError as e:
            logger.error(f"Failed to check for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error checking for updates: {e}", exc_info=True)
            return None

    def download_update(
        self, download_url: str, progress_callback: Optional[callable] = None
    ) -> Optional[Path]:
        """Download an update package.

        Args:
            download_url: URL to download the update from
            progress_callback: Optional callback for progress updates (bytes_downloaded, total_bytes)

        Returns:
            Path to the downloaded file, or None if download failed
        """
        try:
            logger.info(f"Downloading update from {download_url}")

            # Create temporary file
            temp_dir = tempfile.mkdtemp(prefix="easy_dataset_update_")
            temp_file = Path(temp_dir) / "update.zip"

            # Download with progress tracking
            with self.client.stream("GET", download_url) as response:
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(temp_file, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback:
                            progress_callback(downloaded, total_size)

            logger.info(f"Update downloaded to {temp_file}")
            return temp_file

        except httpx.HTTPError as e:
            logger.error(f"Failed to download update: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading update: {e}", exc_info=True)
            return None

    def verify_update(self, update_file: Path, expected_hash: Optional[str] = None) -> bool:
        """Verify the integrity of an update package.

        Args:
            update_file: Path to the update file
            expected_hash: Expected SHA256 hash (optional)

        Returns:
            True if verification passed, False otherwise
        """
        try:
            if not update_file.exists():
                logger.error(f"Update file not found: {update_file}")
                return False

            # Calculate hash
            sha256_hash = hashlib.sha256()
            with open(update_file, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)

            calculated_hash = sha256_hash.hexdigest()

            if expected_hash:
                if calculated_hash != expected_hash:
                    logger.error(
                        f"Hash mismatch! Expected: {expected_hash}, Got: {calculated_hash}"
                    )
                    return False
                logger.info("Hash verification passed")
            else:
                logger.info(f"Update file hash: {calculated_hash}")

            return True

        except Exception as e:
            logger.error(f"Failed to verify update: {e}", exc_info=True)
            return False

    def install_update(self, update_file: Path, install_dir: Optional[Path] = None) -> bool:
        """Install an update package.

        Args:
            update_file: Path to the update file
            install_dir: Directory to install to (defaults to current installation)

        Returns:
            True if installation succeeded, False otherwise
        """
        try:
            if not update_file.exists():
                logger.error(f"Update file not found: {update_file}")
                return False

            if install_dir is None:
                # Determine installation directory
                install_dir = Path(__file__).parent.parent.parent

            logger.info(f"Installing update to {install_dir}")

            # Create backup
            backup_dir = install_dir.parent / f"{install_dir.name}_backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            logger.info(f"Creating backup at {backup_dir}")
            shutil.copytree(install_dir, backup_dir, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))

            try:
                # Extract update
                import zipfile

                with zipfile.ZipFile(update_file, "r") as zip_ref:
                    zip_ref.extractall(install_dir)

                logger.info("Update installed successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to install update: {e}", exc_info=True)

                # Restore backup
                logger.info("Restoring backup...")
                if install_dir.exists():
                    shutil.rmtree(install_dir)
                shutil.copytree(backup_dir, install_dir)
                logger.info("Backup restored")

                return False

        except Exception as e:
            logger.error(f"Unexpected error installing update: {e}", exc_info=True)
            return False

    def _is_newer_version(self, version1: str, version2: str) -> bool:
        """Compare two version strings.

        Args:
            version1: First version (e.g., "2.1.0")
            version2: Second version (e.g., "2.0.0")

        Returns:
            True if version1 is newer than version2
        """
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]

            # Pad with zeros if needed
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            return v1_parts > v2_parts

        except (ValueError, AttributeError):
            logger.warning(f"Failed to compare versions: {version1} vs {version2}")
            return False

    def cleanup(self):
        """Clean up resources."""
        try:
            self.client.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Convenience functions for use in Electron app

def check_for_backend_updates(current_version: str = "2.0.0") -> Optional[dict]:
    """Check if backend updates are available.

    Args:
        current_version: Current version of the backend

    Returns:
        Update information if available, None otherwise
    """
    updater = BackendUpdater(current_version=current_version)
    try:
        return updater.check_for_updates()
    finally:
        updater.cleanup()


def download_backend_update(
    download_url: str, progress_callback: Optional[callable] = None
) -> Optional[Path]:
    """Download a backend update.

    Args:
        download_url: URL to download from
        progress_callback: Optional progress callback

    Returns:
        Path to downloaded file, or None if failed
    """
    updater = BackendUpdater()
    try:
        return updater.download_update(download_url, progress_callback)
    finally:
        updater.cleanup()


def install_backend_update(update_file: Path) -> bool:
    """Install a backend update.

    Args:
        update_file: Path to update file

    Returns:
        True if installation succeeded
    """
    updater = BackendUpdater()
    try:
        return updater.install_update(update_file)
    finally:
        updater.cleanup()
