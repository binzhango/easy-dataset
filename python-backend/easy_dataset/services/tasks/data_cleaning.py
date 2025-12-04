"""Data cleaning task handler."""

import re
from typing import List, Set
from sqlalchemy.orm import Session

from easy_dataset.models.dataset import Datasets
from easy_dataset.services.task_service import TaskService


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    - Removes leading/trailing whitespace
    - Replaces multiple spaces with single space
    - Normalizes line breaks
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    
    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def remove_duplicate_punctuation(text: str) -> str:
    """
    Remove duplicate punctuation marks.
    
    Args:
        text: Text to clean
        
    Returns:
        Text with duplicate punctuation removed
    """
    # Remove duplicate periods, commas, etc.
    text = re.sub(r'\.\.+', '.', text)
    text = re.sub(r',,+', ',', text)
    text = re.sub(r'!!+', '!', text)
    text = re.sub(r'\?\?+', '?', text)
    text = re.sub(r';;+', ';', text)
    text = re.sub(r'::+', ':', text)
    
    return text


def fix_spacing_around_punctuation(text: str) -> str:
    """
    Fix spacing around punctuation marks.
    
    Args:
        text: Text to fix
        
    Returns:
        Text with proper spacing
    """
    # Remove space before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Add space after punctuation if missing (except at end of string)
    text = re.sub(r'([.,!?;:])([^\s\n])', r'\1 \2', text)
    
    return text


def clean_text(text: str) -> str:
    """
    Apply all text cleaning operations.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    text = normalize_whitespace(text)
    text = remove_duplicate_punctuation(text)
    text = fix_spacing_around_punctuation(text)
    return text


def find_duplicate_entries(
    db: Session,
    project_id: str
) -> List[tuple[str, List[str]]]:
    """
    Find duplicate dataset entries based on question text.
    
    Args:
        db: Database session
        project_id: Project ID to search within
        
    Returns:
        List of tuples (question_text, [list of duplicate entry IDs])
    """
    # Get all dataset entries for project
    entries = db.query(Datasets).filter(
        Datasets.project_id == project_id
    ).all()
    
    # Group by question text
    question_groups: dict[str, List[str]] = {}
    for entry in entries:
        normalized_question = entry.question.strip().lower()
        if normalized_question not in question_groups:
            question_groups[normalized_question] = []
        question_groups[normalized_question].append(entry.id)
    
    # Find duplicates (groups with more than one entry)
    duplicates = [
        (question, ids)
        for question, ids in question_groups.items()
        if len(ids) > 1
    ]
    
    return duplicates


async def process_data_cleaning_task(
    task_id: str,
    db: Session,
    project_id: str,
    config: dict
) -> None:
    """
    Process data cleaning task asynchronously.
    
    This task:
    1. Normalizes whitespace in questions and answers
    2. Fixes formatting issues (punctuation, spacing)
    3. Optionally removes duplicate entries
    4. Updates task progress during processing
    
    Args:
        task_id: ID of the task tracking this operation
        db: Database session
        project_id: ID of the project
        config: Configuration containing:
            - remove_duplicates: Whether to remove duplicate entries (default: False)
            - keep_first: If removing duplicates, keep first occurrence (default: True)
    
    Raises:
        ValueError: If data cleaning fails
    """
    task_service = TaskService(db)
    
    try:
        # Get all dataset entries for project
        entries = db.query(Datasets).filter(
            Datasets.project_id == project_id
        ).all()
        
        if not entries:
            task_service.complete_task(
                task_id,
                note="No dataset entries found to clean"
            )
            return
        
        # Update total count
        task = task_service.get_task(task_id)
        if task:
            task.total_count = len(entries)
            db.commit()
        
        # Step 1: Clean text in all entries
        task_service.update_task_progress(
            task_id,
            completed_count=0,
            note="Cleaning text formatting..."
        )
        
        cleaned_count = 0
        for idx, entry in enumerate(entries):
            # Clean question
            original_question = entry.question
            entry.question = clean_text(entry.question)
            
            # Clean answer
            original_answer = entry.answer
            entry.answer = clean_text(entry.answer)
            
            # Clean chunk content
            original_chunk = entry.chunk_content
            entry.chunk_content = clean_text(entry.chunk_content)
            
            # Track if anything changed
            if (entry.question != original_question or
                entry.answer != original_answer or
                entry.chunk_content != original_chunk):
                cleaned_count += 1
            
            # Update progress periodically
            if (idx + 1) % 10 == 0 or idx == len(entries) - 1:
                task_service.update_task_progress(
                    task_id,
                    completed_count=idx + 1,
                    note=f"Cleaned {idx + 1}/{len(entries)} entries"
                )
                db.commit()
        
        # Step 2: Remove duplicates if requested
        remove_duplicates = config.get('remove_duplicates', False)
        removed_count = 0
        
        if remove_duplicates:
            task_service.update_task_progress(
                task_id,
                completed_count=len(entries),
                note="Finding and removing duplicates..."
            )
            
            duplicates = find_duplicate_entries(db, project_id)
            keep_first = config.get('keep_first', True)
            
            for question_text, duplicate_ids in duplicates:
                # Keep first or last entry, remove others
                if keep_first:
                    ids_to_remove = duplicate_ids[1:]
                else:
                    ids_to_remove = duplicate_ids[:-1]
                
                # Delete duplicate entries
                db.query(Datasets).filter(
                    Datasets.id.in_(ids_to_remove)
                ).delete(synchronize_session=False)
                
                removed_count += len(ids_to_remove)
            
            db.commit()
        
        # Mark task as complete
        note = f"Cleaned {cleaned_count} entries"
        if remove_duplicates:
            note += f", removed {removed_count} duplicates"
        
        task_service.complete_task(task_id, note=note)
        
    except Exception as e:
        # Mark task as failed
        task_service.fail_task(
            task_id,
            error_message=f"Data cleaning failed: {str(e)}"
        )
        raise
