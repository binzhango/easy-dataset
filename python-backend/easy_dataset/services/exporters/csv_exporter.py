"""CSV format exporter for datasets."""

import csv
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from io import StringIO
from sqlalchemy.orm import Query

from easy_dataset.services.exporters.base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class CSVExporter(BaseExporter):
    """
    Export datasets to CSV (Comma-Separated Values) format.
    
    Features:
    - Proper escaping of special characters (quotes, commas, newlines)
    - Handles multiline content in cells
    - Configurable delimiter (comma, tab, semicolon, etc.)
    - Optional header row
    - Configurable quote character
    
    The CSV format is useful for:
    - Spreadsheet applications (Excel, Google Sheets)
    - Data analysis tools (pandas, R)
    - Simple text processing
    
    Example output:
        question,answer,model,score
        "What is ML?","Machine learning is...","gpt-4",4.5
        "What is AI?","Artificial intelligence is...","gpt-4",5.0
    
    Multiline content is properly quoted:
        question,answer
        "What is
        machine learning?","ML is a field
        of AI that..."
    """
    
    FILE_EXTENSION = ".csv"
    SUPPORTS_STREAMING = True
    
    def __init__(
        self,
        session,
        include_metadata: bool = True,
        delimiter: str = ',',
        quotechar: str = '"',
        include_header: bool = True,
        columns: Optional[List[str]] = None,
        **options
    ):
        """
        Initialize CSV exporter.
        
        Args:
            session: SQLAlchemy database session
            include_metadata: Whether to include metadata fields
            delimiter: Field delimiter (default: comma)
            quotechar: Quote character for escaping (default: double quote)
            include_header: Whether to include header row
            columns: List of columns to export (None = all columns)
            **options: Additional options
        """
        super().__init__(session, include_metadata, **options)
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.include_header = include_header
        self.columns = columns
    
    def export(
        self,
        query: Query,
        output_path: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Export dataset to CSV format.
        
        Args:
            query: SQLAlchemy query for dataset entries
            output_path: Path to save the CSV file
            progress_callback: Optional callback for progress updates
        
        Returns:
            Path to the exported file or CSV string
        """
        total = self._get_total_count(query)
        logger.info(f"Exporting {total} entries to CSV")
        
        # Determine columns to export
        if self.columns:
            fieldnames = self.columns
        else:
            fieldnames = self._get_default_columns()
        
        # Prepare output
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Stream to file
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    quoting=csv.QUOTE_MINIMAL
                )
                
                # Write header
                if self.include_header:
                    writer.writeheader()
                
                # Write rows
                for idx, entry in enumerate(query.all(), 1):
                    row = self._prepare_row(entry, fieldnames)
                    writer.writerow(row)
                    
                    # Report progress
                    self._report_progress(idx, total, progress_callback)
            
            logger.info(f"Exported {total} entries to {output_file}")
            return str(output_file)
        else:
            # Return as string
            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=fieldnames,
                delimiter=self.delimiter,
                quotechar=self.quotechar,
                quoting=csv.QUOTE_MINIMAL
            )
            
            # Write header
            if self.include_header:
                writer.writeheader()
            
            # Write rows
            for idx, entry in enumerate(query.all(), 1):
                row = self._prepare_row(entry, fieldnames)
                writer.writerow(row)
                
                # Report progress
                self._report_progress(idx, total, progress_callback)
            
            return output.getvalue()
    
    def _get_default_columns(self) -> List[str]:
        """
        Get default column names based on metadata setting.
        
        Returns:
            List of column names
        """
        # Always include question and answer
        columns = ['question', 'answer']
        
        if self.include_metadata:
            columns.extend([
                'id',
                'question_id',
                'answer_type',
                'chunk_name',
                'chunk_content',
                'model',
                'question_label',
                'cot',
                'confirmed',
                'score',
                'ai_evaluation',
                'tags',
                'note',
                'create_at',
                'update_at'
            ])
        
        return columns
    
    def _prepare_row(self, entry: Any, fieldnames: List[str]) -> Dict[str, Any]:
        """
        Prepare a row for CSV export.
        
        Converts the dataset entry to a dictionary with only the specified fields.
        Handles special characters and multiline content.
        
        Args:
            entry: Dataset model instance
            fieldnames: List of field names to include
        
        Returns:
            Dictionary with field values
        """
        # Get full entry data
        full_data = self._prepare_entry(entry)
        
        # Extract only requested fields
        row = {}
        for field in fieldnames:
            value = full_data.get(field, '')
            
            # Convert None to empty string
            if value is None:
                value = ''
            
            # Convert boolean to string
            elif isinstance(value, bool):
                value = 'true' if value else 'false'
            
            # Convert numbers to string
            elif isinstance(value, (int, float)):
                value = str(value)
            
            # Keep strings as-is (csv module handles escaping)
            row[field] = value
        
        return row

