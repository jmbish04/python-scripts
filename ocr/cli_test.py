import unittest
from unittest.mock import MagicMock, patch
import base64
import os

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ocr import run

class TestCli(unittest.TestCase):
    @patch('ocr.requests.post')
    @patch('ocr.prompt')
    @patch('ocr.menu')
    def test_browser_render_flow(self, mock_menu, mock_prompt, mock_post):
        # Mock the response from the worker
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "extracted_text": "This is the extracted text.",
            "embedding": [1, 2, 3],
            "rag": "# RAG content",
            "summary": "This is a summary."
        }
        mock_post.return_value = mock_response

        # Mock user selections
        mock_menu.side_effect = [
            3,  # Website URL (Browser Render)
            1,  # Generate embeddings? Yes
            2,  # RAG format: markdown
            1,  # Add AI summary? Yes
            1,  # Also export to current path? Yes
        ]
        mock_prompt.side_effect = [
            "https://example.com", # URL
            "my-bucket", # R2 bucket
            "my-key", # Output key
        ]

        # Mock the curses screen object
        mock_stdscr = MagicMock()

        # Run the script
        run(mock_stdscr)

        # Assert that requests.post was called with the correct payload
        expected_payload = {
            "input": {"type": "url", "url": "https://example.com", "browser": True},
            "process": {
                "embeddings": True,
                "rag_format": "markdown",
                "summary": True,
            },
            "output": {"bucket": "my-bucket", "key": "my-key", "local": True},
        }
        mock_post.assert_called_once_with(
            "https://ask-my-doc.hacolby.workers.dev/",
            json=expected_payload,
            timeout=60
        )

if __name__ == '__main__':
    unittest.main()
