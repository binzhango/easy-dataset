"""
Example demonstrating i18n integration with FastAPI.

This example shows how to integrate the i18n system with a FastAPI application
for automatic language detection and localized responses.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from easy_dataset.utils.i18n import detect_language, set_language, t, get_language


# Create FastAPI app
app = FastAPI(
    title="Easy Dataset API with i18n",
    description="Example API with internationalization support"
)


@app.middleware("http")
async def language_middleware(request: Request, call_next):
    """
    Middleware to detect and set language from Accept-Language header.
    
    This middleware runs before each request and automatically sets the
    language based on the client's Accept-Language header.
    """
    # Get Accept-Language header
    accept_language = request.headers.get('Accept-Language')
    
    # Detect and set language
    detected_lang = detect_language(accept_language)
    set_language(detected_lang)
    
    # Add language to request state for access in endpoints
    request.state.language = detected_lang
    
    # Process request
    response = await call_next(request)
    
    # Add language header to response
    response.headers['Content-Language'] = detected_lang
    
    return response


@app.get("/")
async def root(request: Request):
    """Root endpoint with localized welcome message."""
    return {
        "message": t('common.success'),
        "language": request.state.language,
        "supported_languages": ["en", "zh-CN", "tr"]
    }


@app.get("/api/status")
async def get_status(request: Request):
    """Get API status with localized messages."""
    return {
        "status": t('common.success'),
        "message": t('api.request_processed'),
        "language": get_language()
    }


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str, request: Request):
    """Get task status with localized messages."""
    # Simulate task data
    task_data = {
        "id": task_id,
        "type": "file_processing",
        "status": "processing",
        "completed": 7,
        "total": 10
    }
    
    # Calculate percentage
    percentage = int((task_data["completed"] / task_data["total"]) * 100)
    
    return {
        "id": task_data["id"],
        "type": t(f'tasks.types.{task_data["type"]}'),
        "status": t(f'tasks.status.{task_data["status"]}'),
        "progress": t('tasks.messages.task_progress',
                     completed=task_data["completed"],
                     total=task_data["total"],
                     percentage=percentage),
        "language": get_language()
    }


@app.post("/api/files/upload")
async def upload_file(request: Request):
    """Simulate file upload with localized messages."""
    # Simulate successful upload
    return {
        "status": t('common.success'),
        "message": t('file_processing.extracting_text', format='PDF'),
        "language": get_language()
    }


@app.get("/api/files/{file_id}")
async def get_file(file_id: str, request: Request):
    """Get file with error handling and localized messages."""
    # Simulate file not found error
    if file_id == "nonexistent":
        raise HTTPException(
            status_code=404,
            detail=t('errors.file_not_found', path=f'/files/{file_id}')
        )
    
    return {
        "id": file_id,
        "status": t('common.success'),
        "message": t('file_processing.chunk_created', chunk_id=file_id),
        "language": get_language()
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler with localized error messages."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": t('common.error'),
            "detail": exc.detail,
            "language": get_language()
        }
    )


@app.get("/api/llm/generate")
async def generate_content(request: Request):
    """Get LLM prompts in the current language."""
    return {
        "system_prompt": t('prompts.question_generation.system'),
        "user_prompt": t('prompts.question_generation.user',
                        count=5,
                        text="Sample text content..."),
        "instruction": t('prompts.question_generation.instruction'),
        "language": get_language()
    }


@app.get("/api/export/status")
async def export_status(request: Request):
    """Get export status with localized messages."""
    return {
        "status": t('common.processing'),
        "message": t('export.formatting_data', format='JSON'),
        "progress": t('tasks.messages.task_progress',
                     completed=50,
                     total=100,
                     percentage=50),
        "language": get_language()
    }


@app.get("/api/languages")
async def get_languages(request: Request):
    """Get list of supported languages with their names."""
    languages = {
        "en": {
            "code": "en",
            "name": "English",
            "native_name": "English",
            "example": "Success"
        },
        "zh-CN": {
            "code": "zh-CN",
            "name": "Chinese (Simplified)",
            "native_name": "简体中文",
            "example": "成功"
        },
        "tr": {
            "code": "tr",
            "name": "Turkish",
            "native_name": "Türkçe",
            "example": "Başarılı"
        }
    }
    
    # Add current language translation
    for lang_code, lang_info in languages.items():
        set_language(lang_code)
        lang_info["success_message"] = t('common.success')
    
    # Reset to request language
    set_language(request.state.language)
    
    return {
        "current_language": get_language(),
        "supported_languages": languages
    }


@app.get("/api/demo/all-messages")
async def demo_all_messages(request: Request):
    """Demo endpoint showing various localized messages."""
    return {
        "language": get_language(),
        "common": {
            "success": t('common.success'),
            "error": t('common.error'),
            "loading": t('common.loading'),
            "processing": t('common.processing'),
            "completed": t('common.completed')
        },
        "tasks": {
            "pending": t('tasks.status.pending'),
            "processing": t('tasks.status.processing'),
            "completed": t('tasks.status.completed'),
            "file_processing": t('tasks.types.file_processing'),
            "question_generation": t('tasks.types.question_generation')
        },
        "errors": {
            "file_not_found": t('errors.file_not_found', path='/example/file.txt'),
            "invalid_format": t('errors.invalid_file_format', format='xyz'),
            "authentication_failed": t('errors.authentication_failed')
        },
        "file_processing": {
            "extracting_text": t('file_processing.extracting_text', format='PDF'),
            "parsing_document": t('file_processing.parsing_document'),
            "chunks_created": t('file_processing.chunks_created', count=10)
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("Easy Dataset API with i18n - Example Server")
    print("=" * 60)
    print("\nStarting server on http://localhost:8000")
    print("\nTry these endpoints with different Accept-Language headers:")
    print("  - curl -H 'Accept-Language: en' http://localhost:8000/")
    print("  - curl -H 'Accept-Language: zh-CN' http://localhost:8000/")
    print("  - curl -H 'Accept-Language: tr' http://localhost:8000/")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
