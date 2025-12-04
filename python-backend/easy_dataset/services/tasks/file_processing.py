"""File processing task handler."""

import json
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session

from easy_dataset.core.file_processor import get_registry, FileStorageUtil
from easy_dataset.core.text_splitter import TextSplitter
from easy_dataset.models.file import UploadFiles
from easy_dataset.models.chunk import Chunks
from easy_dataset.services.task_service import TaskService


async def process_file_task(
    task_id: str,
    db: Session,
    project_id: str,
    file_path: str,
    file_id: str,
    chunk_config: Dict[str, Any]
) -> None:
    """
    Process uploaded file asynchronously.
    
    This task:
    1. Extracts text from the file using appropriate processor
    2. Splits text into chunks based on configuration
    3. Stores chunks in database
    4. Updates task progress during processing
    
    Args:
        task_id: ID of the task tracking this operation
        db: Database session
        project_id: ID of the project
        file_path: Path to the uploaded file
        file_id: ID of the file record in database
        chunk_config: Configuration for text chunking
            - strategy: 'markdown' | 'delimiter' | 'auto'
            - chunk_size: Size of chunks (for auto strategy)
            - overlap: Overlap between chunks (for auto strategy)
            - delimiter: Custom delimiter (for delimiter strategy)
    
    Raises:
        ValueError: If file processing fails
        IOError: If file cannot be read
    """
    task_service = TaskService(db)
    
    try:
        # Step 1: Extract text from file
        task_service.update_task_progress(
            task_id,
            completed_count=0,
            note="Extracting text from file..."
        )
        
        registry = get_registry()
        file_path_obj = Path(file_path)
        processed_doc = registry.process_file(file_path_obj)
        
        # Step 2: Split text into chunks
        task_service.update_task_progress(
            task_id,
            completed_count=1,
            note="Splitting text into chunks..."
        )
        
        text_splitter = TextSplitter()
        strategy = chunk_config.get('strategy', 'auto')
        
        if strategy == 'markdown':
            chunks = text_splitter.split_by_markdown_headers(processed_doc.content)
        elif strategy == 'delimiter':
            delimiter = chunk_config.get('delimiter', '\n\n')
            chunks = text_splitter.split_by_delimiter(
                processed_doc.content,
                delimiter
            )
        else:  # auto
            chunk_size = chunk_config.get('chunk_size', 1000)
            overlap = chunk_config.get('overlap', 100)
            chunks = text_splitter.split_with_overlap(
                processed_doc.content,
                chunk_size=chunk_size,
                overlap=overlap
            )
        
        # Update total count now that we know how many chunks
        task = task_service.get_task(task_id)
        if task:
            task.total_count = len(chunks) + 2  # +2 for extract and split steps
            db.commit()
        
        # Step 3: Store chunks in database
        task_service.update_task_progress(
            task_id,
            completed_count=2,
            note=f"Storing {len(chunks)} chunks..."
        )
        
        for idx, chunk in enumerate(chunks):
            # Create chunk record
            chunk_record = Chunks(
                project_id=project_id,
                file_id=file_id,
                content=chunk.content if hasattr(chunk, 'content') else str(chunk),
                summary=chunk.summary if hasattr(chunk, 'summary') else "",
                size=chunk.size if hasattr(chunk, 'size') else len(str(chunk)),
                index=idx
            )
            db.add(chunk_record)
            
            # Update progress periodically
            if (idx + 1) % 10 == 0 or idx == len(chunks) - 1:
                task_service.update_task_progress(
                    task_id,
                    completed_count=2 + idx + 1,
                    note=f"Stored {idx + 1}/{len(chunks)} chunks"
                )
                db.commit()
        
        # Final commit
        db.commit()
        
        # Mark task as complete
        task_service.complete_task(
            task_id,
            note=f"Successfully processed file and created {len(chunks)} chunks"
        )
        
    except Exception as e:
        # Mark task as failed
        task_service.fail_task(
            task_id,
            error_message=f"File processing failed: {str(e)}"
        )
        raise
