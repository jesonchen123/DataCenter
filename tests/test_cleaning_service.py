import unittest

from app.services.cleaning_service import clean_messages, normalize_text


class CleaningServiceTest(unittest.TestCase):
    def test_normalize_text_standardizes_spacing_newlines_and_punctuation(self):
        self.assertEqual(normalize_text("你好，\r\n我想了解产品!  "), "你好，我想了解产品！")

    def test_clean_messages_removes_empty_duplicates_system_prompts_and_greetings(self):
        messages = [
            {"message_id": "1", "sender_role": "system", "content": "系统提示：撤回消息"},
            {"message_id": "2", "sender_role": "customer", "content": ""},
            {"message_id": "3", "sender_role": "customer", "content": "你好"},
            {"message_id": "4", "sender_role": "customer", "content": "产品怎么使用?"},
            {"message_id": "5", "sender_role": "customer", "content": "产品怎么使用？"},
        ]

        cleaned = clean_messages(messages)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["content"], "产品怎么使用？")


if __name__ == "__main__":
    unittest.main()
