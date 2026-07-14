import unittest
from unittest.mock import MagicMock
import re
import os
import sys

# Add directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_interact import generate_smart_comment, has_negativity, strip_oxford_comma

class TestSmartInteract(unittest.TestCase):

    def setUp(self):
        # Create a mock Gemini model
        self.mock_model = MagicMock()

    def test_hiring_post_detection(self):
        # Mock the response to return "HIRING" for a job post
        mock_response = MagicMock()
        mock_response.text = "HIRING"
        self.mock_model.generate_content.return_value = mock_response

        post_text = "We are hiring a Senior Java Developer! Apply today."
        result = generate_smart_comment(self.mock_model, post_text)
        self.assertEqual(result, "HIRING")

    def test_clickbait_post_detection(self):
        # Mock the response to return "CLICKBAIT"
        mock_response = MagicMock()
        mock_response.text = "CLICKBAIT"
        self.mock_model.generate_content.return_value = mock_response

        post_text = "React is dead. Agree or disagree? Comment below!"
        result = generate_smart_comment(self.mock_model, post_text)
        self.assertEqual(result, "CLICKBAIT")

    def test_oxford_comma_stripping(self):
        self.assertEqual(strip_oxford_comma("Java, Spring Boot, and Kafka"), "Java, Spring Boot and Kafka")
        self.assertEqual(strip_oxford_comma("A, B, and C"), "A, B and C")

    def test_negativity_detection(self):
        self.assertTrue(has_negativity("This is a bad approach"))
        self.assertTrue(has_negativity("Actually no, this is wrong"))
        self.assertFalse(has_negativity("Nice tip, we use this in production too"))

    def test_normal_comment_generation(self):
        # Mock the response to return a normal technical comment
        mock_response = MagicMock()
        mock_response.text = "yeah this is spot on, we hit this index issue last week and fixed it"
        self.mock_model.generate_content.return_value = mock_response

        post_text = "Always index your foreign keys to prevent full table scans in PostgreSQL."
        result = generate_smart_comment(self.mock_model, post_text)
        self.assertEqual(result, "yeah this is spot on, we hit this index issue last week and fixed it")

if __name__ == "__main__":
    unittest.main()
