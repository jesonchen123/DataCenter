import unittest

from app.services.manual_mock_chat_service import build_manual_mock_chat_values


class ManualMockChatServiceTest(unittest.TestCase):
    def test_builds_mock_chat_values_from_manual_payload(self):
        payload = {
            "mock_chat_id": "custom_chat_001",
            "source_platform": "manual_test",
            "business_line": "测试业务线",
            "product_name": "测试产品",
            "scenario_type": "price_consulting",
            "messages": [
                {
                    "message_id": "msg_001",
                    "sender_role": "customer",
                    "sender_name": "客户A",
                    "message_time": "2026-06-22T10:00:00+08:00",
                    "content": "这个产品多少钱？",
                },
                {
                    "message_id": "msg_002",
                    "sender_role": "staff",
                    "sender_name": "销售A",
                    "message_time": "2026-06-22T10:01:00+08:00",
                    "content": "历史报价 9800 元，测试过滤。",
                },
            ],
        }

        values = build_manual_mock_chat_values(payload)

        self.assertEqual(values["mock_chat_id"], "custom_chat_001")
        self.assertEqual(values["source_platform"], "manual_test")
        self.assertEqual(values["business_line"], "测试业务线")
        self.assertEqual(values["product_name"], "测试产品")
        self.assertEqual(values["scenario_type"], "price_consulting")
        self.assertEqual(values["raw_content"]["mock_chat_id"], "custom_chat_001")
        self.assertEqual(values["raw_content"]["messages"][0]["sender_role"], "customer")

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


if __name__ == "__main__":
    unittest.main()
