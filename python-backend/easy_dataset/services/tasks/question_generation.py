"""Question generation task handler."""

import json
import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from easy_dataset.llm.service import LLMService
from easy_dataset.llm.prompts.question_prompts import get_question_prompt
from easy_dataset.models.chunk import Chunks
from easy_dataset.models.question import Questions
from easy_dataset.services.task_service import TaskService


async def generate_questions_for_chunk(
    llm_service: LLMService,
    chunk: Chunks,
    config: Dict[str, Any]
) -> List[str]:
    """
    Generate questions for a single chunk.
    
    Args:
        llm_service: LLM service instance
        chunk: Chunk to generate questions from
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for generation
            - questions_per_chunk: Number of questions to generate
            - active_ga_pair: Optional genre-audience pair
            - custom_prompt: Optional custom prompt template
    
    Returns:
        List of generated question strings
    """
    # Get provider
    provider = llm_service.create_provider(config['provider_config'])
    
    # Build prompt
    prompt = get_question_prompt(
        language=config.get('language', 'zh-CN'),
        text=chunk.content,
        number=config.get('questions_per_chunk'),
        active_ga_pair=config.get('active_ga_pair'),
        custom_prompt=config.get('custom_prompt')
    )
    
    # Generate questions
    messages = [{"role": "user", "content": prompt}]
    response = await provider.chat(messages)
    
    # Parse response - expecting JSON array of questions
    content = response.get('content', '[]')
    
    # Try to extract JSON from markdown code blocks if present
    if '```json' in content:
        start = content.find('```json') + 7
        end = content.find('```', start)
        content = content[start:end].strip()
    elif '```' in content:
        start = content.find('```') + 3
        end = content.find('```', start)
        content = content[start:end].strip()
    
    try:
        questions = json.loads(content)
        if isinstance(questions, list):
            return [str(q) for q in questions if q]
        return []
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract questions line by line
        lines = content.strip().split('\n')
        questions = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                # Remove common prefixes
                for prefix in ['- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ']:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                        break
                if line:
                    questions.append(line)
        return questions


async def process_question_generation_task(
    task_id: str,
    db: Session,
    project_id: str,
    chunk_ids: List[str],
    config: Dict[str, Any]
) -> None:
    """
    Process question generation task asynchronously.
    
    This task:
    1. Loads chunks from database
    2. Generates questions for each chunk using LLM
    3. Stores generated questions in database
    4. Updates task progress during processing
    5. Supports configurable parallelism
    
    Args:
        task_id: ID of the task tracking this operation
        db: Database session
        project_id: ID of the project
        chunk_ids: List of chunk IDs to generate questions for
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for generation (default: zh-CN)
            - questions_per_chunk: Number of questions per chunk
            - parallelism: Number of concurrent generations (default: 3)
            - active_ga_pair: Optional genre-audience pair
            - custom_prompt: Optional custom prompt template
            - label: Label for generated questions (default: "")
    
    Raises:
        ValueError: If question generation fails
    """
    task_service = TaskService(db)
    llm_service = LLMService(db)
    
    try:
        # Update total count
        task = task_service.get_task(task_id)
        if task:
            task.total_count = len(chunk_ids)
            db.commit()
        
        # Load chunks
        chunks = db.query(Chunks).filter(
            Chunks.id.in_(chunk_ids),
            Chunks.project_id == project_id
        ).all()
        
        if not chunks:
            raise ValueError("No chunks found for the given IDs")
        
        # Get parallelism setting
        parallelism = config.get('parallelism', 3)
        label = config.get('label', '')
        
        # Process chunks in batches
        completed = 0
        for i in range(0, len(chunks), parallelism):
            batch = chunks[i:i + parallelism]
            
            # Generate questions for batch concurrently
            tasks = [
                generate_questions_for_chunk(llm_service, chunk, config)
                for chunk in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store generated questions
            for chunk, result in zip(batch, results):
                if isinstance(result, Exception):
                    # Log error but continue with other chunks
                    task_service.update_task_progress(
                        task_id,
                        completed_count=completed,
                        note=f"Error generating questions for chunk {chunk.id}: {str(result)}"
                    )
                    continue
                
                # Store each question
                for question_text in result:
                    question = Questions(
                        project_id=project_id,
                        chunk_id=chunk.id,
                        question=question_text,
                        label=label,
                        answered=False
                    )
                    db.add(question)
                
                completed += 1
                
                # Update progress
                task_service.update_task_progress(
                    task_id,
                    completed_count=completed,
                    note=f"Generated questions for {completed}/{len(chunks)} chunks"
                )
                db.commit()
        
        # Mark task as complete
        task_service.complete_task(
            task_id,
            note=f"Successfully generated questions for {completed} chunks"
        )
        
    except Exception as e:
        # Mark task as failed
        task_service.fail_task(
            task_id,
            error_message=f"Question generation failed: {str(e)}"
        )
        raise
