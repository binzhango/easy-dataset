"""
Example demonstrating how to use the prompt templates in Easy Dataset.

This example shows:
1. Question generation prompts
2. Answer generation prompts
3. Data cleaning prompts
4. Dataset evaluation prompts
"""

from easy_dataset.llm.prompts import (
    get_question_prompt,
    get_answer_prompt,
    get_data_clean_prompt,
    get_dataset_evaluation_prompt,
)


def example_question_generation():
    """Example: Generate questions from text"""
    print("=" * 60)
    print("EXAMPLE 1: Question Generation")
    print("=" * 60)
    
    # Sample text to analyze
    text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, 
    in contrast to the natural intelligence displayed by humans and animals. 
    Leading AI textbooks define the field as the study of "intelligent agents": 
    any device that perceives its environment and takes actions that maximize 
    its chance of successfully achieving its goals.
    """
    
    # Generate prompt in English
    prompt_en = get_question_prompt(
        language='en',
        text=text,
        number=3
    )
    
    print("\nEnglish Question Generation Prompt (first 500 chars):")
    print(prompt_en[:500] + "...")
    
    # Generate prompt with Genre-Audience pair
    prompt_with_ga = get_question_prompt(
        language='en',
        text=text,
        number=3,
        active_ga_pair={
            'active': True,
            'genre': 'Technical Documentation',
            'audience': 'Software Engineers'
        }
    )
    
    print("\n\nWith Genre-Audience (first 500 chars):")
    print(prompt_with_ga[:500] + "...")


def example_answer_generation():
    """Example: Generate answers to questions"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Answer Generation")
    print("=" * 60)
    
    # Sample context and question
    text = """
    Python is a high-level, interpreted programming language. 
    It was created by Guido van Rossum and first released in 1991. 
    Python's design philosophy emphasizes code readability with 
    its notable use of significant indentation.
    """
    
    question = "Who created Python and when was it first released?"
    
    # Generate basic answer prompt
    prompt = get_answer_prompt(
        language='en',
        text=text,
        question=question
    )
    
    print("\nBasic Answer Generation Prompt (first 500 chars):")
    print(prompt[:500] + "...")
    
    # Generate answer prompt with label template
    prompt_with_template = get_answer_prompt(
        language='en',
        text=text,
        question="What type of language is Python?",
        question_template={
            'answerType': 'label',
            'labels': ['Compiled', 'Interpreted', 'Assembly', 'Other'],
            'description': 'Select the most appropriate language type'
        }
    )
    
    print("\n\nWith Label Template (last 300 chars):")
    print("..." + prompt_with_template[-300:])


def example_data_cleaning():
    """Example: Clean noisy text data"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Data Cleaning")
    print("=" * 60)
    
    # Sample noisy text
    noisy_text = """
    This   is  a   text   with    extra    spaces...
    
    
    And multiple blank lines!!!
    
    Also some  weird   formatting  issues.
    """
    
    # Generate cleaning prompt
    prompt = get_data_clean_prompt(
        language='en',
        text=noisy_text
    )
    
    print("\nData Cleaning Prompt (first 500 chars):")
    print(prompt[:500] + "...")


def example_dataset_evaluation():
    """Example: Evaluate Q&A dataset quality"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Dataset Evaluation")
    print("=" * 60)
    
    # Sample Q&A pair with context
    chunk_content = """
    Machine learning is a subset of artificial intelligence that 
    focuses on the development of algorithms that can learn from 
    and make predictions or decisions based on data.
    """
    
    question = "What is machine learning?"
    answer = """
    Machine learning is a subset of AI that develops algorithms 
    capable of learning from data and making predictions or decisions.
    """
    
    # Generate evaluation prompt
    prompt = get_dataset_evaluation_prompt(
        language='en',
        chunk_content=chunk_content,
        question=question,
        answer=answer
    )
    
    print("\nDataset Evaluation Prompt (first 500 chars):")
    print(prompt[:500] + "...")
    
    # Example with distilled content (no original text)
    prompt_distilled = get_dataset_evaluation_prompt(
        language='en',
        chunk_content='',  # Empty for distilled datasets
        question="What is the capital of France?",
        answer="The capital of France is Paris."
    )
    
    print("\n\nDistilled Dataset Evaluation (showing 'Distilled Content'):")
    # Find and show the chunk content section
    lines = prompt_distilled.split('\n')
    for i, line in enumerate(lines):
        if 'Original Text Chunk Content:' in line:
            print('\n'.join(lines[i:i+3]))
            break


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("EASY DATASET PROMPT TEMPLATES - USAGE EXAMPLES")
    print("=" * 60)
    
    example_question_generation()
    example_answer_generation()
    example_data_cleaning()
    example_dataset_evaluation()
    
    print("\n\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nThese prompts can be used with any LLM provider:")
    print("- OpenAI (GPT-3.5, GPT-4)")
    print("- Ollama (local models)")
    print("- OpenRouter (multiple models)")
    print("- LiteLLM (100+ models)")
    print("- Gemini (Google models)")


if __name__ == '__main__':
    main()
