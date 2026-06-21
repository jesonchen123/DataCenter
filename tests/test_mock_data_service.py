import unittest

from app.services.mock_data_service import build_mock_chats


class MockDataServiceTest(unittest.TestCase):
    def test_builds_at_least_twenty_mock_chats(self):
        chats = build_mock_chats()

        self.assertGreaterEqual(len(chats), 20)
        self.assertEqual(len({chat["mock_chat_id"] for chat in chats}), len(chats))

    def test_covers_required_business_scenarios(self):
        chats = build_mock_chats()
        scenarios = {chat["scenario_type"] for chat in chats}

        self.assertIn("product_consulting", scenarios)
        self.assertIn("after_sales", scenarios)
        self.assertIn("price_consulting", scenarios)
        self.assertIn("customer_objection", scenarios)

    def test_each_chat_has_required_mock_payload_shape(self):
        for chat in build_mock_chats():
            with self.subTest(chat=chat["mock_chat_id"]):
                self.assertIn("source_platform", chat)
                self.assertIn("business_line", chat)
                self.assertIn("product_name", chat)
                self.assertIn("messages", chat["raw_content"])
                self.assertGreaterEqual(len(chat["raw_content"]["messages"]), 2)


if __name__ == "__main__":
    unittest.main()
