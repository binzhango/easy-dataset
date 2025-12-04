# Internationalization (i18n) Implementation

## Overview

The Easy Dataset Python backend includes comprehensive internationalization (i18n) support for multiple languages. This document describes the implementation, usage, and how to add new languages or translations.

## Supported Languages

- **English (en)**: Default language
- **Chinese Simplified (zh-CN)**: 简体中文
- **Turkish (tr)**: Türkçe

## Architecture

### Core Components

1. **I18n Class** (`easy_dataset/utils/i18n.py`): Main internationalization manager
   - Singleton pattern for global state management
   - Thread-safe implementation
   - Automatic translation file loading
   - Language detection from HTTP headers
   - Variable interpolation support

2. **Translation Files** (`locales/*/messages.json`): JSON-based translation storage
   - Nested structure for organization
   - Support for variable placeholders
   - Easy to edit and maintain

### Directory Structure

```
python-backend/
├── easy_dataset/
│   └── utils/
│       └── i18n.py          # Core i18n implementation
├── locales/
│   ├── en/
│   │   └── messages.json    # English translations
│   ├── zh-CN/
│   │   └── messages.json    # Chinese translations
│   └── tr/
│       └── messages.json    # Turkish translations
└── tests/
    └── test_i18n.py         # i18n tests
```

## Usage

### Basic Usage

```python
from easy_dataset.utils.i18n import t, set_language, get_language

# Set the current language
set_language('zh-CN')

# Translate a key
message = t('common.success')  # Returns: "成功"

# Get current language
current_lang = get_language()  # Returns: "zh-CN"
```

### Translation with Variables

```python
from easy_dataset.utils.i18n import t

# Translation with variable interpolation
error_msg = t('errors.file_not_found', path='/data/file.txt')
# Returns: "File not found: /data/file.txt" (in English)
# Returns: "文件未找到: /data/file.txt" (in Chinese)

# Multiple variables
progress = t('tasks.messages.task_progress', 
             completed=5, total=10, percentage=50)
# Returns: "Progress: 5/10 (50%)"
```

### Language Detection

```python
from easy_dataset.utils.i18n import detect_language, set_language

# Detect language from HTTP Accept-Language header
accept_lang = request.headers.get('Accept-Language')
detected_lang = detect_language(accept_lang)
set_language(detected_lang)
```

### Using the I18n Instance Directly

```python
from easy_dataset.utils.i18n import get_i18n

i18n = get_i18n()

# Set language
i18n.set_language('tr')

# Translate
message = i18n.translate('common.loading')  # Returns: "Yükleniyor..."

# Get supported languages
languages = i18n.get_supported_languages()  # Returns: ['en', 'zh-CN', 'tr']
```

### In FastAPI Applications

```python
from fastapi import FastAPI, Request
from easy_dataset.utils.i18n import detect_language, set_language, t

app = FastAPI()

@app.middleware("http")
async def language_middleware(request: Request, call_next):
    # Detect and set language from request headers
    accept_lang = request.headers.get('Accept-Language')
    lang = detect_language(accept_lang)
    set_language(lang)
    
    response = await call_next(request)
    return response

@app.get("/api/status")
async def get_status():
    return {
        "status": t('common.success'),
        "message": t('api.request_processed')
    }
```

## Translation File Format

Translation files use nested JSON structure with dot notation for keys:

```json
{
  "common": {
    "success": "Success",
    "error": "Error",
    "loading": "Loading..."
  },
  "errors": {
    "file_not_found": "File not found: {{path}}",
    "invalid_format": "Invalid format: {{format}}"
  },
  "tasks": {
    "status": {
      "pending": "Pending",
      "processing": "Processing",
      "completed": "Completed"
    }
  }
}
```

### Variable Placeholders

Use `{{variable_name}}` syntax for variable placeholders:

```json
{
  "errors": {
    "file_not_found": "File not found: {{path}}",
    "invalid_value": "Invalid value for {{field}}: {{value}}"
  }
}
```

## Adding New Languages

### Step 1: Create Translation Directory

```bash
mkdir -p python-backend/locales/[language-code]
```

### Step 2: Create Translation File

Create `messages.json` in the new language directory:

```bash
touch python-backend/locales/[language-code]/messages.json
```

### Step 3: Add Translations

Copy the structure from `locales/en/messages.json` and translate all values:

```json
{
  "common": {
    "success": "[Translation]",
    "error": "[Translation]",
    ...
  },
  ...
}
```

### Step 4: Register Language

Update `easy_dataset/utils/i18n.py`:

```python
class I18n:
    # Add new language code to supported languages
    SUPPORTED_LANGUAGES = ['en', 'zh-CN', 'tr', 'new-lang']
```

### Step 5: Test

```python
from easy_dataset.utils.i18n import set_language, t

set_language('new-lang')
assert t('common.success') == '[Expected Translation]'
```

## Translation Categories

### Common Messages
- `common.*`: General UI messages (success, error, loading, etc.)

### Error Messages
- `errors.*`: Error messages with context
- Includes file errors, database errors, API errors, validation errors

### Task Messages
- `tasks.status.*`: Task status labels
- `tasks.types.*`: Task type names
- `tasks.messages.*`: Task progress and completion messages

### File Processing
- `file_processing.*`: Messages for document processing operations
- Includes extraction, parsing, splitting, metadata operations

### LLM Integration
- `llm.*`: Messages for LLM API interactions
- Includes connection, requests, responses, errors

### Prompts
- `prompts.*`: System and user prompts for LLM operations
- Includes question generation, answer generation, data cleaning, evaluation

### Export
- `export.*`: Messages for dataset export operations
- Includes formatting, validation, file writing

### Validation
- `validation.*`: Data validation messages

### Database
- `database.*`: Database operation messages

### API
- `api.*`: API request/response messages

## Best Practices

### 1. Use Descriptive Keys

```python
# Good
t('errors.file_not_found', path=file_path)

# Avoid
t('error1', path=file_path)
```

### 2. Keep Translations Consistent

Maintain consistent terminology across all languages:
- Use the same technical terms
- Keep formatting consistent
- Preserve variable placeholders

### 3. Provide Context in Keys

```python
# Good - clear context
t('tasks.messages.task_completed')
t('export.json_export')

# Avoid - ambiguous
t('completed')
t('export')
```

### 4. Handle Missing Translations

The system automatically falls back to English if a translation is missing:

```python
# If 'new.key' doesn't exist in Chinese, it will use English
set_language('zh-CN')
message = t('new.key')  # Falls back to English translation
```

### 5. Test All Languages

Always test translations in all supported languages:

```python
def test_translation_exists():
    for lang in ['en', 'zh-CN', 'tr']:
        set_language(lang)
        assert t('common.success') != 'common.success'
```

## Integration with Services

### Task Service Example

```python
from easy_dataset.utils.i18n import t

class TaskService:
    def create_task(self, task_type: str):
        # Use translated messages
        logger.info(t('tasks.messages.task_created', task_id=task.id))
        return task
    
    def update_progress(self, completed: int, total: int):
        percentage = (completed / total) * 100
        message = t('tasks.messages.task_progress',
                   completed=completed,
                   total=total,
                   percentage=percentage)
        return message
```

### Error Handling Example

```python
from easy_dataset.utils.i18n import t
from fastapi import HTTPException

def process_file(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=t('errors.file_not_found', path=file_path)
        )
```

## Testing

Run i18n tests:

```bash
cd python-backend
python -m pytest tests/test_i18n.py -v
```

Test coverage includes:
- Singleton pattern
- Language switching
- Translation lookup
- Variable interpolation
- Language detection
- Fallback behavior
- Dynamic translation addition

## Performance Considerations

1. **Singleton Pattern**: Only one I18n instance exists, reducing memory overhead
2. **Lazy Loading**: Translations are loaded once at initialization
3. **Thread Safety**: Thread-safe implementation for concurrent requests
4. **Caching**: Translations are cached in memory for fast access

## Future Enhancements

Potential improvements for future versions:

1. **Pluralization Support**: Handle singular/plural forms
2. **Date/Time Formatting**: Locale-specific date and time formatting
3. **Number Formatting**: Locale-specific number formatting
4. **RTL Language Support**: Right-to-left language support
5. **Translation Management UI**: Web interface for managing translations
6. **Translation Validation**: Automated checks for missing translations
7. **Context-Aware Translations**: Different translations based on context

## Troubleshooting

### Translations Not Loading

**Problem**: Translations return keys instead of translated text

**Solution**: 
1. Check that translation files exist in `locales/[lang]/messages.json`
2. Verify JSON syntax is valid
3. Ensure the locales directory is in the correct location
4. Check file permissions

### Language Not Switching

**Problem**: Language doesn't change when calling `set_language()`

**Solution**:
1. Verify the language code is in `SUPPORTED_LANGUAGES`
2. Check that translation files exist for that language
3. Ensure you're using the global instance or calling `set_language()` correctly

### Variable Interpolation Not Working

**Problem**: Variables not being replaced in translations

**Solution**:
1. Check that placeholders use `{{variable}}` syntax
2. Verify variable names match between code and translation
3. Ensure variables are passed as keyword arguments

## Contributing

When adding new translations:

1. Follow the existing structure and naming conventions
2. Test all translations thoroughly
3. Ensure consistency across all languages
4. Update this documentation if adding new categories
5. Run tests to verify functionality

## License

This i18n implementation is part of the Easy Dataset project and follows the same license (AGPL-3.0).
