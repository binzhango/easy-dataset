"""Multi-turn conversation generation task handler."""

import json
import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from easy_dataset.llm.service import LLMService
from easy_dataset.models.question import Questions
from easy_dataset.models.chunk import Chunks
from easy_dataset.models.conversation import DatasetConversations
from easy_dataset.services.task_service import TaskService


def get_conversation_prompt(
    language: str,
    scenario: str,
    role_a: str,
    role_b: str,
    question: str,
    chunk_content: str,
    max_turns: int
) -> str:
    """
    Generate multi-turn conversation generation prompt.
    
    Args:
        language: Language code ('en', 'zh', 'tr')
        scenario: Conversation scenario (teaching, consulting, discussion, etc.)
        role_a: Role A definition
        role_b: Role B definition
        question: Initial question
        chunk_content: Reference content
        max_turns: Maximum number of turns
        
    Returns:
        Complete conversation generation prompt
    """
    if language == 'en':
        prompt = f"""# Role: Multi-turn Conversation Generator

## Task
Generate a natural multi-turn conversation between two roles based on the given scenario, question, and reference content.

## Scenario
{scenario}

## Roles
- Role A: {role_a}
- Role B: {role_b}

## Initial Question
{question}

## Reference Content
{chunk_content}

## Requirements
1. Generate a natural conversation with {max_turns} turns (each role speaks {max_turns // 2} times)
2. The conversation should be based on the reference content
3. Maintain context and coherence across turns
4. Each turn should add value to the conversation
5. The conversation should feel natural and realistic

## Output Format
Return a JSON array of messages in ShareGPT format:
```json
[
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}},
  ...
]
```

Note: "user" represents {role_a}, "assistant" represents {role_b}
"""
    elif language == 'tr':
        prompt = f"""# Rol: Çok Turlu Konuşma Üretici

## Görev
Verilen senaryo, soru ve referans içeriğe dayalı olarak iki rol arasında doğal çok turlu konuşma oluşturun.

## Senaryo
{scenario}

## Roller
- Rol A: {role_a}
- Rol B: {role_b}

## İlk Soru
{question}

## Referans İçerik
{chunk_content}

## Gereksinimler
1. {max_turns} turlu doğal konuşma oluşturun (her rol {max_turns // 2} kez konuşur)
2. Konuşma referans içeriğe dayanmalıdır
3. Turlar arasında bağlam ve tutarlılık koruyun
4. Her tur konuşmaya değer katmalıdır
5. Konuşma doğal ve gerçekçi hissetmelidir

## Çıktı Formatı
ShareGPT formatında mesaj JSON dizisi döndürün:
```json
[
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}},
  ...
]
```

Not: "user" {role_a}'yı, "assistant" {role_b}'yi temsil eder
"""
    else:  # Chinese
        prompt = f"""# Role: 多轮对话生成器

## 任务
基于给定的场景、问题和参考内容，生成两个角色之间的自然多轮对话。

## 场景
{scenario}

## 角色
- 角色A: {role_a}
- 角色B: {role_b}

## 初始问题
{question}

## 参考内容
{chunk_content}

## 要求
1. 生成 {max_turns} 轮自然对话（每个角色说 {max_turns // 2} 次）
2. 对话应基于参考内容
3. 在各轮之间保持上下文和连贯性
4. 每一轮都应为对话增加价值
5. 对话应感觉自然和真实

## 输出格式
返回 ShareGPT 格式的消息 JSON 数组：
```json
[
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}},
  ...
]
```

注意："user" 代表 {role_a}，"assistant" 代表 {role_b}
"""
    
    return prompt


async def generate_conversation(
    llm_service: LLMService,
    question: Questions,
    chunk: Chunks,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate multi-turn conversation for a question.
    
    Args:
        llm_service: LLM service instance
        question: Question to base conversation on
        chunk: Source chunk containing context
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for generation
            - scenario: Conversation scenario
            - role_a: Role A definition
            - role_b: Role B definition
            - max_turns: Maximum number of turns
    
    Returns:
        Dictionary with 'messages' (list) and 'turn_count' (int) keys
    """
    # Get provider
    provider = llm_service.create_provider(config['provider_config'])
    
    # Build conversation generation prompt
    prompt = get_conversation_prompt(
        language=config.get('language', 'zh-CN'),
        scenario=config.get('scenario', 'General Discussion'),
        role_a=config.get('role_a', 'User'),
        role_b=config.get('role_b', 'Assistant'),
        question=question.question,
        chunk_content=chunk.content,
        max_turns=config.get('max_turns', 4)
    )
    
    # Generate conversation
    messages = [{"role": "user", "content": prompt}]
    response = await provider.chat(messages)
    
    # Parse response - expecting JSON array of messages
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
        messages_list = json.loads(content)
        if isinstance(messages_list, list):
            return {
                'messages': messages_list,
                'turn_count': len(messages_list)
            }
        return {'messages': [], 'turn_count': 0}
    except json.JSONDecodeError:
        # If parsing fails, return empty conversation
        return {'messages': [], 'turn_count': 0}


async def process_conversation_generation_task(
    task_id: str,
    db: Session,
    project_id: str,
    question_ids: List[str],
    config: Dict[str, Any]
) -> None:
    """
    Process multi-turn conversation generation task asynchronously.
    
    This task:
    1. Loads questions and their source chunks from database
    2. Generates multi-turn conversations for each question using LLM
    3. Maintains context across turns
    4. Stores conversations in ShareGPT format
    5. Updates task progress during processing
    6. Supports configurable parallelism
    
    Args:
        task_id: ID of the task tracking this operation
        db: Database session
        project_id: ID of the project
        question_ids: List of question IDs to generate conversations for
        config: Configuration containing:
            - provider_config: LLM provider configuration
            - language: Language for generation (default: zh-CN)
            - scenario: Conversation scenario (default: "General Discussion")
            - role_a: Role A definition (default: "User")
            - role_b: Role B definition (default: "Assistant")
            - max_turns: Maximum number of turns (default: 4)
            - parallelism: Number of concurrent generations (default: 3)
            - model_name: Name of model used (for metadata)
    
    Raises:
        ValueError: If conversation generation fails
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
        
        # Get configuration
        parallelism = config.get('parallelism', 3)
        model_name = config.get('model_name', 'unknown')
        scenario = config.get('scenario', 'General Discussion')
        role_a = config.get('role_a', 'User')
        role_b = config.get('role_b', 'Assistant')
        max_turns = config.get('max_turns', 4)
        
        # Process questions in batches
        completed = 0
        for i in range(0, len(questions), parallelism):
            batch = questions[i:i + parallelism]
            
            # Generate conversations for batch concurrently
            tasks = []
            for question in batch:
                chunk = chunks_dict.get(question.chunk_id)
                if chunk:
                    tasks.append(
                        generate_conversation(llm_service, question, chunk, config)
                    )
                else:
                    # Skip questions without chunks
                    tasks.append(asyncio.sleep(0))  # Placeholder
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store generated conversations
            for question, result in zip(batch, results):
                if isinstance(result, Exception):
                    # Log error but continue with other questions
                    task_service.update_task_progress(
                        task_id,
                        completed_count=completed,
                        note=f"Error generating conversation for question {question.id}: {str(result)}"
                    )
                    continue
                
                if not isinstance(result, dict) or not result.get('messages'):
                    # Skip placeholder results or empty conversations
                    continue
                
                # Get chunk for metadata
                chunk = chunks_dict.get(question.chunk_id)
                if not chunk:
                    continue
                
                # Create conversation entry
                conversation = DatasetConversations(
                    project_id=project_id,
                    question_id=question.id,
                    question=question.question,
                    chunk_id=chunk.id,
                    model=model_name,
                    question_label=question.label,
                    score=0.0,
                    ai_evaluation='',
                    tags='',
                    note='',
                    scenario=scenario,
                    role_a=role_a,
                    role_b=role_b,
                    turn_count=result['turn_count'],
                    max_turns=max_turns,
                    raw_messages=json.dumps(result['messages']),
                    confirmed=False
                )
                db.add(conversation)
                
                completed += 1
                
                # Update progress
                task_service.update_task_progress(
                    task_id,
                    completed_count=completed,
                    note=f"Generated conversations for {completed}/{len(questions)} questions"
                )
                db.commit()
        
        # Mark task as complete
        task_service.complete_task(
            task_id,
            note=f"Successfully generated {completed} multi-turn conversations"
        )
        
    except Exception as e:
        # Mark task as failed
        task_service.fail_task(
            task_id,
            error_message=f"Conversation generation failed: {str(e)}"
        )
        raise
