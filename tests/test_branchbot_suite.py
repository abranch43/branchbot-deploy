import os
import sys
import unittest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from branchbot_auto_suite import gmail_to_proposal_tracker


class TestBranchbotAutoSuite(unittest.TestCase):
    """Test the BranchBot automation suite."""

    def setUp(self):
        """Set up test environment."""
        # Ensure SAFE_MODE is enabled for testing
        os.environ["SAFE_MODE"] = "true"

    def test_safe_mode_enabled(self):
        """Test that SAFE_MODE is properly enabled."""
        import branchbot_auto_suite

        self.assertTrue(branchbot_auto_suite.SAFE_MODE)

    def test_gmail_to_proposal_tracker_safe_mode(self):
        """Test gmail_to_proposal_tracker in safe mode."""
        # Should not crash and should handle safe mode gracefully
        test_message = {
            "id": "test123",
            "subject": "Test RFP",
            "sender": "test@example.com",
        }

        # This should run without error in safe mode
        try:
            gmail_to_proposal_tracker(test_message)
        except Exception as e:
            self.fail(f"gmail_to_proposal_tracker failed in safe mode: {e}")

    def test_environment_variables_handling(self):
        """Test that missing environment variables are handled gracefully."""
        import branchbot_auto_suite

        # These should be None or safe defaults when not set
        self.assertIsNotNone(branchbot_auto_suite.SAFE_MODE)

        # In safe mode, external integrations should be disabled
        if branchbot_auto_suite.SAFE_MODE:
            self.assertIsNone(branchbot_auto_suite.openai_client)


if __name__ == "__main__":
    unittest.main()
