# i18n Quick Reference Guide

## Quick Start

```python
from easy_dataset.utils.i18n import t, set_language

# Set language
set_language('zh-CN')  # Options: 'en', 'zh-CN', 'tr'

# Translate
message = t('common.success')  # Returns: "成功"
```

## Common Functions

### Set Language
```python
from easy_dataset.utils.i18n import set_language

set_language('en')      # English
set_language('zh-CN')   # Chinese
set_language('tr')      # Turkish
```

### Get Current Language
```python
from easy_dataset.utils.i18n import get_language

current = get_language()  # Returns: 'en', 'zh-CN', or 'tr'
```

### Translate
```python
from easy_dataset.utils.i18n import t

# Simple translation
msg = t('common.success')

# With variables
error = t('errors.file_not_found', path='/data/file.txt')
progress = t('tasks.messages.task_progress', completed=5, total=10, percentage=50)
```

### Detect Language
```python
from easy_dataset.utils.i18n import detect_language

# From HTTP header
lang = detect_language('zh-CN,zh;q=0.9,en;q=0.8')  # Returns: 'zh-CN'
```

## Translation Keys

### Common Messages
```python
t('common.success')        # Success / 成功 / Başarılı
t('common.error')          # Error / 错误 / Hata
t('common.loading')        # Loading... / 加载中... / Yükleniyor...
t('common.processing')     # Processing... / 处理中... / İşleniyor...
t('common.completed')      # Completed / 已完成 / Tamamlandı
t('common.failed')         # Failed / 失败 / Başarısız
```

### Error Messages
```python
t('errors.file_not_found', path='/path/to/file')
t('errors.invalid_file_format', format='xyz')
t('errors.file_too_large', max_size=100)
t('errors.authentication_failed')
t('errors.rate_limit_exceeded')
t('errors.timeout_error')
```

### Task Messages
```python
# Status
t('tasks.status.pending')      # Pending / 待处理 / Beklemede
t('tasks.status.processing')   # Processing / 处理中 / İşleniyor
t('tasks.status.completed')    # Completed / 已完成 / Tamamlandı
t('tasks.status.failed')       # Failed / 失败 / Başarısız

# Types
t('tasks.types.file_processing')
t('tasks.types.question_generation')
t('tasks.types.answer_generation')

# Progress
t('tasks.messages.task_progress', completed=5, total=10, percentage=50)
t('tasks.messages.task_completed')
t('tasks.messages.task_failed', error='Error message')
```

### File Processing
```python
t('file_processing.extracting_text', format='PDF')
t('file_processing.parsing_document')
t('file_processing.splitting_text')
t('file_processing.chunks_created', count=10)
```

### LLM Messages
```python
t('llm.connecting', provider='OpenAI')
t('llm.sending_request')
t('llm.receiving_response')
t('llm.retrying', attempt=2, max_attempts=3)
```

### LLM Prompts
```python
# Question generation
t('prompts.question_generation.system')
t('prompts.question_generation.user', count=5, text='...')
t('prompts.question_generation.instruction')

# Answer generation
t('prompts.answer_generation.system')
t('prompts.answer_generation.user', question='...', context='...')
t('prompts.answer_generation.instruction')

# Data cleaning
t('prompts.data_cleaning.system')
t('prompts.data_cleaning.user', text='...')

# Evaluation
t('prompts.evaluation.system')
t('prompts.evaluation.user', question='...', answer='...')
```

### Export Messages
```python
t('export.preparing_data')
t('export.formatting_data', format='JSON')
t('export.writing_file', filename='dataset.json')
t('export.export_completed', filename='dataset.json')
```

## FastAPI Integration

### Middleware
```python
from fastapi import FastAPI, Request
from easy_dataset.utils.i18n import detect_language, set_language

app = FastAPI()

@app.middleware("http")
async def language_middleware(request: Request, call_next):
    accept_lang = request.headers.get('Accept-Language')
    lang = detect_language(accept_lang)
    set_language(lang)
    response = await call_next(request)
    return response
```

### Endpoint
```python
from easy_dataset.utils.i18n import t

@app.get("/api/status")
async def get_status():
    return {
        "status": t('common.success'),
        "message": t('api.request_processed')
    }
```

### Error Handling
```python
from fastapi import HTTPException
from easy_dataset.utils.i18n import t

@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    if not file_exists(file_id):
        raise HTTPException(
            status_code=404,
            detail=t('errors.file_not_found', path=file_id)
        )
    return {"file": file_id}
```

## Testing

```python
from easy_dataset.utils.i18n import set_language, t

def test_translation():
    # Test English
    set_language('en')
    assert t('common.success') == 'Success'
    
    # Test Chinese
    set_language('zh-CN')
    assert t('common.success') == '成功'
    
    # Test Turkish
    set_language('tr')
    assert t('common.success') == 'Başarılı'
```

## Variable Interpolation

### Single Variable
```python
t('errors.file_not_found', path='/data/file.txt')
# English: "File not found: /data/file.txt"
# Chinese: "文件未找到: /data/file.txt"
```

### Multiple Variables
```python
t('tasks.messages.task_progress', completed=5, total=10, percentage=50)
# English: "Progress: 5/10 (50%)"
# Chinese: "进度: 5/10 (50%)"
```

## Supported Languages

| Code | Language | Native Name |
|------|----------|-------------|
| en | English | English |
| zh-CN | Chinese (Simplified) | 简体中文 |
| tr | Turkish | Türkçe |

## Examples

See these files for complete examples:
- `examples/i18n_usage_example.py` - Basic usage examples
- `examples/fastapi_i18n_example.py` - FastAPI integration

## Documentation

- `I18N_IMPLEMENTATION.md` - Detailed documentation
- `I18N_SUMMARY.md` - Implementation summary
- `tests/test_i18n.py` - Test cases

## Tips

1. **Always use translation keys**: Don't hardcode strings
2. **Provide context**: Use descriptive key names
3. **Test all languages**: Verify translations work correctly
4. **Use variables**: Make translations dynamic with interpolation
5. **Handle missing translations**: System falls back to English automatically
