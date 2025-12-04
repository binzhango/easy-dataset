.PHONY: help install install-dev test lint format type-check clean build venv

help:
	@echo "Easy Dataset Python - Development Commands"
	@echo ""
	@echo "venv             Create uv virtual environment"
	@echo "install          Install package in production mode"
	@echo "install-dev      Install package with development dependencies"
	@echo "test             Run test suite"
	@echo "test-cov         Run tests with coverage report"
	@echo "lint             Run linting checks"
	@echo "format           Format code with black"
	@echo "type-check       Run type checking with mypy"
	@echo "clean            Clean build artifacts"
	@echo "build            Build distribution packages"

venv:
	uv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source .venv/bin/activate  (Unix/macOS)"
	@echo "  .venv\\Scripts\\activate  (Windows)"

install:
	uv pip install -e .

install-dev:
	uv pip install -r requirements-dev.txt
	uv pip install -e .

test:
	pytest

test-cov:
	pytest --cov=easy_dataset --cov=easy_dataset_server --cov-report=html --cov-report=term

lint:
	ruff check easy_dataset/ easy_dataset_server/ tests/

format:
	black easy_dataset/ easy_dataset_server/ tests/ examples/
	ruff check --fix easy_dataset/ easy_dataset_server/ tests/

type-check:
	mypy easy_dataset/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build
