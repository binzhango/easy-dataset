@echo off
REM Development environment setup script for Easy Dataset Python backend (Windows)

echo Setting up Easy Dataset Python development environment...
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo uv is not installed.
    echo Please install uv first:
    echo   Visit: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

echo uv is installed
echo.

REM Create virtual environment
echo Creating virtual environment with uv...
uv venv
echo Virtual environment created at .venv
echo.

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call .venv\Scripts\activate.bat

echo Installing development dependencies...
uv pip install -r requirements-dev.txt

echo Installing easy-dataset package in editable mode...
uv pip install -e .

echo.
echo Setup complete!
echo.
echo To activate the virtual environment, run:
echo   .venv\Scripts\activate.bat
echo.
echo Available commands:
echo   pytest             - Run tests
echo   ruff check         - Run linting
echo   black .            - Format code
echo   mypy easy_dataset  - Run type checking
echo.
echo Or use the CLI:
echo   easy-dataset --help
