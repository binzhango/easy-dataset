"""Dataset exporter service - Export datasets to various formats."""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from easy_dataset.models.dataset import Datasets

logger = logging.getLogger(__name__)


class DatasetExporterService:
    """
    Service for exporting datasets to various formats.
    
    Supports multiple export formats:
    - JSON: Standard JSON format for LLM training
    - JSONL: JSON Lines format (one object per line)
    - CSV: Comma-separated values
    - Hugging Face: Format compatible with datasets library
    - LLaMA Factory: Format for LLaMA Factory training
    
    Features:
    - Streaming support for large datasets
    - Progress tracking
    - Filtering by tags, ratings, confirmation status
    - Format-specific options
    
    Example:
        >>> from easy_dataset.services.exporter import DatasetExporterService
        >>> from easy_dataset.database import get_session
        >>> 
        >>> session = get_session()
        >>> exporter = DatasetExporterService(session)
        >>> 
        >>> # Export to JSON
        >>> path = exporter.export(
        ...     project_id="abc123",
        ...     format="json",
        ...     output_path="dataset.json",
        ...     min_rating=4.0
        ... )
        >>> print(f"Exported to: {path}")
    """
    
    def __init__(self, session: Session):
        """
        Initialize the exporter service.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self._exporters: Dict[str, Any] = {}
        self._register_exporters()
    
    def _register_exporters(self) -> None:
        """Register all available exporters."""
        # Import exporters here to avoid circular imports
        try:
            from easy_dataset.services.exporters.json_exporter import JSONExporter
            self._exporters['json'] = JSONExporter
        except ImportError:
            logger.warning("JSON exporter not available")
        
        try:
            from easy_dataset.services.exporters.jsonl_exporter import JSONLExporter
            self._exporters['jsonl'] = JSONLExporter
        except ImportError:
            logger.warning("JSONL exporter not available")
        
        try:
            from easy_dataset.services.exporters.csv_exporter import CSVExporter
            self._exporters['csv'] = CSVExporter
        except ImportError:
            logger.warning("CSV exporter not available")
        
        try:
            from easy_dataset.services.exporters.huggingface_exporter import HuggingFaceExporter
            self._exporters['huggingface'] = HuggingFaceExporter
        except ImportError:
            logger.warning("Hugging Face exporter not available")
        
        try:
            from easy_dataset.services.exporters.llamafactory_exporter import LLaMAFactoryExporter
            self._exporters['llamafactory'] = LLaMAFactoryExporter
        except ImportError:
            logger.warning("LLaMA Factory exporter not available")
    
    def export(
        self,
        project_id: str,
        format: str,
        output_path: Optional[str] = None,
        filter_tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        confirmed_only: bool = False,
        include_metadata: bool = True,
        progress_callback: Optional[callable] = None,
        **format_options: Any
    ) -> str:
        """
        Export dataset to specified format.
        
        Args:
            project_id: Project ID to export from
            format: Export format (json, jsonl, csv, huggingface, llamafactory)
            output_path: Path to save the exported file. If None, returns data as string
            filter_tags: Only export entries with these tags
            min_rating: Only export entries with rating >= this value
            confirmed_only: Only export confirmed entries
            include_metadata: Include metadata fields in export
            progress_callback: Optional callback function(current, total) for progress
            **format_options: Format-specific options
        
        Returns:
            Path to the exported file or the exported data as string
        
        Raises:
            ValueError: If format is not supported
            FileNotFoundError: If project has no dataset entries
        """
        # Validate format
        if format not in self._exporters:
            available = ', '.join(self._exporters.keys())
            raise ValueError(
                f"Unsupported export format: {format}. "
                f"Available formats: {available}"
            )
        
        # Query dataset entries with filters
        query = self.session.query(Datasets).filter(
            Datasets.project_id == project_id
        )
        
        # Apply filters
        if filter_tags:
            # Filter by tags (tags are comma-separated in the database)
            for tag in filter_tags:
                query = query.filter(Datasets.tags.contains(tag))
        
        if min_rating is not None:
            query = query.filter(Datasets.score >= min_rating)
        
        if confirmed_only:
            query = query.filter(Datasets.confirmed == True)
        
        # Order by creation date
        query = query.order_by(Datasets.create_at)
        
        # Get total count for progress tracking
        total_count = query.count()
        
        if total_count == 0:
            raise FileNotFoundError(
                f"No dataset entries found for project {project_id} "
                f"with the specified filters"
            )
        
        logger.info(
            f"Exporting {total_count} dataset entries from project {project_id} "
            f"to format: {format}"
        )
        
        # Create exporter instance
        exporter_class = self._exporters[format]
        exporter = exporter_class(
            session=self.session,
            include_metadata=include_metadata,
            **format_options
        )
        
        # Export data
        result = exporter.export(
            query=query,
            output_path=output_path,
            progress_callback=progress_callback
        )
        
        logger.info(f"Export completed: {result}")
        return result
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported export formats.
        
        Returns:
            List of format names
        """
        return list(self._exporters.keys())
    
    def get_format_info(self, format: str) -> Dict[str, Any]:
        """
        Get information about a specific export format.
        
        Args:
            format: Format name
        
        Returns:
            Dictionary with format information
        
        Raises:
            ValueError: If format is not supported
        """
        if format not in self._exporters:
            raise ValueError(f"Unsupported format: {format}")
        
        exporter_class = self._exporters[format]
        return {
            'name': format,
            'description': exporter_class.__doc__ or '',
            'file_extension': getattr(exporter_class, 'FILE_EXTENSION', ''),
            'supports_streaming': getattr(exporter_class, 'SUPPORTS_STREAMING', False),
        }

