"""
Test package structure and imports.

This test verifies that the package structure is correctly set up
and that basic imports work as expected.
"""

import pytest


def test_package_import():
    """Test that the main package can be imported."""
    import easy_dataset
    assert easy_dataset.__version__ == "2.0.0"


def test_package_metadata():
    """Test that package metadata is correctly set."""
    import easy_dataset
    assert hasattr(easy_dataset, "__version__")
    assert hasattr(easy_dataset, "__author__")
    assert hasattr(easy_dataset, "__license__")
    assert easy_dataset.__license__ == "AGPL-3.0"


def test_subpackage_imports():
    """Test that subpackages can be imported."""
    # These should not raise ImportError
    import easy_dataset.core
    import easy_dataset.models
    import easy_dataset.schemas
    import easy_dataset.llm
    import easy_dataset.llm.providers
    import easy_dataset.llm.prompts
    import easy_dataset.database
    import easy_dataset.utils


def test_server_package_import():
    """Test that the server package can be imported."""
    import easy_dataset_server
    assert easy_dataset_server.__version__ == "2.0.0"


def test_cli_import():
    """Test that the CLI module can be imported."""
    from easy_dataset import cli
    assert hasattr(cli, "main")


def test_cli_commands_exist():
    """Test that CLI commands are registered."""
    from easy_dataset.cli import main
    
    # Get the click group
    assert hasattr(main, "commands")
    
    # Check that expected commands exist
    expected_commands = ["init", "process", "generate-questions", "generate-answers", "export", "serve"]
    for cmd in expected_commands:
        assert cmd in main.commands, f"Command '{cmd}' not found in CLI"
