"""
EasyDataset - Main facade class for the Easy Dataset package.

This class provides a unified interface for all Easy Dataset functionality,
making it easy to use the package programmatically without a web framework.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class EasyDataset:
    """
    Main interface for Easy Dataset functionality.
    
    This facade class provides a simple, unified API for:
    - Project management (create, get, update, delete)
    - File processing (upload and extract text)
    - Question generation from text chunks
    - Answer generation for questions
    - Dataset management and export
    - LLM provider configuration
    
    Example:
        >>> from easy_dataset import EasyDataset
        >>> dataset = EasyDataset(database_url="sqlite:///my_dataset.db")
        >>> 
        >>> # Configure LLM
        >>> dataset.configure_llm({
        ...     "provider": "openai",
        ...     "api_key": "sk-...",
        ...     "model": "gpt-4"
        ... })
        >>> 
        >>> # Create a project
        >>> project = dataset.create_project(
        ...     name="My Project",
        ...     description="Dataset for fine-tuning"
        ... )
        >>> 
        >>> # Process a file
        >>> chunks = dataset.process_file(project.id, "document.pdf")
        >>> 
        >>> # Generate questions
        >>> questions = dataset.generate_questions(
        ...     project_id=project.id,
        ...     chunk_ids=[chunk.id for chunk in chunks]
        ... )
        >>> 
        >>> # Generate answers
        >>> answers = dataset.generate_answers(
        ...     project_id=project.id,
        ...     question_ids=[q.id for q in questions]
        ... )
        >>> 
        >>> # Export dataset
        >>> dataset.export_dataset(
        ...     project_id=project.id,
        ...     format="json",
        ...     output_path="dataset.json"
        ... )
    """
    
    def __init__(
        self,
        database_url: str = "sqlite:///easy_dataset.db",
        **kwargs
    ):
        """
        Initialize the EasyDataset instance.
        
        Args:
            database_url: SQLAlchemy database URL. Defaults to SQLite in current directory.
            **kwargs: Additional configuration options.
        """
        self.database_url = database_url
        self.config = kwargs
        self._session: Optional[Session] = None
        self._llm_client = None
        
        logger.info(f"Initializing EasyDataset with database: {database_url}")
        
        # Initialize database connection (will be implemented in task 3.1)
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and session."""
        from easy_dataset.database import init_database, get_session_factory
        
        # Initialize database tables if they don't exist
        init_database(self.database_url)
        
        # Create session factory
        session_factory = get_session_factory(self.database_url)
        self._session = session_factory()
        
        logger.debug(f"Database initialized: {self.database_url}")
    
    def _get_session(self) -> Session:
        """
        Get or create a database session.
        
        Returns:
            SQLAlchemy Session instance.
        """
        if self._session is None:
            self._init_database()
        return self._session
    
    # ========================================================================
    # LLM Configuration
    # ========================================================================
    
    def configure_llm(self, config: Dict[str, Any]) -> None:
        """
        Configure the LLM provider for question and answer generation.
        
        Args:
            config: LLM configuration dictionary containing:
                - provider: Provider name (openai, ollama, gemini, etc.)
                - api_key: API key for the provider (if required)
                - model: Model name to use
                - endpoint: Custom endpoint URL (optional)
                - temperature: Temperature for generation (optional)
                - max_tokens: Maximum tokens to generate (optional)
        
        Example:
            >>> dataset.configure_llm({
            ...     "provider": "openai",
            ...     "api_key": "sk-...",
            ...     "model": "gpt-4",
            ...     "temperature": 0.7
            ... })
        """
        # This will be implemented when LLM integration is created (task 8)
        logger.info(f"Configuring LLM provider: {config.get('provider')}")
        self._llm_config = config
        # Actual provider initialization will happen in task 8
        logger.debug("LLM configuration stored - provider initialization in task 8")
    
    def get_llm_client(self):
        """
        Get the configured LLM client.
        
        Returns:
            Configured LLM client instance.
            
        Raises:
            ValueError: If LLM has not been configured.
        """
        if self._llm_client is None:
            raise ValueError(
                "LLM not configured. Call configure_llm() first."
            )
        return self._llm_client
    
    # ========================================================================
    # Project Management
    # ========================================================================
    
    def create_project(
        self,
        name: str,
        description: str = "",
        **kwargs
    ) -> Any:  # Will return Project model once implemented
        """
        Create a new project.
        
        A project is a container for all related documents, chunks, questions,
        and datasets. It allows you to organize your work and maintain separate
        configurations for different use cases.
        
        Args:
            name: Project name (required)
            description: Project description (optional)
            **kwargs: Additional project configuration:
                - global_prompt: Global prompt template
                - question_prompt: Question generation prompt template
                - answer_prompt: Answer generation prompt template
                - default_model_config_id: Default LLM model configuration
        
        Returns:
            Created Project instance with generated ID.
            
        Example:
            >>> project = dataset.create_project(
            ...     name="Medical QA Dataset",
            ...     description="Dataset for medical question answering",
            ...     global_prompt="You are a medical expert..."
            ... )
            >>> print(project.id)
            'abc123def456'
        """
        # This will be implemented when Project model is created (task 3.2)
        logger.info(f"Creating project: {name}")
        raise NotImplementedError(
            "Project creation not yet implemented. "
            "This will be available after task 3.2 is completed."
        )
    
    def get_project(self, project_id: str) -> Any:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID to retrieve.
            
        Returns:
            Project instance if found, None otherwise.
            
        Example:
            >>> project = dataset.get_project("abc123def456")
            >>> print(project.name)
            'Medical QA Dataset'
        """
        # This will be implemented when Project model is created (task 3.2)
        logger.debug(f"Getting project: {project_id}")
        raise NotImplementedError(
            "Project retrieval not yet implemented. "
            "This will be available after task 3.2 is completed."
        )
    
    def list_projects(
        self,
        limit: int = 100,
        offset: int = 0,
        **filters
    ) -> List[Any]:
        """
        List all projects with optional filtering.
        
        Args:
            limit: Maximum number of projects to return.
            offset: Number of projects to skip (for pagination).
            **filters: Additional filter criteria.
            
        Returns:
            List of Project instances.
            
        Example:
            >>> projects = dataset.list_projects(limit=10)
            >>> for project in projects:
            ...     print(f"{project.name}: {len(project.chunks)} chunks")
        """
        # This will be implemented when Project model is created (task 3.2)
        logger.debug(f"Listing projects (limit={limit}, offset={offset})")
        raise NotImplementedError(
            "Project listing not yet implemented. "
            "This will be available after task 3.2 is completed."
        )
    
    def update_project(
        self,
        project_id: str,
        **updates
    ) -> Any:
        """
        Update a project's properties.
        
        Args:
            project_id: Project ID to update.
            **updates: Fields to update (name, description, prompts, etc.)
            
        Returns:
            Updated Project instance.
            
        Example:
            >>> project = dataset.update_project(
            ...     "abc123def456",
            ...     description="Updated description",
            ...     global_prompt="New prompt template"
            ... )
        """
        # This will be implemented when Project model is created (task 3.2)
        logger.info(f"Updating project: {project_id}")
        raise NotImplementedError(
            "Project update not yet implemented. "
            "This will be available after task 3.2 is completed."
        )
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project and all associated data.
        
        Warning: This will delete all chunks, questions, datasets, and other
        data associated with the project. This operation cannot be undone.
        
        Args:
            project_id: Project ID to delete.
            
        Returns:
            True if deleted successfully, False otherwise.
            
        Example:
            >>> success = dataset.delete_project("abc123def456")
            >>> if success:
            ...     print("Project deleted")
        """
        # This will be implemented when Project model is created (task 3.2)
        logger.warning(f"Deleting project: {project_id}")
        raise NotImplementedError(
            "Project deletion not yet implemented. "
            "This will be available after task 3.2 is completed."
        )
    
    # ========================================================================
    # File Processing
    # ========================================================================
    
    def process_file(
        self,
        project_id: str,
        file_path: str,
        **options
    ) -> List[Any]:  # Will return List[Chunk] once implemented
        """
        Process a file and create text chunks.
        
        This method handles file upload, text extraction, and chunking in one step.
        Supported formats: PDF, DOCX, EPUB, Markdown, TXT.
        
        Args:
            project_id: Project ID to associate chunks with.
            file_path: Path to the file to process.
            **options: Processing options:
                - chunk_size: Maximum chunk size in characters
                - chunk_overlap: Overlap between chunks in characters
                - split_by: Splitting strategy ('markdown', 'delimiter', 'auto')
                - delimiter: Custom delimiter for splitting (if split_by='delimiter')
                
        Returns:
            List of created Chunk instances.
            
        Example:
            >>> chunks = dataset.process_file(
            ...     project_id="abc123",
            ...     file_path="document.pdf",
            ...     chunk_size=1000,
            ...     chunk_overlap=100
            ... )
            >>> print(f"Created {len(chunks)} chunks")
        """
        # This will be implemented when file processing is created (task 6)
        logger.info(f"Processing file: {file_path} for project {project_id}")
        raise NotImplementedError(
            "File processing not yet implemented. "
            "This will be available after task 6 is completed."
        )
    
    def upload_file(
        self,
        project_id: str,
        file_path: str,
        **metadata
    ) -> Any:  # Will return UploadFile once implemented
        """
        Upload a file without processing it immediately.
        
        This creates a file record in the database but doesn't extract text
        or create chunks. Use process_file() for immediate processing.
        
        Args:
            project_id: Project ID to associate file with.
            file_path: Path to the file to upload.
            **metadata: Additional file metadata.
            
        Returns:
            Created UploadFile instance.
            
        Example:
            >>> file = dataset.upload_file(
            ...     project_id="abc123",
            ...     file_path="document.pdf"
            ... )
            >>> print(f"Uploaded: {file.file_name}")
        """
        # This will be implemented when file processing is created (task 6)
        logger.info(f"Uploading file: {file_path} for project {project_id}")
        raise NotImplementedError(
            "File upload not yet implemented. "
            "This will be available after task 6 is completed."
        )
    
    # ========================================================================
    # Question Generation
    # ========================================================================
    
    def generate_questions(
        self,
        project_id: str,
        chunk_ids: Optional[List[str]] = None,
        **options
    ) -> List[Any]:  # Will return List[Question] once implemented
        """
        Generate questions from text chunks using LLM.
        
        Args:
            project_id: Project ID containing the chunks.
            chunk_ids: List of chunk IDs to generate questions from.
                      If None, generates for all chunks in project.
            **options: Generation options:
                - num_questions: Number of questions per chunk (default: 1)
                - question_type: Type of questions to generate
                - language: Language for questions (default: 'en')
                - custom_prompt: Custom prompt template
                - batch_size: Number of chunks to process concurrently
                
        Returns:
            List of generated Question instances.
            
        Example:
            >>> questions = dataset.generate_questions(
            ...     project_id="abc123",
            ...     chunk_ids=["chunk1", "chunk2"],
            ...     num_questions=3,
            ...     language="en"
            ... )
            >>> for q in questions:
            ...     print(q.question)
        """
        # This will be implemented when question generation is created (task 10.4)
        logger.info(
            f"Generating questions for project {project_id}, "
            f"chunks: {len(chunk_ids) if chunk_ids else 'all'}"
        )
        raise NotImplementedError(
            "Question generation not yet implemented. "
            "This will be available after task 10.4 is completed."
        )
    
    # ========================================================================
    # Answer Generation
    # ========================================================================
    
    def generate_answers(
        self,
        project_id: str,
        question_ids: Optional[List[str]] = None,
        **options
    ) -> List[Any]:  # Will return List[Dataset] once implemented
        """
        Generate answers for questions using LLM.
        
        Args:
            project_id: Project ID containing the questions.
            question_ids: List of question IDs to generate answers for.
                         If None, generates for all unanswered questions.
            **options: Generation options:
                - include_thinking: Include chain-of-thought reasoning
                - language: Language for answers (default: 'en')
                - custom_prompt: Custom prompt template
                - batch_size: Number of questions to process concurrently
                
        Returns:
            List of created Dataset entries (question-answer pairs).
            
        Example:
            >>> answers = dataset.generate_answers(
            ...     project_id="abc123",
            ...     question_ids=["q1", "q2"],
            ...     include_thinking=True
            ... )
            >>> for entry in answers:
            ...     print(f"Q: {entry.question}")
            ...     print(f"A: {entry.answer}")
        """
        # This will be implemented when answer generation is created (task 10.6)
        logger.info(
            f"Generating answers for project {project_id}, "
            f"questions: {len(question_ids) if question_ids else 'all'}"
        )
        raise NotImplementedError(
            "Answer generation not yet implemented. "
            "This will be available after task 10.6 is completed."
        )
    
    # ========================================================================
    # Dataset Management
    # ========================================================================
    
    def create_dataset_entry(
        self,
        project_id: str,
        question: str,
        answer: str,
        **metadata
    ) -> Any:  # Will return Dataset once implemented
        """
        Create a dataset entry (question-answer pair) manually.
        
        Args:
            project_id: Project ID to associate entry with.
            question: Question text.
            answer: Answer text.
            **metadata: Additional metadata (tags, rating, notes, etc.)
            
        Returns:
            Created Dataset instance.
            
        Example:
            >>> entry = dataset.create_dataset_entry(
            ...     project_id="abc123",
            ...     question="What is Python?",
            ...     answer="Python is a programming language.",
            ...     tags=["programming", "basics"],
            ...     rating=5
            ... )
        """
        # This will be implemented when dataset models are created (task 3.3)
        logger.info(f"Creating dataset entry for project {project_id}")
        raise NotImplementedError(
            "Dataset entry creation not yet implemented. "
            "This will be available after task 3.3 is completed."
        )
    
    def list_dataset_entries(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
        **filters
    ) -> List[Any]:
        """
        List dataset entries with optional filtering.
        
        Args:
            project_id: Project ID to list entries from.
            limit: Maximum number of entries to return.
            offset: Number of entries to skip (for pagination).
            **filters: Filter criteria (tags, rating, etc.)
            
        Returns:
            List of Dataset instances.
            
        Example:
            >>> entries = dataset.list_dataset_entries(
            ...     project_id="abc123",
            ...     tags=["important"],
            ...     rating__gte=4
            ... )
        """
        # This will be implemented when dataset models are created (task 3.3)
        logger.debug(f"Listing dataset entries for project {project_id}")
        raise NotImplementedError(
            "Dataset entry listing not yet implemented. "
            "This will be available after task 3.3 is completed."
        )
    
    # ========================================================================
    # Dataset Export
    # ========================================================================
    
    def export_dataset(
        self,
        project_id: str,
        format: str = "json",
        output_path: Optional[str] = None,
        **options
    ) -> str:
        """
        Export dataset to a file in the specified format.
        
        Supported formats:
        - json: Standard JSON format
        - jsonl: JSON Lines format (one object per line)
        - csv: Comma-separated values
        - huggingface: Hugging Face datasets format
        - llamafactory: LLaMA Factory format
        
        Args:
            project_id: Project ID to export dataset from.
            format: Export format (json, jsonl, csv, huggingface, llamafactory)
            output_path: Path to save the exported file. If None, returns data as string.
            **options: Format-specific options:
                - include_metadata: Include metadata in export
                - filter_tags: Only export entries with specific tags
                - min_rating: Only export entries with rating >= this value
                - confirmed_only: Only export confirmed entries
                - progress_callback: Callback function for progress updates
                
        Returns:
            Path to the exported file, or the exported data as a string.
            
        Example:
            >>> path = dataset.export_dataset(
            ...     project_id="abc123",
            ...     format="json",
            ...     output_path="dataset.json",
            ...     min_rating=4
            ... )
            >>> print(f"Exported to: {path}")
        """
        from easy_dataset.services.exporter import DatasetExporterService
        
        logger.info(
            f"Exporting dataset for project {project_id} "
            f"to format: {format}"
        )
        
        # Create exporter service
        exporter = DatasetExporterService(self.session)
        
        # Export dataset
        result = exporter.export(
            project_id=project_id,
            format=format,
            output_path=output_path,
            **options
        )
        
        logger.info(f"Export completed: {result}")
        return result
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def get_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get statistics for a project.
        
        Args:
            project_id: Project ID to get stats for.
            
        Returns:
            Dictionary containing project statistics:
            - num_files: Number of uploaded files
            - num_chunks: Number of text chunks
            - num_questions: Number of generated questions
            - num_answers: Number of generated answers
            - num_dataset_entries: Number of dataset entries
            
        Example:
            >>> stats = dataset.get_stats("abc123")
            >>> print(f"Chunks: {stats['num_chunks']}")
            >>> print(f"Questions: {stats['num_questions']}")
        """
        # This will be implemented when models are created (task 3)
        logger.debug(f"Getting stats for project {project_id}")
        raise NotImplementedError(
            "Statistics not yet implemented. "
            "This will be available after task 3 is completed."
        )
    
    def close(self):
        """
        Close database connections and clean up resources.
        
        Call this when you're done using the EasyDataset instance,
        especially in long-running applications.
        
        Example:
            >>> dataset = EasyDataset()
            >>> try:
            ...     # Use dataset
            ...     pass
            ... finally:
            ...     dataset.close()
        """
        if self._session:
            self._session.close()
            self._session = None
        logger.info("EasyDataset instance closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False
