#!/bin/bash
# Development environment setup script for Easy Dataset Python backend

set -e

echo "🚀 Setting up Easy Dataset Python development environment..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo "Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "✅ uv is installed"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment with uv..."
uv venv
echo "✅ Virtual environment created at .venv"
echo ""

# Activate virtual environment
echo "🔧 Installing dependencies..."
source .venv/bin/activate

# Install development dependencies
echo "📥 Installing development dependencies..."
uv pip install -r requirements-dev.txt

# Install package in editable mode
echo "📥 Installing easy-dataset package in editable mode..."
uv pip install -e .

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Available commands:"
echo "  make test          - Run tests"
echo "  make lint          - Run linting"
echo "  make format        - Format code"
echo "  make type-check    - Run type checking"
echo ""
echo "Or use the CLI:"
echo "  easy-dataset --help"
