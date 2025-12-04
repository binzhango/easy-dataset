"""
LLM prompt templates.

This module contains prompt templates for question generation,
answer generation, evaluation, and other LLM tasks.
"""

from .question_prompts import (
    get_question_prompt,
    get_ga_prompt,
    QUESTION_PROMPT_ZH,
    QUESTION_PROMPT_EN,
    QUESTION_PROMPT_TR,
)

from .answer_prompts import (
    get_answer_prompt,
    get_question_template_prompts,
    ANSWER_PROMPT_ZH,
    ANSWER_PROMPT_EN,
    ANSWER_PROMPT_TR,
)

from .eval_prompts import (
    get_data_clean_prompt,
    get_dataset_evaluation_prompt,
    DATA_CLEAN_PROMPT_ZH,
    DATA_CLEAN_PROMPT_EN,
    DATA_CLEAN_PROMPT_TR,
    DATASET_EVALUATION_PROMPT_ZH,
    DATASET_EVALUATION_PROMPT_EN,
    DATASET_EVALUATION_PROMPT_TR,
)

__all__ = [
    # Question generation
    'get_question_prompt',
    'get_ga_prompt',
    'QUESTION_PROMPT_ZH',
    'QUESTION_PROMPT_EN',
    'QUESTION_PROMPT_TR',
    # Answer generation
    'get_answer_prompt',
    'get_question_template_prompts',
    'ANSWER_PROMPT_ZH',
    'ANSWER_PROMPT_EN',
    'ANSWER_PROMPT_TR',
    # Evaluation and cleaning
    'get_data_clean_prompt',
    'get_dataset_evaluation_prompt',
    'DATA_CLEAN_PROMPT_ZH',
    'DATA_CLEAN_PROMPT_EN',
    'DATA_CLEAN_PROMPT_TR',
    'DATASET_EVALUATION_PROMPT_ZH',
    'DATASET_EVALUATION_PROMPT_EN',
    'DATASET_EVALUATION_PROMPT_TR',
]
