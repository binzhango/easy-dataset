"""Hugging Face datasets format exporter."""

import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Query

from easy_dataset.services.exporters.base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class HuggingFaceExporter(BaseExporter):
    """
    Export datasets to Hugging Face datasets library format.
    
    Creates a dataset compatible with the Hugging Face datasets library,
    which can be loaded using:
        from datasets import load_dataset
        dataset = load_dataset('json', data_files='dataset.json')
    
    The exporter creates:
    1. A JSON/JSONL file with the dataset entries
    2. A dataset_info.json file with metadata
    3. Optional train/test split
    
    Format structure:
        dataset/
        ├── train.json (or train.jsonl)
        ├── test.json (or test.jsonl) [optional]
        └── dataset_info.json
    
    Example dataset_info.json:
        {
            "description": "Dataset for LLM fine-tuning",
            "features": {
                "question": {"dtype": "string"},
                "answer": {"dtype": "string"}
            },
            "splits": {
                "train": {"num_examples": 800},
                "test": {"num_examples": 200}
            }
        }
    """
    
    FILE_EXTENSION = ".json"
    SUPPORTS_STREAMING = True
    
    def __init__(
        self,
        session,
        include_metadata: bool = True,
        split_ratio: Optional[float] = None,
        use_jsonl: bool = True,
        dataset_name: str = "easy_dataset",
        description: str = "Dataset created with Easy Dataset",
        **options
    ):
        """
        Initialize Hugging Face exporter.
        
        Args:
            session: SQLAlchemy database session
            include_metadata: Whether to include metadata fields
            split_ratio: Train/test split ratio (e.g., 0.8 for 80/20 split). None = no split
            use_jsonl: Use JSONL format instead of JSON
            dataset_name: Name of the dataset
            description: Dataset description
            **options: Additional options
        """
        super().__init__(session, include_metadata, **options)
        self.split_ratio = split_ratio
        self.use_jsonl = use_jsonl
        self.dataset_name = dataset_name
        self.description = description
        
        if split_ratio is not None and not (0 < split_ratio < 1):
            raise ValueError("split_ratio must be between 0 and 1")
    
    def export(
        self,
        query: Query,
        output_path: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Export dataset to Hugging Face format.
        
        Args:
            query: SQLAlchemy query for dataset entries
            output_path: Path to output directory or file
            progress_callback: Optional callback for progress updates
        
        Returns:
            Path to the output directory
        """
        total = self._get_total_count(query)
        logger.info(f"Exporting {total} entries to Hugging Face format")
        
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
        
        # Collect all entries
        all_entries = []
        for idx, entry in enumerate(query.all(), 1):
            converted = self._convert_entry(entry)
            all_entries.append(converted)
            
            # Report progress
            self._report_progress(idx, total, progress_callback)
        
        # Split data if requested
        if self.split_ratio:
            split_idx = int(len(all_entries) * self.split_ratio)
            train_entries = all_entries[:split_idx]
            test_entries = all_entries[split_idx:]
            
            # Write train split
            train_file = self._write_split(
                output_dir,
                'train',
                train_entries
            )
            
            # Write test split
            test_file = self._write_split(
                output_dir,
                'test',
                test_entries
            )
            
            splits = {
                'train': {
                    'name': 'train',
                    'num_examples': len(train_entries),
                    'file': train_file.name
                },
                'test': {
                    'name': 'test',
                    'num_examples': len(test_entries),
                    'file': test_file.name
                }
            }
        else:
            # Write single file
            data_file = self._write_split(
                output_dir,
                'train',
                all_entries
            )
            
            splits = {
                'train': {
                    'name': 'train',
                    'num_examples': len(all_entries),
                    'file': data_file.name
                }
            }
        
        # Create dataset_info.json
        dataset_info = self._create_dataset_info(all_entries, splits)
        info_file = output_dir / 'dataset_info.json'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, indent=2)
        
        logger.info(f"Exported Hugging Face dataset to {output_dir}")
        return str(output_dir)
    
    def _write_split(
        self,
        output_dir: Path,
        split_name: str,
        entries: List[Dict[str, Any]]
    ) -> Path:
        """
        Write a data split to file.
        
        Args:
            output_dir: Output directory
            split_name: Name of the split (train, test, etc.)
            entries: List of entries to write
        
        Returns:
            Path to the written file
        """
        if self.use_jsonl:
            file_path = output_dir / f'{split_name}.jsonl'
            with open(file_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    json_line = json.dumps(entry, ensure_ascii=False)
                    f.write(json_line + '\n')
        else:
            file_path = output_dir / f'{split_name}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def _convert_entry(self, entry: Any) -> Dict[str, Any]:
        """
        Convert entry to Hugging Face format.
        
        Uses a simple format with question and answer fields,
        plus optional metadata.
        
        Args:
            entry: Dataset model instance
        
        Returns:
            Dictionary in Hugging Face format
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
                'tags': entry.tags.split(',') if entry.tags else [],
                'note': entry.note,
            })
        
        return data
    
    def _create_dataset_info(
        self,
        entries: List[Dict[str, Any]],
        splits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create dataset_info.json metadata.
        
        Args:
            entries: Sample entries to infer schema
            splits: Information about data splits
        
        Returns:
            Dataset info dictionary
        """
        # Infer features from first entry
        features = {}
        if entries:
            sample = entries[0]
            for key, value in sample.items():
                if isinstance(value, str):
                    dtype = 'string'
                elif isinstance(value, bool):
                    dtype = 'bool'
                elif isinstance(value, int):
                    dtype = 'int64'
                elif isinstance(value, float):
                    dtype = 'float64'
                elif isinstance(value, list):
                    dtype = 'list'
                else:
                    dtype = 'string'
                
                features[key] = {'dtype': dtype}
        
        # Create dataset info
        dataset_info = {
            'dataset_name': self.dataset_name,
            'description': self.description,
            'version': '1.0.0',
            'features': features,
            'splits': splits,
            'created_at': datetime.utcnow().isoformat(),
            'homepage': 'https://github.com/yourusername/easy-dataset',
            'license': 'AGPL-3.0',
        }
        
        return dataset_info

