"""
Example demonstrating internationalization (i18n) usage in Easy Dataset.

This script shows how to use the i18n system for multi-language support.
"""

from easy_dataset.utils.i18n import (
    t, set_language, get_language, 
    detect_language, get_i18n
)


def example_basic_translation():
    """Example 1: Basic translation usage."""
    print("=" * 60)
    print("Example 1: Basic Translation")
    print("=" * 60)
    
    # English (default)
    set_language('en')
    print(f"Language: {get_language()}")
    print(f"Success: {t('common.success')}")
    print(f"Loading: {t('common.loading')}")
    print()
    
    # Chinese
    set_language('zh-CN')
    print(f"Language: {get_language()}")
    print(f"Success: {t('common.success')}")
    print(f"Loading: {t('common.loading')}")
    print()
    
    # Turkish
    set_language('tr')
    print(f"Language: {get_language()}")
    print(f"Success: {t('common.success')}")
    print(f"Loading: {t('common.loading')}")
    print()


def example_variable_interpolation():
    """Example 2: Translation with variable interpolation."""
    print("=" * 60)
    print("Example 2: Variable Interpolation")
    print("=" * 60)
    
    # English
    set_language('en')
    print(f"Language: {get_language()}")
    error = t('errors.file_not_found', path='/data/document.pdf')
    print(f"Error: {error}")
    
    progress = t('tasks.messages.task_progress', 
                 completed=7, total=10, percentage=70)
    print(f"Progress: {progress}")
    print()
    
    # Chinese
    set_language('zh-CN')
    print(f"Language: {get_language()}")
    error = t('errors.file_not_found', path='/data/document.pdf')
    print(f"Error: {error}")
    
    progress = t('tasks.messages.task_progress', 
                 completed=7, total=10, percentage=70)
    print(f"Progress: {progress}")
    print()


def example_nested_keys():
    """Example 3: Nested translation keys."""
    print("=" * 60)
    print("Example 3: Nested Translation Keys")
    print("=" * 60)
    
    set_language('en')
    print(f"Language: {get_language()}")
    print(f"Task Status - Pending: {t('tasks.status.pending')}")
    print(f"Task Status - Processing: {t('tasks.status.processing')}")
    print(f"Task Status - Completed: {t('tasks.status.completed')}")
    print(f"Task Type - File Processing: {t('tasks.types.file_processing')}")
    print(f"Task Type - Question Generation: {t('tasks.types.question_generation')}")
    print()
    
    set_language('zh-CN')
    print(f"Language: {get_language()}")
    print(f"Task Status - Pending: {t('tasks.status.pending')}")
    print(f"Task Status - Processing: {t('tasks.status.processing')}")
    print(f"Task Status - Completed: {t('tasks.status.completed')}")
    print(f"Task Type - File Processing: {t('tasks.types.file_processing')}")
    print(f"Task Type - Question Generation: {t('tasks.types.question_generation')}")
    print()


def example_language_detection():
    """Example 4: Language detection from Accept-Language header."""
    print("=" * 60)
    print("Example 4: Language Detection")
    print("=" * 60)
    
    # Simulate different Accept-Language headers
    headers = [
        'en-US,en;q=0.9',
        'zh-CN,zh;q=0.9,en;q=0.8',
        'tr-TR,tr;q=0.9,en;q=0.8',
        'fr-FR,fr;q=0.9',  # Unsupported, should fallback to English
    ]
    
    for header in headers:
        detected = detect_language(header)
        set_language(detected)
        print(f"Accept-Language: {header}")
        print(f"Detected Language: {detected}")
        print(f"Message: {t('common.success')}")
        print()


def example_error_messages():
    """Example 5: Error messages in different languages."""
    print("=" * 60)
    print("Example 5: Error Messages")
    print("=" * 60)
    
    errors = [
        ('errors.file_not_found', {'path': '/data/file.txt'}),
        ('errors.invalid_file_format', {'format': 'xyz'}),
        ('errors.file_too_large', {'max_size': 100}),
        ('errors.authentication_failed', {}),
    ]
    
    for lang in ['en', 'zh-CN', 'tr']:
        set_language(lang)
        print(f"\nLanguage: {lang}")
        print("-" * 40)
        for error_key, params in errors:
            message = t(error_key, **params)
            print(f"  {message}")


def example_llm_prompts():
    """Example 6: LLM prompts in different languages."""
    print("=" * 60)
    print("Example 6: LLM Prompts")
    print("=" * 60)
    
    for lang in ['en', 'zh-CN', 'tr']:
        set_language(lang)
        print(f"\nLanguage: {lang}")
        print("-" * 40)
        
        # Question generation prompt
        system = t('prompts.question_generation.system')
        print(f"System Prompt: {system}")
        
        user = t('prompts.question_generation.user', 
                count=3, 
                text="Sample text content here...")
        print(f"User Prompt: {user[:100]}...")
        print()


def example_task_messages():
    """Example 7: Task progress messages."""
    print("=" * 60)
    print("Example 7: Task Progress Messages")
    print("=" * 60)
    
    # Simulate task progress
    total = 10
    for completed in [0, 3, 7, 10]:
        percentage = (completed / total) * 100 if total > 0 else 0
        
        print(f"\nProgress: {completed}/{total}")
        print("-" * 40)
        
        for lang in ['en', 'zh-CN', 'tr']:
            set_language(lang)
            message = t('tasks.messages.task_progress',
                       completed=completed,
                       total=total,
                       percentage=int(percentage))
            print(f"  [{lang}] {message}")


def example_supported_languages():
    """Example 8: Get supported languages."""
    print("=" * 60)
    print("Example 8: Supported Languages")
    print("=" * 60)
    
    i18n = get_i18n()
    languages = i18n.get_supported_languages()
    
    print(f"Supported Languages: {', '.join(languages)}")
    print()
    
    for lang in languages:
        set_language(lang)
        print(f"{lang}: {t('common.success')}")


def main():
    """Run all examples."""
    print("\n")
    print("=" * 60)
    print("Easy Dataset - Internationalization (i18n) Examples")
    print("=" * 60)
    print()
    
    example_basic_translation()
    example_variable_interpolation()
    example_nested_keys()
    example_language_detection()
    example_error_messages()
    example_llm_prompts()
    example_task_messages()
    example_supported_languages()
    
    print("\n")
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
