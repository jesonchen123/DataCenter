import unittest

from app.services.manual_mock_chat_service import build_manual_mock_chat_values


class ManualMockChatServiceTest(unittest.TestCase):
    def test_builds_mock_chat_values_from_simplified_payload(self):
        values = build_manual_mock_chat_values(
            {
                "mock_chat_id": "custom_chat_001",
                "source_platform": "manual_test",
                "business_line": "测试业务线",
                "product_name": "测试产品",
                "scenario_type": "price_consulting",
                "messages": [
                    {"role": "customer", "sender": "客户A", "time": "2026-06-22T10:00:00+08:00", "text": "这个产品多少钱？"},
                    {"role": "staff", "sender": "销售A", "time": "2026-06-22T10:01:00+08:00", "text": "历史报价 9800 元，测试过滤。"},
                ],
            }
        )

        messages = values["raw_content"]["messages"]
        self.assertEqual(values["mock_chat_id"], "custom_chat_001")
        self.assertEqual(values["source_platform"], "manual_test")
        self.assertEqual(values["business_line"], "测试业务线")
        self.assertEqual(values["product_name"], "测试产品")
        self.assertEqual(values["scenario_type"], "price_consulting")
        self.assertEqual(values["raw_content"]["mock_chat_id"], "custom_chat_001")
        self.assertEqual(messages[0]["message_id"], "custom_chat_001_msg_001")
        self.assertEqual(messages[0]["sender_role"], "customer")
        self.assertEqual(messages[0]["sender_name"], "客户A")
        self.assertEqual(messages[0]["message_time"], "2026-06-22T10:00:00+08:00")
        self.assertEqual(messages[0]["content"], "这个产品多少钱？")

    def test_rejects_empty_messages(self):
        with self.assertRaises(ValueError):
            build_manual_mock_chat_values(
                {
                    "mock_chat_id": "custom_chat_empty",
                    "source_platform": "manual_test",
                    "messages": [],
                }
            )

    def test_rejects_invalid_sender_role(self):
        with self.assertRaises(ValueError):
            build_manual_mock_chat_values(
                {
                    "mock_chat_id": "custom_chat_bad_role",
                    "source_platform": "manual_test",
                    "messages": [
                        {
                            "message_id": "msg_001",
                            "sender_role": "sales",
                            "content": "非法角色",
                        }
                    ],
                }
            )

    def test_rejects_legacy_standard_message_fields(self):
        with self.assertRaises(ValueError):
            build_manual_mock_chat_values(
                {
                    "mock_chat_id": "custom_chat_legacy",
                    "messages": [
                        {
                            "message_id": "msg_001",
                            "sender_role": "customer",
                            "content": "旧格式不再支持",
                        }
                    ],
                }
            )

    def test_accepts_simplified_role_text_messages(self):
        values = build_manual_mock_chat_values(
            {
                "mock_chat_id": "simple_chat_001",
                "messages": [
                    {"role": "customer", "text": "这个产品多少钱？"},
                    {"role": "staff", "text": "具体价格以公司正式报价为准。"},
                ],
            }
        )

        messages = values["raw_content"]["messages"]
        self.assertEqual(values["source_platform"], "manual_test")
        self.assertEqual(messages[0]["message_id"], "simple_chat_001_msg_001")
        self.assertEqual(messages[0]["sender_role"], "customer")
        self.assertEqual(messages[0]["content"], "这个产品多少钱？")
        self.assertEqual(messages[1]["message_id"], "simple_chat_001_msg_002")
        self.assertEqual(messages[1]["sender_role"], "staff")

    def test_accepts_sender_text_alias_for_simplified_messages(self):
        values = build_manual_mock_chat_values(
            {
                "mock_chat_id": "simple_chat_002",
                "messages": [
                    {"role": "customer", "sender": "客户A", "text": "怎么使用？"},
                ],
            }
        )

        self.assertEqual(values["raw_content"]["messages"][0]["sender_name"], "客户A")


if __name__ == "__main__":
    unittest.main()
