import unittest
import os
import sys

# Add the parent directory to the Python path to allow importing the ocr package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ocr.python import process_document

class E2ETest(unittest.TestCase):
    def test_browser_render_e2e(self):
        # Define the payload for the test
        payload = {
            "input": {"type": "url", "url": "https://example.com", "browser": True},
            "process": {
                "embeddings": True,
                "rag_format": "markdown",
                "summary": True,
            },
            "output": {"bucket": "mcp-test-bucket", "key": "e2e-test-output", "local": False},
        }

        # Call the process_document function
        result = process_document(payload)

        # Assert that the request was successful and the response contains the expected fields
        self.assertNotIn("error", result)
        self.assertIn("extracted_text", result)
        self.assertIn("embedding", result)
        self.assertIn("rag", result)
        self.assertIn("summary", result)

if __name__ == '__main__':
    unittest.main()
