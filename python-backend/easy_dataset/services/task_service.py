"""Task service for managing background jobs."""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from sqlalchemy.orm import Session
from sqlalchemy import select

from easy_dataset.models.task import Task
from easy_dataset.schemas.task import TaskStatus, TaskCreate, TaskUpdate


class TaskService:
    """
    Service for managing background tasks.
    
    Provides functionality to create, update, track, and cancel tasks.
    Uses database-backed queue for task persistence and recovery.
    
    Attributes:
        db: Database session
        _running_tasks: Dictionary of currently running asyncio tasks
    """
    
    def __init__(self, db: Session):
        """
        Initialize task service.
        
        Args:
            db: Database session
        """
        self.db = db
        self._running_tasks: Dict[str, asyncio.Task] = {}
    
    def create_task(
        self,
        project_id: str,
        task_type: str,
        total_count: int = 0,
        model_info: Optional[Dict[str, Any]] = None,
        language: str = "zh-CN",
        detail: str = "",
        note: str = ""
    ) -> Task:
        """
        Create a new task.
        
        Args:
            project_id: ID of the project this task belongs to
            task_type: Type of task being performed
            total_count: Total number of items to process
            model_info: Model configuration information
            language: Language for generation
            detail: Task details
            note: Task notes
            
        Returns:
            Created task instance
        """
        # Serialize model_info to JSON
        model_info_json = json.dumps(model_info or {})
        
        # Create task instance
        task = Task(
            project_id=project_id,
            task_type=task_type,
            status=TaskStatus.PROCESSING,
            total_count=total_count,
            model_info=model_info_json,
            language=language,
            detail=detail,
            note=note,
            completed_count=0,
            start_time=datetime.utcnow()
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task instance or None if not found
        """
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def list_tasks(
        self,
        project_id: Optional[str] = None,
        task_type: Optional[str] = None,
        status: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        List tasks with optional filtering.
        
        Args:
            project_id: Filter by project ID
            task_type: Filter by task type
            status: Filter by status
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of task instances
        """
        query = self.db.query(Task)
        
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        if status is not None:
            query = query.filter(Task.status == status)
        
        query = query.order_by(Task.create_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def update_task_progress(
        self,
        task_id: str,
        completed_count: int,
        note: str = ""
    ) -> Optional[Task]:
        """
        Update task progress.
        
        Args:
            task_id: Task ID
            completed_count: Number of items completed
            note: Optional note to add
            
        Returns:
            Updated task instance or None if not found
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        task.completed_count = completed_count
        if note:
            task.note = note
        task.update_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def complete_task(
        self,
        task_id: str,
        note: str = ""
    ) -> Optional[Task]:
        """
        Mark task as completed.
        
        Args:
            task_id: Task ID
            note: Optional completion note
            
        Returns:
            Updated task instance or None if not found
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        task.end_time = datetime.utcnow()
        if note:
            task.note = note
        task.update_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        # Remove from running tasks
        if task_id in self._running_tasks:
            del self._running_tasks[task_id]
        
        return task
    
    def fail_task(
        self,
        task_id: str,
        error_message: str
    ) -> Optional[Task]:
        """
        Mark task as failed.
        
        Args:
            task_id: Task ID
            error_message: Error message describing the failure
            
        Returns:
            Updated task instance or None if not found
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        task.status = TaskStatus.FAILED
        task.end_time = datetime.utcnow()
        task.note = error_message
        task.update_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        # Remove from running tasks
        if task_id in self._running_tasks:
            del self._running_tasks[task_id]
        
        return task
    
    def cancel_task(self, task_id: str) -> Optional[Task]:
        """
        Cancel a running task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated task instance or None if not found
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        # Cancel the asyncio task if it's running
        if task_id in self._running_tasks:
            asyncio_task = self._running_tasks[task_id]
            asyncio_task.cancel()
            del self._running_tasks[task_id]
        
        # Update task status
        task.status = TaskStatus.INTERRUPTED
        task.end_time = datetime.utcnow()
        task.note = "Task canceled by user"
        task.update_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    async def run_task_async(
        self,
        task_id: str,
        task_func: Callable,
        *args,
        **kwargs
    ) -> None:
        """
        Run a task asynchronously.
        
        Args:
            task_id: Task ID
            task_func: Async function to execute
            *args: Positional arguments for task_func
            **kwargs: Keyword arguments for task_func
        """
        try:
            # Execute the task function
            await task_func(task_id, *args, **kwargs)
            
            # Mark as completed if not already updated
            task = self.get_task(task_id)
            if task and task.status == TaskStatus.PROCESSING:
                self.complete_task(task_id)
                
        except asyncio.CancelledError:
            # Task was canceled
            self.cancel_task(task_id)
            raise
            
        except Exception as e:
            # Task failed
            self.fail_task(task_id, str(e))
            raise
    
    def start_task_async(
        self,
        task_id: str,
        task_func: Callable,
        *args,
        **kwargs
    ) -> asyncio.Task:
        """
        Start a task asynchronously and track it.
        
        Args:
            task_id: Task ID
            task_func: Async function to execute
            *args: Positional arguments for task_func
            **kwargs: Keyword arguments for task_func
            
        Returns:
            The asyncio Task object
        """
        # Create and store the asyncio task
        asyncio_task = asyncio.create_task(
            self.run_task_async(task_id, task_func, *args, **kwargs)
        )
        self._running_tasks[task_id] = asyncio_task
        
        return asyncio_task
    
    def get_running_tasks(self) -> List[str]:
        """
        Get list of currently running task IDs.
        
        Returns:
            List of task IDs
        """
        return list(self._running_tasks.keys())
    
    def is_task_running(self, task_id: str) -> bool:
        """
        Check if a task is currently running.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task is running, False otherwise
        """
        return task_id in self._running_tasks
    
    def recover_interrupted_tasks(self) -> List[Task]:
        """
        Recover tasks that were interrupted (e.g., due to server restart).
        
        Finds tasks with PROCESSING status and marks them as INTERRUPTED.
        
        Returns:
            List of recovered tasks
        """
        # Find all tasks still marked as processing
        interrupted_tasks = self.db.query(Task).filter(
            Task.status == TaskStatus.PROCESSING
        ).all()
        
        # Mark them as interrupted
        for task in interrupted_tasks:
            task.status = TaskStatus.INTERRUPTED
            task.end_time = datetime.utcnow()
            task.note = "Task interrupted due to server restart"
            task.update_at = datetime.utcnow()
        
        if interrupted_tasks:
            self.db.commit()
        
        return interrupted_tasks
