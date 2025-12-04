"""Dataset evaluation task handler."""

import json
import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from easy_dataset.llm.service import LLMService
from easy_dataset.llm.prompts.eval_prompts import (
    DATASET_EVALUATION_PROMPT_ZH,
    DATASET_EVALUATION_PROMPT_EN,
    DATASET_EVALUATION_PROMPT_TR
)
from easy_dataset.models.dataset import Datasets
from easy_dataset.services.task_service import TaskService


def substitute_variables(template: str, variables: Dict[str, Any]) -> str:
    """
    Substitute template variables with actual values.
    
    Args:
        template: Template string with {{variable}} placeholders
        variables: Dictionary of variable names to values
        
    Returns:
        Template with all variables substituted
    """
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def get_evaluation_prompt(
    language: str,
    question: str,
    answer: str,
    chunk_content: str
) -> str:
    """
    Generate dataset evaluation prompt.
    
    Args:
        language: Language code ('en', 'zh', 'tr')
        question: Question text
        answer: Answer text
        chunk_content: Original chunk content (or "Distilled Content" if none)
        
    Returns:
        Complete evaluation prompt
    """
    # Select base prompt template
    if language == 'en':
        base_prompt = DATASET_EVALUATION_PROMPT_EN
    elif language == 'tr':
        base_prompt = DATASET_EVALUATION_PROMPT_TR
    else:
        base_prompt = DATASET_EVALUATION_PROMPT_ZH
    
    # Prepare variables
    variables = {
        'chunkContent': chunk_content or 'Distilled Content',
        'question': question,
        'answer': answer
    }
    
    # Substitute all variables
    return substitute_variables(base_prompt, variables)


async def evaluate_dataset_entry(
    llm_service: LLMService,
    entry: Datasets,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate a single dataset entry.
    
    Args:
        llm_service: LLM service instance
        entry: Dataset entry to evaluate
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for evaluation
    
    Returns:
        Dictionary with 'score' and 'evaluation' keys
    """
    # Get provider
    provider = llm_service.create_provider(config['provider_config'])
    
    # Build evaluation prompt
    prompt = get_evaluation_prompt(
        language=config.get('language', 'zh-CN'),
        question=entry.question,
        answer=entry.answer,
        chunk_content=entry.chunk_content
    )
    
    # Generate evaluation
    messages = [{"role": "user", "content": prompt}]
    response = await provider.chat(messages)
    
    # Parse response - expecting JSON with score and evaluation
    content = response.get('content', '{}')
    
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
        result = json.loads(content)
        return {
            'score': float(result.get('score', 0.0)),
            'evaluation': str(result.get('evaluation', ''))
        }
    except (json.JSONDecodeError, ValueError):
        # If parsing fails, return default values
        return {
            'score': 0.0,
            'evaluation': 'Evaluation parsing failed'
        }


async def process_dataset_evaluation_task(
    task_id: str,
    db: Session,
    project_id: str,
    dataset_ids: List[str],
    config: Dict[str, Any]
) -> None:
    """
    Process dataset evaluation task asynchronously.
    
    This task:
    1. Loads dataset entries from database
    2. Evaluates each entry using LLM
    3. Stores evaluation scores and conclusions
    4. Updates task progress during processing
    5. Supports configurable parallelism
    
    Args:
        task_id: ID of the task tracking this operation
        db: Database session
        project_id: ID of the project
        dataset_ids: List of dataset entry IDs to evaluate
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for evaluation (default: zh-CN)
            - parallelism: Number of concurrent evaluations (default: 3)
    
    Raises:
        ValueError: If evaluation fails
    """
    task_service = TaskService(db)
    llm_service = LLMService(db)
    
    try:
        # Update total count
        task = task_service.get_task(task_id)
        if task:
            task.total_count = len(dataset_ids)
            db.commit()
        
        # Load dataset entries
        entries = db.query(Datasets).filter(
            Datasets.id.in_(dataset_ids),
            Datasets.project_id == project_id
        ).all()
        
        if not entries:
            raise ValueError("No dataset entries found for the given IDs")
        
        # Get parallelism setting
        parallelism = config.get('parallelism', 3)
        
        # Process entries in batches
        completed = 0
        for i in range(0, len(entries), parallelism):
            batch = entries[i:i + parallelism]
            
            # Evaluate batch concurrently
            tasks = [
                evaluate_dataset_entry(llm_service, entry, config)
                for entry in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store evaluation results
            for entry, result in zip(batch, results):
                if isinstance(result, Exception):
                    # Log error but continue with other entries
                    task_service.update_task_progress(
                        task_id,
                        completed_count=completed,
                        note=f"Error evaluating entry {entry.id}: {str(result)}"
                    )
                    continue
                
                # Update entry with evaluation results
                entry.score = result['score']
                entry.ai_evaluation = result['evaluation']
                
                completed += 1
                
                # Update progress
                task_service.update_task_progress(
                    task_id,
                    completed_count=completed,
                    note=f"Evaluated {completed}/{len(entries)} entries"
                )
                db.commit()
        
        # Mark task as complete
        task_service.complete_task(
            task_id,
            note=f"Successfully evaluated {completed} dataset entries"
        )
        
    except Exception as e:
        # Mark task as failed
        task_service.fail_task(
            task_id,
            error_message=f"Dataset evaluation failed: {str(e)}"
        )
        raise
