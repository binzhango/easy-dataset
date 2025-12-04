"""JSON format exporter for datasets."""

import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from sqlalchemy.orm import Query

from easy_dataset.services.exporters.base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class JSONExporter(BaseExporter):
    """
    Export datasets to JSON format.
    
    Supports multiple LLM training schemas:
    - alpaca: Alpaca format (instruction, input, output)
    - sharegpt: ShareGPT format (conversations array)
    - openai: OpenAI fine-tuning format (messages array)
    - raw: Raw format with all fields
    
    Example output (Alpaca format):
        [
            {
                "instruction": "What is machine learning?",
                "input": "",
                "output": "Machine learning is..."
            }
        ]
    
    Example output (ShareGPT format):
        [
            {
                "conversations": [
                    {"from": "human", "value": "What is machine learning?"},
                    {"from": "gpt", "value": "Machine learning is..."}
                ]
            }
        ]
    """
    
    FILE_EXTENSION = ".json"
    SUPPORTS_STREAMING = False
    
    def __init__(
        self,
        session,
        include_metadata: bool = True,
        schema: str = "raw",
        indent: Optional[int] = 2,
        ensure_ascii: bool = False,
        **options
    ):
        """
        Initialize JSON exporter.
        
        Args:
            session: SQLAlchemy database session
            include_metadata: Whether to include metadata fields
            schema: Output schema (alpaca, sharegpt, openai, raw)
            indent: JSON indentation (None for compact)
            ensure_ascii: Whether to escape non-ASCII characters
            **options: Additional options
        """
        super().__init__(session, include_metadata, **options)
        self.schema = schema
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        
        # Validate schema
        valid_schemas = ['alpaca', 'sharegpt', 'openai', 'raw']
        if schema not in valid_schemas:
            raise ValueError(
                f"Invalid schema: {schema}. "
                f"Valid schemas: {', '.join(valid_schemas)}"
            )
    
    def export(
        self,
        query: Query,
        output_path: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Export dataset to JSON format.
        
        Args:
            query: SQLAlchemy query for dataset entries
            output_path: Path to save the JSON file
            progress_callback: Optional callback for progress updates
        
        Returns:
            Path to the exported file or JSON string
        """
        total = self._get_total_count(query)
        logger.info(f"Exporting {total} entries to JSON ({self.schema} schema)")
        
        # Collect all entries
        entries = []
        for idx, entry in enumerate(query.all(), 1):
            # Convert entry based on schema
            converted = self._convert_entry(entry)
            entries.append(converted)
            
            # Report progress
            self._report_progress(idx, total, progress_callback)
        
        # Convert to JSON
        json_data = json.dumps(
            entries,
            indent=self.indent,
            ensure_ascii=self.ensure_ascii
        )
        
        # Save to file or return string
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            logger.info(f"Exported {total} entries to {output_file}")
            return str(output_file)
        else:
            return json_data
    
    def _convert_entry(self, entry: Any) -> Dict[str, Any]:
        """
        Convert a dataset entry to the specified schema format.
        
        Args:
            entry: Dataset model instance
        
        Returns:
            Dictionary in the specified schema format
        """
        if self.schema == 'alpaca':
            return self._to_alpaca_format(entry)
        elif self.schema == 'sharegpt':
            return self._to_sharegpt_format(entry)
        elif self.schema == 'openai':
            return self._to_openai_format(entry)
        else:  # raw
            return self._prepare_entry(entry)
    
    def _to_alpaca_format(self, entry: Any) -> Dict[str, Any]:
        """
        Convert entry to Alpaca format.
        
        Alpaca format:
        {
            "instruction": "question text",
            "input": "context or empty",
            "output": "answer text"
        }
        """
        data = {
            'instruction': entry.question,
            'input': entry.chunk_content if self.include_metadata else '',
            'output': entry.answer
        }
        
        # Add optional fields if metadata is included
        if self.include_metadata:
            data['metadata'] = {
                'id': entry.id,
                'model': entry.model,
                'label': entry.question_label,
                'score': entry.score,
                'tags': entry.tags.split(',') if entry.tags else [],
            }
        
        return data
    
    def _to_sharegpt_format(self, entry: Any) -> Dict[str, Any]:
        """
        Convert entry to ShareGPT format.
        
        ShareGPT format:
        {
            "conversations": [
                {"from": "human", "value": "question"},
                {"from": "gpt", "value": "answer"}
            ]
        }
        """
        conversations = [
            {'from': 'human', 'value': entry.question},
            {'from': 'gpt', 'value': entry.answer}
        ]
        
        # Add system message if chunk content is included
        if self.include_metadata and entry.chunk_content:
            conversations.insert(0, {
                'from': 'system',
                'value': f'Context: {entry.chunk_content}'
            })
        
        data = {'conversations': conversations}
        
        # Add metadata if requested
        if self.include_metadata:
            data['metadata'] = {
                'id': entry.id,
                'model': entry.model,
                'label': entry.question_label,
                'score': entry.score,
                'tags': entry.tags.split(',') if entry.tags else [],
            }
        
        return data
    
    def _to_openai_format(self, entry: Any) -> Dict[str, Any]:
        """
        Convert entry to OpenAI fine-tuning format.
        
        OpenAI format:
        {
            "messages": [
                {"role": "user", "content": "question"},
                {"role": "assistant", "content": "answer"}
            ]
        }
        """
        messages = [
            {'role': 'user', 'content': entry.question},
            {'role': 'assistant', 'content': entry.answer}
        ]
        
        # Add system message if chunk content is included
        if self.include_metadata and entry.chunk_content:
            messages.insert(0, {
                'role': 'system',
                'content': f'Context: {entry.chunk_content}'
            })
        
        data = {'messages': messages}
        
        # Add metadata if requested
        if self.include_metadata:
            data['metadata'] = {
                'id': entry.id,
                'model': entry.model,
                'label': entry.question_label,
                'score': entry.score,
                'tags': entry.tags.split(',') if entry.tags else [],
            }
        
        return data

