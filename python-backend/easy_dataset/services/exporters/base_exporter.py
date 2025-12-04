"""Base exporter class for all export formats."""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
from sqlalchemy.orm import Session, Query


class BaseExporter(ABC):
    """
    Abstract base class for dataset exporters.
    
    All format-specific exporters should inherit from this class
    and implement the export method.
    
    Attributes:
        FILE_EXTENSION: Default file extension for this format
        SUPPORTS_STREAMING: Whether this format supports streaming large datasets
    """
    
    FILE_EXTENSION = ""
    SUPPORTS_STREAMING = False
    
    def __init__(
        self,
        session: Session,
        include_metadata: bool = True,
        **options: Any
    ):
        """
        Initialize the exporter.
        
        Args:
            session: SQLAlchemy database session
            include_metadata: Whether to include metadata fields
            **options: Format-specific options
        """
        self.session = session
        self.include_metadata = include_metadata
        self.options = options
    
    @abstractmethod
    def export(
        self,
        query: Query,
        output_path: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Export dataset entries to the specified format.
        
        Args:
            query: SQLAlchemy query for dataset entries
            output_path: Path to save the exported file. If None, return as string
            progress_callback: Optional callback function(current, total) for progress
        
        Returns:
            Path to the exported file or the exported data as string
        """
        pass
    
    def _prepare_entry(self, entry: Any) -> Dict[str, Any]:
        """
        Prepare a dataset entry for export.
        
        Converts the database model to a dictionary with appropriate fields.
        
        Args:
            entry: Dataset model instance
        
        Returns:
            Dictionary representation of the entry
        """
        data = {
            'question': entry.question,
            'answer': entry.answer,
        }
        
        if self.include_metadata:
            data.update({
                'id': entry.id,
                'question_id': entry.question_id,
                'answer_type': entry.answer_type,
                'chunk_name': entry.chunk_name,
                'chunk_content': entry.chunk_content,
                'model': entry.model,
                'question_label': entry.question_label,
                'cot': entry.cot,
                'confirmed': entry.confirmed,
                'score': entry.score,
                'ai_evaluation': entry.ai_evaluation,
                'tags': entry.tags,
                'note': entry.note,
                'create_at': entry.create_at.isoformat() if entry.create_at else None,
                'update_at': entry.update_at.isoformat() if entry.update_at else None,
            })
        
        return data
    
    def _get_total_count(self, query: Query) -> int:
        """
        Get total count of entries in the query.
        
        Args:
            query: SQLAlchemy query
        
        Returns:
            Total count of entries
        """
        return query.count()
    
    def _report_progress(
        self,
        current: int,
        total: int,
        callback: Optional[callable] = None
    ) -> None:
        """
        Report progress to callback if provided.
        
        Args:
            current: Current progress count
            total: Total count
            callback: Optional callback function
        """
        if callback:
            callback(current, total)

