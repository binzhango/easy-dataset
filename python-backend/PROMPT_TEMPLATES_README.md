# Prompt Templates System

This document describes the prompt template system in Easy Dataset Python backend.

## Overview

The prompt templates system provides multi-language support for:
- **Question Generation**: Generate questions from text chunks
- **Answer Generation**: Generate answers with context injection
- **Data Cleaning**: Clean and normalize text data
- **Dataset Evaluation**: Evaluate Q&A dataset quality

All prompts support three languages: **English (en)**, **Chinese (zh)**, and **Turkish (tr)**.

## Architecture

```
easy_dataset/llm/prompts/
├── __init__.py              # Public API exports
├── question_prompts.py      # Question generation templates
├── answer_prompts.py        # Answer generation templates
└── eval_prompts.py          # Evaluation and cleaning templates
```

## Question Generation

### Basic Usage

```python
from easy_dataset.llm.prompts import get_question_prompt

text = "Your text content here..."

# Generate prompt in English
prompt = get_question_prompt(
    language='en',
    text=text,
    number=5  # Number of questions to generate
)
```

### With Genre-Audience Targeting

```python
# Generate questions for specific audience and genre
prompt = get_question_prompt(
    language='en',
    text=text,
    number=5,
    active_ga_pair={
        'active': True,
        'genre': 'Technical Documentation',
        'audience': 'Software Engineers'
    }
)
```

### With Custom Prompt

```python
# Use your own custom prompt template
custom_template = """
Your custom prompt template here with {{text}} and {{number}} placeholders
"""

prompt = get_question_prompt(
    language='en',
    text=text,
    custom_prompt=custom_template
)
```

### Features

- **Automatic question count**: Defaults to `text_length / 240` if not specified
- **Genre-Audience (GA) pairs**: Customize questions for specific contexts
- **Multi-language**: Full support for English, Chinese, Turkish
- **Template variables**: `{{text}}`, `{{number}}`, `{{textLength}}`, `{{gaPrompt}}`, etc.

## Answer Generation

### Basic Usage

```python
from easy_dataset.llm.prompts import get_answer_prompt

text = "Reference text containing the answer..."
question = "What is the question?"

# Generate answer prompt
prompt = get_answer_prompt(
    language='en',
    text=text,
    question=question
)
```

### With Question Templates

#### Label-based Answers

```python
# For multiple-choice or classification answers
prompt = get_answer_prompt(
    language='en',
    text=text,
    question="What type of language is Python?",
    question_template={
        'answerType': 'label',
        'labels': ['Compiled', 'Interpreted', 'Assembly', 'Other'],
        'description': 'Select the most appropriate language type'
    }
)
```

#### Custom Format Answers

```python
# For structured output formats
prompt = get_answer_prompt(
    language='en',
    text=text,
    question="Analyze the sentiment",
    question_template={
        'answerType': 'custom_format',
        'customFormat': '{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0}',
        'description': 'Return sentiment analysis in JSON format'
    }
)
```

### Features

- **Context injection**: Automatically includes reference text and question
- **Chain-of-thought**: Prompts encourage step-by-step reasoning
- **Custom formats**: Support for labels, structured output, free-form text
- **Template descriptions**: Add custom instructions to prompts

## Data Cleaning

### Usage

```python
from easy_dataset.llm.prompts import get_data_clean_prompt

noisy_text = "Text with   extra  spaces and errors..."

# Generate cleaning prompt
prompt = get_data_clean_prompt(
    language='en',
    text=noisy_text
)
```

### Cleaning Objectives

1. **Remove Noise**: Meaningless symbols, garbled text, duplicates
2. **Standardize Format**: Encoding, punctuation, spacing
3. **Optimize Content**: Fix typos, grammar errors
4. **Organize Structure**: Paragraph optimization
5. **Preserve Meaning**: Keep original intent intact

## Dataset Evaluation

### Usage

```python
from easy_dataset.llm.prompts import get_dataset_evaluation_prompt

# Evaluate Q&A pair with original text
prompt = get_dataset_evaluation_prompt(
    language='en',
    chunk_content="Original text chunk...",
    question="What is machine learning?",
    answer="Machine learning is..."
)
```

### Distilled Datasets

For datasets without original text reference:

```python
# Empty chunk_content for distilled datasets
prompt = get_dataset_evaluation_prompt(
    language='en',
    chunk_content='',  # Will show "Distilled Content"
    question="What is the capital of France?",
    answer="The capital of France is Paris."
)
```

### Evaluation Dimensions

1. **Question Quality (25%)**
   - Clarity and precision
   - Grammar and structure
   - Appropriate difficulty
   - Question type (factual/reasoning/creative)

2. **Answer Quality (35%)**
   - Accuracy and completeness
   - Logical coherence
   - Based on provided content
   - Professional and credible

3. **Text Relevance (25%)**
   - Q&A alignment with source text
   - Text support for answer
   - Logical consistency (for distilled datasets)

4. **Overall Consistency (15%)**
   - Logical loop between Q, A, and text
   - Suitability for model training
   - No obvious errors or inconsistencies

### Output Format

The evaluation prompt expects JSON output:

```json
{
  "score": 4.5,
  "evaluation": "Detailed evaluation with strengths, weaknesses, and suggestions..."
}
```

Score range: 0-5 (in 0.5 increments)

## Template Variable Substitution

All prompt templates use `{{variable}}` syntax for placeholders:

```python
from easy_dataset.llm.prompts.question_prompts import substitute_variables

template = "Hello {{name}}, you are {{age}} years old."
variables = {'name': 'Alice', 'age': 30}

result = substitute_variables(template, variables)
# Result: "Hello Alice, you are 30 years old."
```

## Custom Prompts

All prompt generation functions accept a `custom_prompt` parameter:

```python
# Define your custom template
my_template = """
Custom prompt with {{variable1}} and {{variable2}}
"""

# Use it with any prompt function
prompt = get_question_prompt(
    language='en',
    text=text,
    custom_prompt=my_template
)
```

This allows you to:
- Override default prompts
- Implement domain-specific templates
- A/B test different prompt strategies
- Integrate with custom prompt management systems

## Language Support

### Supported Languages

- **English (en)**: Full support
- **Chinese (zh)**: Full support (Simplified Chinese)
- **Turkish (tr)**: Full support

### Language Selection

```python
# English
prompt = get_question_prompt(language='en', text=text)

# Chinese
prompt = get_question_prompt(language='zh', text=text)

# Turkish
prompt = get_question_prompt(language='tr', text=text)
```

## Integration with LLM Providers

These prompts work with any LLM provider:

```python
from easy_dataset.llm.prompts import get_question_prompt
from easy_dataset.llm.providers import OpenAIProvider

# Generate prompt
prompt = get_question_prompt(language='en', text=text)

# Use with LLM provider
provider = OpenAIProvider(config={'api_key': 'sk-...', 'model': 'gpt-4'})
response = await provider.chat([{'role': 'user', 'content': prompt}])
```

## Examples

See `examples/prompt_usage_example.py` for complete working examples:

```bash
cd python-backend
python examples/prompt_usage_example.py
```

## Best Practices

1. **Choose appropriate language**: Match the language to your text content
2. **Use Genre-Audience pairs**: For specialized question generation
3. **Leverage templates**: Use question templates for structured outputs
4. **Custom prompts**: Override defaults for domain-specific needs
5. **Evaluate quality**: Use evaluation prompts to assess dataset quality
6. **Clean data first**: Use cleaning prompts before generation tasks

## API Reference

### Question Generation

```python
get_question_prompt(
    language: str,              # 'en', 'zh', 'tr'
    text: str,                  # Text to analyze
    number: Optional[int],      # Number of questions (default: len(text)//240)
    active_ga_pair: Optional[Dict],  # Genre-audience configuration
    custom_prompt: Optional[str]     # Custom template
) -> str
```

### Answer Generation

```python
get_answer_prompt(
    language: str,              # 'en', 'zh', 'tr'
    text: str,                  # Reference text (context)
    question: str,              # Question to answer
    question_template: Optional[Dict],  # Template configuration
    custom_prompt: Optional[str]        # Custom template
) -> str
```

### Data Cleaning

```python
get_data_clean_prompt(
    language: str,              # 'en', 'zh', 'tr'
    text: str,                  # Text to clean
    custom_prompt: Optional[str]  # Custom template
) -> str
```

### Dataset Evaluation

```python
get_dataset_evaluation_prompt(
    language: str,              # 'en', 'zh', 'tr'
    chunk_content: str,         # Original text (empty for distilled)
    question: str,              # Question to evaluate
    answer: str,                # Answer to evaluate
    custom_prompt: Optional[str]  # Custom template
) -> str
```

## Future Enhancements

Potential improvements for the prompt system:

1. **Prompt versioning**: Track and manage prompt template versions
2. **A/B testing**: Built-in support for prompt experimentation
3. **Prompt analytics**: Track which prompts produce best results
4. **More languages**: Add support for additional languages
5. **Prompt optimization**: Automatic prompt refinement based on results
6. **Template library**: Pre-built templates for common use cases

## Contributing

When adding new prompt templates:

1. Follow the existing structure and naming conventions
2. Support all three languages (en, zh, tr)
3. Include comprehensive docstrings
4. Add examples to the usage example file
5. Update this README with new functionality
6. Write tests for new prompt functions

## License

This prompt system is part of Easy Dataset and follows the same license (AGPL-3.0).
