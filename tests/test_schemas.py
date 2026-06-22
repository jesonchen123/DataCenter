import unittest

from app.schemas import ManualMockChatCreateRequest

try:
    from pydantic import ValidationError
except ModuleNotFoundError:  # pragma: no cover
    ValidationError = None


@unittest.skipIf(ValidationError is None, "pydantic is not installed")
class SchemaTest(unittest.TestCase):
    def test_manual_mock_chat_rejects_time_field(self):
        with self.assertRaises(ValidationError):
            ManualMockChatCreateRequest.model_validate(
                {
                    "mock_chat_id": "schema_chat_001",
                    "messages": [
                        {
                            "role": "customer",
                            "sender": "客户A",
                            "time": "2026-06-22T10:00:00+08:00",
                            "text": "时间字段不再接收",
                        }
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
