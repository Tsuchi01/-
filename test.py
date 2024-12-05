import json
import unittest
from unittest.mock import patch, Mock
from t5_helper import T5Helper  # Import your module where T5Helper is defined


class TestT5HelperQuery(unittest.TestCase):
    def setUp(self):
        self.helper = T5Helper()
        self.helper.api_url = "api-inference.huggingface.co"
        self.helper.api_token = "fake_token"

    @patch("http.client.HTTPSConnection")
    def test_query_valid_response(self, mock_https):
        # Mock a valid API response
        mock_conn = Mock()
        mock_https.return_value = mock_conn
        mock_conn.getresponse.return_value.status = 200
        mock_conn.getresponse.return_value.read.return_value = json.dumps(
            [{"generated_text": "Test Response"}]
        ).encode("utf-8")

        result = self.helper.query("Test Prompt")
        self.assertEqual(result[0]["generated_text"], "Test Response")


    @patch("http.client.HTTPSConnection")
    def test_query_network_failure(self, mock_https):
        # Simulate a network failure
        mock_conn = Mock()
        mock_https.return_value = mock_conn
        mock_conn.request.side_effect = Exception("Network Failure")

        result = self.helper.query("Test Prompt")
        self.assertEqual(result["status_code"], 500)
        self.assertIn("Network Failure", result["error"])

    @patch("http.client.HTTPSConnection")
    def test_query_invalid_json_response(self, mock_https):
        # Mock an invalid JSON response
        mock_conn = Mock()
        mock_https.return_value = mock_conn
        mock_conn.getresponse.return_value.status = 200
        mock_conn.getresponse.return_value.read.return_value = "Invalid JSON".encode("utf-8")

        result = self.helper.query("Test Prompt")
        self.assertIn("error", result)
        self.assertEqual(result["status_code"], 500)

    @patch("http.client.HTTPSConnection")
    def test_query_unexpected_error(self, mock_https):
        # Simulate an unexpected error during processing
        mock_conn = Mock()
        mock_https.return_value = mock_conn
        mock_conn.getresponse.side_effect = Exception("Unexpected Error")

        result = self.helper.query("Test Prompt")
        self.assertEqual(result["status_code"], 500)
        self.assertIn("Unexpected Error", result["error"])


if __name__ == "__main__":
    unittest.main()
