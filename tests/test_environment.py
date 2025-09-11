import os
import sys
import unittest

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestEnvironment(unittest.TestCase):
    """Test basic environment and imports."""

    def test_python_version(self):
        """Ensure we're running on Python 3.12+."""
        self.assertGreaterEqual(sys.version_info[:2], (3, 12))

    def test_basic_imports(self):
        """Test that core dependencies can be imported."""
        try:
            import fastapi
            import openai
            import requests
            import streamlit
            import stripe
            import uvicorn
        except ImportError as e:
            self.fail(f"Failed to import core dependency: {e}")

    def test_development_tools(self):
        """Test that development tools are available."""
        try:
            import mypy
            import pytest
            import ruff
        except ImportError as e:
            self.fail(f"Failed to import development tool: {e}")

    def test_project_structure(self):
        """Verify expected project directories exist."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        expected_dirs = ["branchberg", "branchbot", "ops", "ops_out", "tests"]

        for dir_name in expected_dirs:
            dir_path = os.path.join(project_root, dir_name)
            self.assertTrue(
                os.path.isdir(dir_path), f"Directory {dir_name} should exist"
            )

    def test_config_files(self):
        """Verify essential config files exist."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        expected_files = [
            ".env.example",
            "Makefile",
            "requirements.txt",
            "requirements_final.txt",
            "BRANCHBOT_BRIDGE.md",
        ]

        for file_name in expected_files:
            file_path = os.path.join(project_root, file_name)
            self.assertTrue(os.path.isfile(file_path), f"File {file_name} should exist")


if __name__ == "__main__":
    unittest.main()
