"""Answer generation task handler."""

import json
import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from easy_dataset.llm.service import LLMService
from easy_dataset.llm.prompts.answer_prompts import get_answer_prompt
from easy_dataset.models.question import Questions
from easy_dataset.models.chunk import Chunks
from easy_dataset.models.dataset import Datasets
from easy_dataset.services.task_service import TaskService


def extract_thinking_and_answer(response_content: str) -> tuple[str, str]:
    """
    Extract chain-of-thought (thinking) and final answer from LLM response.
    
    Looks for common patterns like:
    - "思考：...答案：..." (Chinese)
    - "Thinking:...Answer:..." (English)
    - "Düşünce:...Cevap:..." (Turkish)
    
    Args:
        response_content: Raw response from LLM
        
    Returns:
        Tuple of (thinking/cot, answer)
    """
    content = response_content.strip()
    
    # Try to find thinking/answer separators
    separators = [
        ('思考：', '答案：'),
        ('思考:', '答案:'),
        ('Thinking:', 'Answer:'),
        ('Düşünce:', 'Cevap:'),
        ('CoT:', 'Answer:'),
        ('Chain of Thought:', 'Answer:')
    ]
    
    for think_sep, answer_sep in separators:
        if think_sep in content and answer_sep in content:
            parts = content.split(answer_sep, 1)
            if len(parts) == 2:
                thinking = parts[0].replace(think_sep, '').strip()
                answer = parts[1].strip()
                return thinking, answer
    
    # If no separator found, treat entire content as answer
    return '', content


async def generate_answer_for_question(
    llm_service: LLMService,
    question: Questions,
    chunk: Chunks,
    config: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generate answer for a single question.
    
    Args:
        llm_service: LLM service instance
        question: Question to answer
        chunk: Source chunk containing context
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for generation
            - question_template: Optional template for custom answer format
            - custom_prompt: Optional custom prompt template
    
    Returns:
        Dictionary with 'answer' and 'cot' (chain-of-thought) keys
    """
    # Get provider
    provider = llm_service.create_provider(config['provider_config'])
    
    # Build prompt with question and chunk context
    prompt = get_answer_prompt(
        language=config.get('language', 'zh-CN'),
        text=chunk.content,
        question=question.question,
        question_template=config.get('question_template'),
        custom_prompt=config.get('custom_prompt')
    )
    
    # Generate answer
    messages = [{"role": "user", "content": prompt}]
    response = await provider.chat(messages)
    
    # Extract content
    content = response.get('content', '')
    
    # Extract thinking and answer
    cot, answer = extract_thinking_and_answer(content)
    
    return {
        'answer': answer,
        'cot': cot
    }


async def process_answer_generation_task(
    task_id: str,
    db: Session,
    project_id: str,
    question_ids: List[str],
    config: Dict[str, Any]
) -> None:
    """
    Process answer generation task asynchronously.
    
    This task:
    1. Loads questions and their source chunks from database
    2. Generates answers for each question using LLM with chunk context
    3. Stores generated answers as dataset entries
    4. Updates task progress during processing
    5. Supports configurable parallelism
    6. Maintains question-answer pair integrity
    
    Args:
        task_id: ID of the task tracking this operation
        db: Database session
        project_id: ID of the project
        question_ids: List of question IDs to generate answers for
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for generation (default: zh-CN)
            - parallelism: Number of concurrent generations (default: 3)
            - question_template: Optional template for custom answer format
            - custom_prompt: Optional custom prompt template
            - model_name: Name of model used (for metadata)
    
    Raises:
        ValueError: If answer generation fails
    """
    task_service = TaskService(db)
    llm_service = LLMService(db)
    
    try:
        # Update total count
        task = task_service.get_task(task_id)
        if task:
            task.total_count = len(question_ids)
            db.commit()
        
        # Load questions with their chunks
        questions = db.query(Questions).filter(
            Questions.id.in_(question_ids),
            Questions.project_id == project_id
        ).all()
        
        if not questions:
            raise ValueError("No questions found for the given IDs")
        
        # Load all chunks at once for efficiency
        chunk_ids = [q.chunk_id for q in questions]
        chunks_dict = {
            chunk.id: chunk
            for chunk in db.query(Chunks).filter(Chunks.id.in_(chunk_ids)).all()
        }
        
        # Get parallelism setting
        parallelism = config.get('parallelism', 3)
        model_name = config.get('model_name', 'unknown')
        
        # Process questions in batches
        completed = 0
        for i in range(0, len(questions), parallelism):
            batch = questions[i:i + parallelism]
            
            # Generate answers for batch concurrently
            tasks = []
            for question in batch:
                chunk = chunks_dict.get(question.chunk_id)
                if chunk:
                    tasks.append(
                        generate_answer_for_question(llm_service, question, chunk, config)
                    )
                else:
                    # Skip questions without chunks
                    tasks.append(asyncio.sleep(0))  # Placeholder
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store generated answers as dataset entries
            for question, result in zip(batch, results):
                if isinstance(result, Exception):
                    # Log error but continue with other questions
                    task_service.update_task_progress(
                        task_id,
                        completed_count=completed,
                        note=f"Error generating answer for question {question.id}: {str(result)}"
                    )
                    continue
                
                if not isinstance(result, dict):
                    # Skip placeholder results
                    continue
                
                # Get chunk for metadata
                chunk = chunks_dict.get(question.chunk_id)
                if not chunk:
                    continue
                
                # Create dataset entry
                dataset_entry = Datasets(
                    project_id=project_id,
                    question_id=question.id,
                    question=question.question,
                    answer=result['answer'],
                    answer_type='text',
                    chunk_name=f"Chunk {chunk.index}",
                    chunk_content=chunk.content,
                    model=model_name,
                    question_label=question.label,
                    cot=result['cot'],
                    confirmed=False,
                    score=0.0,
                    ai_evaluation='',
                    tags='',
                    note='',
                    other=''
                )
                db.add(dataset_entry)
                
                # Mark question as answered
                question.answered = True
                
                completed += 1
                
                # Update progress
                task_service.update_task_progress(
                    task_id,
                    completed_count=completed,
                    note=f"Generated answers for {completed}/{len(questions)} questions"
                )
                db.commit()
        
        # Mark task as complete
        task_service.complete_task(
            task_id,
            note=f"Successfully generated answers for {completed} questions"
        )
        
    except Exception as e:
        # Mark task as failed
        task_service.fail_task(
            task_id,
            error_message=f"Answer generation failed: {str(e)}"
        )
        raise
