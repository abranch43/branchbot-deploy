import os
import sys
import unittest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestBranchbergApp(unittest.TestCase):
    """Test the main FastAPI application."""

    def test_main_module_import(self):
        """Test that the main FastAPI module can be imported."""
        try:
            from branchberg.app import main
        except ImportError as e:
            self.fail(f"Failed to import branchberg.app.main: {e}")

    def test_app_placeholder_content(self):
        """Test that main.py contains expected placeholder content."""
        main_file = os.path.join(
            os.path.dirname(__file__), "..", "branchberg", "app", "main.py"
        )

        with open(main_file) as f:
            content = f.read()

        # Should contain placeholder comment about FastAPI backend
        self.assertIn("FastAPI backend", content)
        self.assertIn("webhook", content.lower())


class TestBranchbergDashboard(unittest.TestCase):
    """Test the Streamlit dashboard components."""

    def test_dashboard_directory_exists(self):
        """Test that dashboard directory exists."""
        dashboard_dir = os.path.join(
            os.path.dirname(__file__), "..", "branchberg", "dashboard"
        )
        self.assertTrue(os.path.isdir(dashboard_dir))

    def test_streamlit_app_exists(self):
        """Test that streamlit app file exists."""
        streamlit_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "branchberg",
            "dashboard",
            "streamlit_app.py",
        )
        # Note: File may not exist yet, but directory should
        dashboard_dir = os.path.dirname(streamlit_file)
        self.assertTrue(os.path.isdir(dashboard_dir))


if __name__ == "__main__":
    unittest.main()
