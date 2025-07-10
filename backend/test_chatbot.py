import unittest
import chatbot
import logging
from unittest.mock import patch, mock_open

class TestChatbotCore(unittest.TestCase):

    def setUp(self):
        chatbot.questions.clear()
        chatbot.DEBUG = False
        # Remove all logging handlers before each test to avoid side effects
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()
        # Always patch open so nothing writes to disk for ANY test
        self.open_patcher = patch("builtins.open", mock_open())
        self.mock_open = self.open_patcher.start()
        # Default: patch os.path.exists to False (file doesn't exist)
        self.path_exists_patcher = patch("os.path.exists", return_value=False)
        self.mock_path_exists = self.path_exists_patcher.start()

    def tearDown(self):
        self.open_patcher.stop()
        self.path_exists_patcher.stop()

    def test_setup_logging_enabled_info(self):
        with patch("chatbot.logging.basicConfig") as mock_config:
            chatbot.setup_logging(True, 'INFO')
            mock_config.assert_called_with(
                filename='app.log',
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                encoding='utf-8',
                force=True
            )

    def test_add_question_new(self):
        result = chatbot.add_question("What is AI?", "AI stands for Artificial Intelligence.")
        self.assertTrue(result)
        self.assertIn("what is ai?", chatbot.questions)
        self.assertEqual(chatbot.questions["what is ai?"], ["AI stands for Artificial Intelligence."])

    def test_add_question_existing(self):
        chatbot.questions["what is ai?"] = ["First answer."]
        result = chatbot.add_question("What is AI?", "Second answer.")
        self.assertTrue(result)
        self.assertEqual(
            chatbot.questions["what is ai?"],
            ["First answer.", "Second answer."]
        )

    def test_answer_question_found(self):
        chatbot.questions["what is ai?"] = ["Artificial Intelligence"]
        answer = chatbot.answer_question("What is AI?")
        self.assertEqual(answer, "Artificial Intelligence")

    def test_answer_question_not_found(self):
        chatbot.questions.clear()
        answer = chatbot.answer_question("Unknown?")
        self.assertEqual(answer, "I don't have an answer for that question.")

    def test_import_questions_from_csv_valid(self):
        csv_content = "question,answer1\nWhat is Python?,A programming language\n"
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=csv_content)):
                chatbot.import_questions_from_csv("dummy.csv")
        self.assertIn("what is python?", chatbot.questions)
        self.assertEqual(chatbot.questions["what is python?"], ["A programming language"])

    def test_import_questions_from_csv_invalid_header(self):
        csv_content = "notquestion,notanswer\nsomething,somethingelse\n"
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=csv_content)):
                with patch("chatbot.logging.warning") as log_warn:
                    chatbot.import_questions_from_csv("dummy.csv")
                    log_warn.assert_called()

    def test_save_questions_to_csv_success(self):
        data = {"what is ai?": ["AI stands for Artificial Intelligence."]}
        m = mock_open()
        with patch("builtins.open", m):
            result = chatbot.save_questions_to_csv("test.csv", data)
        self.assertTrue(result)

    def test_save_questions_to_csv_error(self):
        data = {"q": ["a"]}
        with patch("builtins.open", side_effect=PermissionError):
            result = chatbot.save_questions_to_csv("test.csv", data)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()