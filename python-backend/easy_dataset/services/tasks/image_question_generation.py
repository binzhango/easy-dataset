"""Image question generation task handler."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from easy_dataset.llm.service import LLMService
from easy_dataset.models.image import Images
from easy_dataset.models.question import Questions
from easy_dataset.models.task import Task, TaskStatus
from easy_dataset.services.image_service import ImageService

logger = logging.getLogger(__name__)


class ImageQuestionGenerationTask:
    """
    Task handler for generating questions from images using vision-capable LLM models.
    
    Features:
    - Uses vision-capable models (GPT-4V, Gemini Vision, etc.)
    - Supports custom question templates
    - Batch processing with progress tracking
    - Error handling and retry logic
    """
    
    def __init__(
        self,
        db_session: Session,
        llm_service: LLMService,
        image_service: ImageService
    ):
        """
        Initialize image question generation task.
        
        Args:
            db_session: Database session
            llm_service: LLM service for API calls
            image_service: Image service for loading images
        """
        self.db = db_session
        self.llm_service = llm_service
        self.image_service = image_service
    
    def get_default_prompt_template(self, language: str = "en") -> str:
        """
        Get default prompt template for image question generation.
        
        Args:
            language: Language code (en, zh-CN, tr)
            
        Returns:
            Prompt template string
        """
        templates = {
            "en": """Analyze this image and generate {num_questions} thoughtful questions about it.

The questions should:
- Be specific to what you see in the image
- Cover different aspects (objects, actions, context, details)
- Be answerable based on the image content
- Vary in complexity

Format your response as a JSON array of questions:
["Question 1?", "Question 2?", "Question 3?"]""",
            
            "zh-CN": """分析这张图片并生成 {num_questions} 个有深度的问题。

问题应该：
- 针对图片中看到的内容
- 涵盖不同方面（物体、动作、背景、细节）
- 基于图片内容可以回答
- 难度各异

将回答格式化为 JSON 数组：
["问题 1？", "问题 2？", "问题 3？"]""",
            
            "tr": """Bu görseli analiz edin ve {num_questions} düşündürücü soru oluşturun.

Sorular şunları içermelidir:
- Görselde gördüklerinize özgü olmalı
- Farklı yönleri kapsamalı (nesneler, eylemler, bağlam, detaylar)
- Görsel içeriğe dayanarak cevaplanabilir olmalı
- Karmaşıklık açısından çeşitlilik göstermeli

Yanıtınızı JSON dizisi olarak biçimlendirin:
["Soru 1?", "Soru 2?", "Soru 3?"]"""
        }
        
        return templates.get(language, templates["en"])
    
    def validate_vision_model(self, model_name: str) -> bool:
        """
        Validate that the model supports vision capabilities.
        
        Args:
            model_name: Model name
            
        Returns:
            True if model supports vision
        """
        # List of known vision-capable models
        vision_models = [
            "gpt-4-vision",
            "gpt-4v",
            "gpt-4o",
            "gpt-4-turbo",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
        ]
        
        model_lower = model_name.lower()
        
        # Check if model name contains vision keywords or matches known models
        return any(
            vm in model_lower for vm in vision_models
        ) or "vision" in model_lower or "4o" in model_lower
    
    async def generate_questions_for_image(
        self,
        image: Images,
        config: Dict[str, Any],
        num_questions: int = 3,
        custom_prompt: Optional[str] = None,
        language: str = "en"
    ) -> List[str]:
        """
        Generate questions for a single image.
        
        Args:
            image: Images model instance
            config: LLM provider configuration
            num_questions: Number of questions to generate
            custom_prompt: Optional custom prompt template
            language: Language code
            
        Returns:
            List of generated questions
            
        Raises:
            ValueError: If model doesn't support vision
            RuntimeError: If generation fails
        """
        # Validate vision capability
        model_name = config.get("model", "")
        if not self.validate_vision_model(model_name):
            raise ValueError(
                f"Model '{model_name}' does not appear to support vision. "
                "Please use a vision-capable model like gpt-4o, gpt-4-vision, or gemini-pro-vision."
            )
        
        # Get image data as data URL
        image_data_url = self.image_service.get_image_data_url(image.id)
        
        if not image_data_url:
            raise RuntimeError(f"Failed to load image data for image {image.id}")
        
        # Prepare prompt
        if custom_prompt:
            prompt = custom_prompt.format(num_questions=num_questions)
        else:
            prompt = self.get_default_prompt_template(language).format(
                num_questions=num_questions
            )
        
        # Call vision API
        try:
            response = await self.llm_service.vision_chat(
                config=config,
                prompt=prompt,
                image_data=image_data_url,
                mime_type="image/jpeg"
            )
            
            # Extract questions from response
            text = response.get("text", "")
            
            # Try to parse as JSON array
            import json
            try:
                questions = json.loads(text)
                if isinstance(questions, list):
                    return [str(q).strip() for q in questions if q]
            except json.JSONDecodeError:
                pass
            
            # Fallback: split by newlines and filter
            questions = [
                line.strip().lstrip("0123456789.-) ")
                for line in text.split("\n")
                if line.strip() and "?" in line
            ]
            
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Failed to generate questions for image {image.id}: {e}")
            raise RuntimeError(f"Question generation failed: {e}")
    
    async def process_task(
        self,
        task: Task,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process image question generation task.
        
        Args:
            task: Task model instance
            config: Task configuration containing:
                - image_ids: List of image IDs to process
                - num_questions: Number of questions per image
                - custom_prompt: Optional custom prompt template
                - language: Language code
                - concurrency: Number of concurrent requests
                
        Returns:
            Dictionary with results
        """
        # Extract configuration
        image_ids = config.get("image_ids", [])
        num_questions = config.get("num_questions", 3)
        custom_prompt = config.get("custom_prompt")
        language = config.get("language", "en")
        concurrency = config.get("concurrency", 3)
        
        # Get LLM configuration
        llm_config = config.get("llm_config", {})
        
        if not image_ids:
            raise ValueError("No image IDs provided")
        
        # Update task
        task.total_count = len(image_ids)
        task.status = TaskStatus.PROCESSING
        self.db.commit()
        
        # Process images
        processed = 0
        failed = 0
        generated_questions = []
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_single_image(image_id: str):
            nonlocal processed, failed
            
            async with semaphore:
                try:
                    # Get image
                    image = self.image_service.get_image(image_id)
                    
                    if not image:
                        logger.warning(f"Image not found: {image_id}")
                        failed += 1
                        return
                    
                    # Generate questions
                    questions = await self.generate_questions_for_image(
                        image=image,
                        config=llm_config,
                        num_questions=num_questions,
                        custom_prompt=custom_prompt,
                        language=language
                    )
                    
                    # Store questions in database
                    for question_text in questions:
                        question = Questions(
                            project_id=task.project_id,
                            image_id=image.id,
                            question=question_text,
                            answered=False
                        )
                        self.db.add(question)
                        generated_questions.append(question_text)
                    
                    self.db.commit()
                    
                    processed += 1
                    
                    # Update progress
                    task.processed_count = processed
                    task.failed_count = failed
                    self.db.commit()
                    
                    logger.info(
                        f"Generated {len(questions)} questions for image {image.image_name}"
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to process image {image_id}: {e}")
                    failed += 1
                    
                    # Update progress
                    task.processed_count = processed
                    task.failed_count = failed
                    self.db.commit()
        
        # Process all images concurrently
        await asyncio.gather(
            *[process_single_image(image_id) for image_id in image_ids],
            return_exceptions=True
        )
        
        # Update task status
        if failed == len(image_ids):
            task.status = TaskStatus.FAILED
            task.note = "All images failed to process"
        elif failed > 0:
            task.status = TaskStatus.COMPLETED
            task.note = f"Completed with {failed} failures"
        else:
            task.status = TaskStatus.COMPLETED
            task.note = "All images processed successfully"
        
        self.db.commit()
        
        logger.info(
            f"Image question generation task completed: "
            f"{processed} processed, {failed} failed, "
            f"{len(generated_questions)} questions generated"
        )
        
        return {
            "processed": processed,
            "failed": failed,
            "total_questions": len(generated_questions),
            "questions": generated_questions[:10]  # Return first 10 as sample
        }
    
    async def generate_single_question(
        self,
        image_id: str,
        config: Dict[str, Any],
        custom_prompt: Optional[str] = None,
        language: str = "en"
    ) -> Optional[str]:
        """
        Generate a single question for an image (convenience method).
        
        Args:
            image_id: Image ID
            config: LLM provider configuration
            custom_prompt: Optional custom prompt
            language: Language code
            
        Returns:
            Generated question or None if failed
        """
        try:
            image = self.image_service.get_image(image_id)
            
            if not image:
                return None
            
            questions = await self.generate_questions_for_image(
                image=image,
                config=config,
                num_questions=1,
                custom_prompt=custom_prompt,
                language=language
            )
            
            return questions[0] if questions else None
            
        except Exception as e:
            logger.error(f"Failed to generate question for image {image_id}: {e}")
            return None
