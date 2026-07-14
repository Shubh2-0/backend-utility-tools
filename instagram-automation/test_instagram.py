import unittest
from unittest.mock import MagicMock
import sys
import os

# Add directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comment_templates import get_random_comment, is_niche_relevant, TEMPLATES

class TestInstagramCommenter(unittest.TestCase):

    def test_is_niche_relevant_matching(self):
        # Match expected tech keywords
        self.assertTrue(is_niche_relevant("Check out this new Spring Boot tutorial!"))
        self.assertTrue(is_niche_relevant("Learn how to scale Java microservices."))
        self.assertTrue(is_niche_relevant("Understanding system design concepts."))
        self.assertTrue(is_niche_relevant("Writing clean APIs in PostgreSQL."))

        # Filter out irrelevant captions (like fashion, food, travel)
        self.assertFalse(is_niche_relevant("Beautiful red wedding dress."))
        self.assertFalse(is_niche_relevant("Loving this new saree collection from Mumbai."))
        self.assertFalse(is_niche_relevant("Travel vlog from Bali, Indonesia."))

    def test_get_random_comment_template_fallback(self):
        # When caption is empty, it should fall back to templates
        comment = get_random_comment(caption="")
        self.assertTrue(any(template.split(".")[0] in comment for template in TEMPLATES))

    def test_get_random_comment_with_mock_gemini(self):
        # Import the client to mock it
        import comment_templates
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "yeah, completing transactions like this is always clean. we use similar configs in production"
        mock_client.models.generate_content.return_value = mock_response
        
        # Temporarily set the client
        original_client = comment_templates.gemini_client
        comment_templates.gemini_client = mock_client
        
        try:
            comment = get_random_comment(caption="How to handle Spring @Transactional rollbacks")
            self.assertEqual(comment, "yeah, completing transactions like this is always clean. we use similar configs in production")
        finally:
            # Restore client
            comment_templates.gemini_client = original_client

if __name__ == "__main__":
    unittest.main()
