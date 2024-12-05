import unittest
from unittest.mock import patch, Mock
from t5_helper import T5Helper  # Import your module where T5Helper is defined


class TestT5HelperGenerateSuggestions(unittest.TestCase):
    def setUp(self):
        self.helper = T5Helper()

    @patch.object(T5Helper, 'query')
    def test_generate_suggestions_no_tasks(self, mock_query):
        # No tasks provided
        tasks = []
        result = self.helper.generate_suggestions(tasks)
        self.assertEqual(result, "Немає завдань для аналізу.")

    @patch.object(T5Helper, 'query')
    def test_generate_suggestions_valid_responses(self, mock_query):
        # Mock valid responses for each task
        mock_query.return_value = [{"generated_text": "Do this and that."}]
        tasks = [
            (1, "Task 1", "Description 1", "2024-12-31", 0, 1),
            (2, "Task 2", "Description 2", "2024-12-25", 0, 2)
        ]

        result = self.helper.generate_suggestions(tasks)
        expected_output = (
            "Завдання: Task 1\nРекомендація: Do this and that.\n\n"
            "Завдання: Task 2\nРекомендація: Do this and that.\n"
        )
        self.assertEqual(result, expected_output)

    @patch.object(T5Helper, 'query')
    def test_generate_suggestions_with_query_error(self, mock_query):
        # Simulate an error in the query response
        mock_query.return_value = {"error": "API error", "status_code": 500}
        tasks = [
            (1, "Task 1", "Description 1", "2024-12-31", 0, 1)
        ]

        result = self.helper.generate_suggestions(tasks)
        self.assertIn("Помилка для 'Task 1': API error", result)

    @patch.object(T5Helper, 'query')
    def test_generate_suggestions_missing_generated_text(self, mock_query):
        # Mock response missing 'generated_text'
        mock_query.return_value = [{"other_key": "No generated text here"}]
        tasks = [
            (1, "Task 1", "Description 1", "2024-12-31", 0, 1)
        ]

        result = self.helper.generate_suggestions(tasks)
        self.assertIn("Рекомендація: (Текст не знайдений у відповіді)", result)


if __name__ == "__main__":
    unittest.main()
