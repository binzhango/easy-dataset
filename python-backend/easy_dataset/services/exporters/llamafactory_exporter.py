"""LLaMA Factory format exporter."""

import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from sqlalchemy.orm import Query

from easy_dataset.services.exporters.base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class LLaMAFactoryExporter(BaseExporter):
    """
    Export datasets to LLaMA Factory format.
    
    LLaMA Factory is a popular framework for fine-tuning LLaMA models.
    It requires:
    1. A data file (JSON or JSONL) with specific format
    2. A dataset_info.json configuration file
    
    Supported task types:
    - sft: Supervised Fine-Tuning (instruction-response pairs)
    - pretrain: Pre-training (raw text)
    - rm: Reward Modeling (ranked responses)
    - ppo: PPO training (with rewards)
    
    Format structure:
        dataset/
        ├── data.json (or data.jsonl)
        └── dataset_info.json
    
    Example data.json (SFT format):
        [
            {
                "instruction": "What is machine learning?",
                "input": "",
                "output": "Machine learning is...",
                "system": "You are a helpful assistant.",
                "history": []
            }
        ]
    
    Example dataset_info.json:
        {
            "my_dataset": {
                "file_name": "data.json",
                "formatting": "alpaca",
                "columns": {
                    "prompt": "instruction",
                    "query": "input",
                    "response": "output",
                    "system": "system",
                    "history": "history"
                }
            }
        }
    """
    
    FILE_EXTENSION = ".json"
    SUPPORTS_STREAMING = True
    
    def __init__(
        self,
        session,
        include_metadata: bool = True,
        task_type: str = "sft",
        formatting: str = "alpaca",
        use_jsonl: bool = False,
        dataset_name: str = "easy_dataset",
        system_prompt: Optional[str] = None,
        **options
    ):
        """
        Initialize LLaMA Factory exporter.
        
        Args:
            session: SQLAlchemy database session
            include_metadata: Whether to include metadata fields
            task_type: Task type (sft, pretrain, rm, ppo)
            formatting: Data formatting (alpaca, sharegpt)
            use_jsonl: Use JSONL format instead of JSON
            dataset_name: Name of the dataset
            system_prompt: Optional system prompt to include
            **options: Additional options
        """
        super().__init__(session, include_metadata, **options)
        self.task_type = task_type
        self.formatting = formatting
        self.use_jsonl = use_jsonl
        self.dataset_name = dataset_name
        self.system_prompt = system_prompt or "You are a helpful assistant."
        
        # Validate task type
        valid_tasks = ['sft', 'pretrain', 'rm', 'ppo']
        if task_type not in valid_tasks:
            raise ValueError(
                f"Invalid task_type: {task_type}. "
                f"Valid types: {', '.join(valid_tasks)}"
            )
        
        # Validate formatting
        valid_formats = ['alpaca', 'sharegpt']
        if formatting not in valid_formats:
            raise ValueError(
                f"Invalid formatting: {formatting}. "
                f"Valid formats: {', '.join(valid_formats)}"
            )
    
    def export(
        self,
        query: Query,
        output_path: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Export dataset to LLaMA Factory format.
        
        Args:
            query: SQLAlchemy query for dataset entries
            output_path: Path to output directory or file
            progress_callback: Optional callback for progress updates
        
        Returns:
            Path to the output directory
        """
        total = self._get_total_count(query)
        logger.info(
            f"Exporting {total} entries to LLaMA Factory format "
            f"(task: {self.task_type}, format: {self.formatting})"
        )
        
        # Determine output directory
        if output_path:
            if Path(output_path).suffix:
                # If a file path is given, use its parent directory
                output_dir = Path(output_path).parent / self.dataset_name
            else:
                # If a directory is given, use it
                output_dir = Path(output_path)
        else:
            output_dir = Path(self.dataset_name)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect and convert entries
        entries = []
        for idx, entry in enumerate(query.all(), 1):
            converted = self._convert_entry(entry)
            entries.append(converted)
            
            # Report progress
            self._report_progress(idx, total, progress_callback)
        
        # Write data file
        if self.use_jsonl:
            data_file = output_dir / 'data.jsonl'
            with open(data_file, 'w', encoding='utf-8') as f:
                for entry in entries:
                    json_line = json.dumps(entry, ensure_ascii=False)
                    f.write(json_line + '\n')
        else:
            data_file = output_dir / 'data.json'
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
        
        # Create dataset_info.json
        dataset_info = self._create_dataset_info(data_file.name)
        info_file = output_dir / 'dataset_info.json'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported LLaMA Factory dataset to {output_dir}")
        return str(output_dir)
    
    def _convert_entry(self, entry: Any) -> Dict[str, Any]:
        """
        Convert entry to LLaMA Factory format.
        
        Args:
            entry: Dataset model instance
        
        Returns:
            Dictionary in LLaMA Factory format
        """
        if self.formatting == 'alpaca':
            return self._to_alpaca_format(entry)
        else:  # sharegpt
            return self._to_sharegpt_format(entry)
    
    def _to_alpaca_format(self, entry: Any) -> Dict[str, Any]:
        """
        Convert entry to Alpaca format for LLaMA Factory.
        
        Alpaca format:
        {
            "instruction": "question",
            "input": "context",
            "output": "answer",
            "system": "system prompt",
            "history": []
        }
        """
        data = {
            'instruction': entry.question,
            'input': entry.chunk_content if self.include_metadata else '',
            'output': entry.answer,
            'system': self.system_prompt,
            'history': []
        }
        
        return data
    
    def _to_sharegpt_format(self, entry: Any) -> Dict[str, Any]:
        """
        Convert entry to ShareGPT format for LLaMA Factory.
        
        ShareGPT format:
        {
            "conversations": [
                {"from": "system", "value": "system prompt"},
                {"from": "human", "value": "question"},
                {"from": "gpt", "value": "answer"}
            ]
        }
        """
        conversations = [
            {'from': 'system', 'value': self.system_prompt},
            {'from': 'human', 'value': entry.question},
            {'from': 'gpt', 'value': entry.answer}
        ]
        
        # Add context as system message if available
        if self.include_metadata and entry.chunk_content:
            conversations.insert(1, {
                'from': 'system',
                'value': f'Context: {entry.chunk_content}'
            })
        
        return {'conversations': conversations}
    
    def _create_dataset_info(self, data_filename: str) -> Dict[str, Any]:
        """
        Create dataset_info.json for LLaMA Factory.
        
        Args:
            data_filename: Name of the data file
        
        Returns:
            Dataset info dictionary
        """
        if self.formatting == 'alpaca':
            columns = {
                'prompt': 'instruction',
                'query': 'input',
                'response': 'output',
                'system': 'system',
                'history': 'history'
            }
        else:  # sharegpt
            columns = {
                'messages': 'conversations'
            }
        
        dataset_info = {
            self.dataset_name: {
                'file_name': data_filename,
                'formatting': self.formatting,
                'columns': columns,
                'tags': {
                    'task_categories': self.task_type,
                    'language_creators': 'machine-generated',
                    'source': 'easy-dataset'
                }
            }
        }
        
        return dataset_info

