import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

from app.services.db_serializers import serialize_mock_chat, serialize_process_task


class DatabaseSerializersTest(unittest.TestCase):
    def test_serialize_mock_chat_exposes_api_shape(self):
        chat = SimpleNamespace(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            mock_chat_id="mock_chat_001",
            source_platform="mock_wechat",
            business_line="默认业务线",
            product_name="默认产品",
            scenario_type="product_consulting",
            raw_content={"messages": [{"content": "产品能做什么？"}]},
            created_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, 10, 1, tzinfo=UTC),
        )

        result = serialize_mock_chat(chat)

        self.assertEqual(result["id"], "00000000-0000-0000-0000-000000000001")
        self.assertEqual(result["mock_chat_id"], "mock_chat_001")
        self.assertEqual(result["raw_content"]["messages"][0]["content"], "产品能做什么？")
        self.assertEqual(result["created_at"], "2026-01-01T10:00:00+00:00")

    def test_serialize_process_task_exposes_status_and_step_result(self):
        task = SimpleNamespace(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            task_no="task_mock_chat_001_20260101100000",
            mock_chat_id=UUID("00000000-0000-0000-0000-000000000001"),
            triggered_by=UUID("00000000-0000-0000-0000-000000000003"),
            status="success",
            current_step="completed",
            progress=100,
            error_message=None,
            retry_count=0,
            step_result={"status": "success"},
            created_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, 10, 1, tzinfo=UTC),
            completed_at=datetime(2026, 1, 1, 10, 2, tzinfo=UTC),
        )

        result = serialize_process_task(task)

        self.assertEqual(result["id"], "00000000-0000-0000-0000-000000000002")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["progress"], 100)
        self.assertEqual(result["step_result"], {"status": "success"})
        self.assertEqual(result["completed_at"], "2026-01-01T10:02:00+00:00")


if __name__ == "__main__":
    unittest.main()
