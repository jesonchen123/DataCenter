import unittest

from app.services.document_import_service import validate_message_array


class SchemaTest(unittest.TestCase):
    def test_validate_rejects_time_field_in_messages(self):
        with self.assertRaises(ValueError):
            validate_message_array(
                [
                    {
                        "role": "customer",
                        "sender": "客户A",
                        "time": "2026-06-22T10:00:00+08:00",
                        "text": "时间字段不再接收",
                    }
                ]
            )

    def test_validate_rejects_legacy_message_id_field(self):
        with self.assertRaises(ValueError):
            validate_message_array(
                [
                    {
                        "message_id": "msg_001",
                        "sender_role": "customer",
                        "content": "旧格式不再支持",
                    }
                ]
            )

    def test_validate_accepts_clean_simplified_message(self):
        result = validate_message_array(
            [
                {"role": "customer", "text": "这个产品怎么使用？", "sender": "客户A"},
                {"role": "staff", "text": "先确认使用场景。", "sender": "销售B"},
            ]
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["role"], "customer")
        self.assertEqual(result[1]["text"], "先确认使用场景。")


if __name__ == "__main__":
    unittest.main()
