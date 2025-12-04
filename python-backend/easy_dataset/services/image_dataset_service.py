"""Image dataset management service."""

import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from easy_dataset.models.image import Images
from easy_dataset.models.image_dataset import ImageDatasets
from easy_dataset.models.project import Projects
from easy_dataset.models.question import Questions

logger = logging.getLogger(__name__)


class ImageDatasetService:
    """
    Service for managing image datasets with QA pairs.
    
    Features:
    - Create image datasets with QA pairs
    - Store image references and answers
    - Support different answer types (text, labels, custom)
    - Filter and search datasets
    - Update and delete entries
    """
    
    # Supported answer types
    ANSWER_TYPES = {"text", "label", "custom_format"}
    
    def __init__(self, db_session: Session):
        """
        Initialize image dataset service.
        
        Args:
            db_session: Database session
        """
        self.db = db_session
    
    def validate_answer_type(self, answer_type: str) -> bool:
        """
        Validate answer type.
        
        Args:
            answer_type: Answer type to validate
            
        Returns:
            True if valid
        """
        return answer_type in self.ANSWER_TYPES
    
    def format_label_answer(self, labels: List[str]) -> str:
        """
        Format label answer as JSON array.
        
        Args:
            labels: List of label strings
            
        Returns:
            JSON string
        """
        return json.dumps(labels)
    
    def parse_label_answer(self, answer: str) -> List[str]:
        """
        Parse label answer from JSON.
        
        Args:
            answer: JSON string
            
        Returns:
            List of labels
        """
        try:
            labels = json.loads(answer)
            if isinstance(labels, list):
                return [str(label) for label in labels]
            return []
        except json.JSONDecodeError:
            return []
    
    def create_dataset_entry(
        self,
        project_id: str,
        image_id: str,
        question: str,
        answer: str,
        model: str,
        answer_type: str = "text",
        question_id: Optional[str] = None,
        tags: str = "",
        note: str = "",
        score: float = 0.0,
        confirmed: bool = False
    ) -> ImageDatasets:
        """
        Create an image dataset entry.
        
        Args:
            project_id: Project ID
            image_id: Image ID
            question: Question text
            answer: Answer text (format depends on answer_type)
            model: Model used to generate answer
            answer_type: Type of answer (text, label, custom_format)
            question_id: Optional question ID reference
            tags: Comma-separated tags
            note: User notes
            score: Quality score (0-5)
            confirmed: Whether entry is confirmed
            
        Returns:
            Created ImageDatasets instance
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If project or image not found
        """
        # Validate project
        project = self.db.query(Projects).filter(
            Projects.id == project_id
        ).first()
        
        if not project:
            raise RuntimeError(f"Project not found: {project_id}")
        
        # Validate image
        image = self.db.query(Images).filter(
            Images.id == image_id
        ).first()
        
        if not image:
            raise RuntimeError(f"Image not found: {image_id}")
        
        # Validate answer type
        if not self.validate_answer_type(answer_type):
            raise ValueError(
                f"Invalid answer type: {answer_type}. "
                f"Supported types: {', '.join(self.ANSWER_TYPES)}"
            )
        
        # Create dataset entry
        dataset_entry = ImageDatasets(
            project_id=project_id,
            image_id=image_id,
            image_name=image.image_name,
            question_id=question_id,
            question=question,
            answer=answer,
            answer_type=answer_type,
            model=model,
            confirmed=confirmed,
            score=score,
            tags=tags,
            note=note
        )
        
        self.db.add(dataset_entry)
        self.db.commit()
        self.db.refresh(dataset_entry)
        
        logger.info(
            f"Created image dataset entry: {dataset_entry.id} "
            f"(image: {image.image_name}, type: {answer_type})"
        )
        
        return dataset_entry
    
    def create_from_question(
        self,
        question_id: str,
        answer: str,
        model: str,
        answer_type: str = "text",
        **kwargs
    ) -> ImageDatasets:
        """
        Create dataset entry from existing question.
        
        Args:
            question_id: Question ID
            answer: Answer text
            model: Model used
            answer_type: Answer type
            **kwargs: Additional fields
            
        Returns:
            Created ImageDatasets instance
            
        Raises:
            RuntimeError: If question not found or has no image
        """
        # Get question
        question = self.db.query(Questions).filter(
            Questions.id == question_id
        ).first()
        
        if not question:
            raise RuntimeError(f"Question not found: {question_id}")
        
        if not question.image_id:
            raise RuntimeError(f"Question {question_id} is not linked to an image")
        
        # Create dataset entry
        return self.create_dataset_entry(
            project_id=question.project_id,
            image_id=question.image_id,
            question=question.question,
            answer=answer,
            model=model,
            answer_type=answer_type,
            question_id=question_id,
            **kwargs
        )
    
    def get_dataset_entry(self, entry_id: str) -> Optional[ImageDatasets]:
        """
        Get dataset entry by ID.
        
        Args:
            entry_id: Dataset entry ID
            
        Returns:
            ImageDatasets instance or None
        """
        return self.db.query(ImageDatasets).filter(
            ImageDatasets.id == entry_id
        ).first()
    
    def list_dataset_entries(
        self,
        project_id: str,
        image_id: Optional[str] = None,
        answer_type: Optional[str] = None,
        confirmed: Optional[bool] = None,
        min_score: Optional[float] = None,
        tags: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ImageDatasets]:
        """
        List image dataset entries with filtering.
        
        Args:
            project_id: Project ID
            image_id: Optional image ID filter
            answer_type: Optional answer type filter
            confirmed: Optional confirmed status filter
            min_score: Optional minimum score filter
            tags: Optional list of tags to filter by
            search_query: Optional search query for question/answer
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of ImageDatasets instances
        """
        query = self.db.query(ImageDatasets).filter(
            ImageDatasets.project_id == project_id
        )
        
        # Apply filters
        if image_id:
            query = query.filter(ImageDatasets.image_id == image_id)
        
        if answer_type:
            query = query.filter(ImageDatasets.answer_type == answer_type)
        
        if confirmed is not None:
            query = query.filter(ImageDatasets.confirmed == confirmed)
        
        if min_score is not None:
            query = query.filter(ImageDatasets.score >= min_score)
        
        if tags:
            # Filter by tags (comma-separated in database)
            tag_filters = [
                ImageDatasets.tags.contains(tag) for tag in tags
            ]
            query = query.filter(or_(*tag_filters))
        
        if search_query:
            # Search in question and answer
            search_filter = or_(
                ImageDatasets.question.contains(search_query),
                ImageDatasets.answer.contains(search_query)
            )
            query = query.filter(search_filter)
        
        # Order by creation date (newest first)
        query = query.order_by(ImageDatasets.create_at.desc())
        
        # Apply pagination
        return query.limit(limit).offset(offset).all()
    
    def update_dataset_entry(
        self,
        entry_id: str,
        **updates
    ) -> Optional[ImageDatasets]:
        """
        Update dataset entry.
        
        Args:
            entry_id: Dataset entry ID
            **updates: Fields to update
            
        Returns:
            Updated ImageDatasets instance or None
        """
        entry = self.get_dataset_entry(entry_id)
        
        if not entry:
            return None
        
        # Update allowed fields
        allowed_fields = {
            "question", "answer", "answer_type", "model",
            "confirmed", "score", "tags", "note"
        }
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(entry, field):
                setattr(entry, field, value)
        
        self.db.commit()
        self.db.refresh(entry)
        
        logger.info(f"Updated image dataset entry: {entry_id}")
        
        return entry
    
    def delete_dataset_entry(self, entry_id: str) -> bool:
        """
        Delete dataset entry.
        
        Args:
            entry_id: Dataset entry ID
            
        Returns:
            True if deleted, False if not found
        """
        entry = self.get_dataset_entry(entry_id)
        
        if not entry:
            return False
        
        self.db.delete(entry)
        self.db.commit()
        
        logger.info(f"Deleted image dataset entry: {entry_id}")
        
        return True
    
    def batch_create_from_questions(
        self,
        question_ids: List[str],
        answers: List[str],
        model: str,
        answer_type: str = "text",
        **common_kwargs
    ) -> List[ImageDatasets]:
        """
        Batch create dataset entries from questions.
        
        Args:
            question_ids: List of question IDs
            answers: List of answers (same length as question_ids)
            model: Model used
            answer_type: Answer type
            **common_kwargs: Common fields for all entries
            
        Returns:
            List of created ImageDatasets instances
            
        Raises:
            ValueError: If lengths don't match
        """
        if len(question_ids) != len(answers):
            raise ValueError("question_ids and answers must have same length")
        
        created_entries = []
        
        for question_id, answer in zip(question_ids, answers):
            try:
                entry = self.create_from_question(
                    question_id=question_id,
                    answer=answer,
                    model=model,
                    answer_type=answer_type,
                    **common_kwargs
                )
                created_entries.append(entry)
            except Exception as e:
                logger.error(f"Failed to create entry for question {question_id}: {e}")
        
        logger.info(f"Batch created {len(created_entries)} image dataset entries")
        
        return created_entries
    
    def get_dataset_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get statistics for image datasets in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with statistics
        """
        entries = self.list_dataset_entries(project_id, limit=10000)
        
        # Count by answer type
        type_counts = {}
        for entry in entries:
            type_counts[entry.answer_type] = type_counts.get(entry.answer_type, 0) + 1
        
        # Count confirmed
        confirmed_count = sum(1 for e in entries if e.confirmed)
        
        # Average score
        scores = [e.score for e in entries if e.score > 0]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "total_entries": len(entries),
            "confirmed_entries": confirmed_count,
            "unconfirmed_entries": len(entries) - confirmed_count,
            "average_score": round(avg_score, 2),
            "by_answer_type": type_counts,
            "unique_images": len(set(e.image_id for e in entries))
        }
    
    def get_entries_by_image(
        self,
        image_id: str,
        limit: int = 100
    ) -> List[ImageDatasets]:
        """
        Get all dataset entries for a specific image.
        
        Args:
            image_id: Image ID
            limit: Maximum results
            
        Returns:
            List of ImageDatasets instances
        """
        return self.db.query(ImageDatasets).filter(
            ImageDatasets.image_id == image_id
        ).order_by(
            ImageDatasets.create_at.desc()
        ).limit(limit).all()
    
    def confirm_entry(self, entry_id: str, confirmed: bool = True) -> Optional[ImageDatasets]:
        """
        Confirm or unconfirm a dataset entry.
        
        Args:
            entry_id: Dataset entry ID
            confirmed: Confirmation status
            
        Returns:
            Updated ImageDatasets instance or None
        """
        return self.update_dataset_entry(entry_id, confirmed=confirmed)
    
    def rate_entry(self, entry_id: str, score: float) -> Optional[ImageDatasets]:
        """
        Rate a dataset entry.
        
        Args:
            entry_id: Dataset entry ID
            score: Score (0-5)
            
        Returns:
            Updated ImageDatasets instance or None
            
        Raises:
            ValueError: If score is out of range
        """
        if not 0 <= score <= 5:
            raise ValueError("Score must be between 0 and 5")
        
        return self.update_dataset_entry(entry_id, score=score)
    
    def add_tags(self, entry_id: str, new_tags: List[str]) -> Optional[ImageDatasets]:
        """
        Add tags to a dataset entry.
        
        Args:
            entry_id: Dataset entry ID
            new_tags: List of tags to add
            
        Returns:
            Updated ImageDatasets instance or None
        """
        entry = self.get_dataset_entry(entry_id)
        
        if not entry:
            return None
        
        # Parse existing tags
        existing_tags = [t.strip() for t in entry.tags.split(",") if t.strip()]
        
        # Add new tags (avoid duplicates)
        for tag in new_tags:
            tag = tag.strip()
            if tag and tag not in existing_tags:
                existing_tags.append(tag)
        
        # Update tags
        entry.tags = ", ".join(existing_tags)
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
