import unittest
from types import SimpleNamespace
from uuid import UUID

from app.services.persistence_service import build_persistence_values


class PersistenceServiceTest(unittest.TestCase):
    def test_build_persistence_values_maps_pipeline_result_to_database_rows(self):
        task = SimpleNamespace(
            id=UUID("00000000-0000-0000-0000-000000000010"),
            mock_chat_id=UUID("00000000-0000-0000-0000-000000000011"),
            triggered_by=UUID("00000000-0000-0000-0000-000000000012"),
        )
        result = {
            "segments": [
                {
                    "segment_no": "seg_mock_chat_001_001",
                    "original_content": "原始内容",
                    "cleaned_content": "清洗内容",
                    "desensitized_content": "脱敏内容",
                    "price_filtered_content": "价格过滤内容",
                    "customer_question": "怎么使用？",
                    "staff_answer": "先登录后台。",
                    "business_line": "默认业务线",
                    "product_name": "默认产品",
                    "tags": ["mock"],
                    "contains_sensitive_info": True,
                    "contains_price_info": False,
                    "price_filter_status": "success",
                    "price_risk_level": "none",
                    "status": "generated",
                }
            ],
            "knowledge_docs": [
                {
                    "doc_no": "kb_seg_mock_chat_001_001",
                    "title": "怎么使用？",
                    "content": "先登录后台。",
                    "question_examples": ["怎么使用？"],
                    "tags": ["产品咨询"],
                    "business_line": "默认业务线",
                    "product_name": "默认产品",
                    "risk_level": "low",
                    "quality_score": 28,
                    "review_status": "pending_review",
                    "price_filtered": True,
                    "contains_price_intent": False,
                    "contains_original_price": False,
                    "is_desensitized": True,
                }
            ],
        }

        values = build_persistence_values(task, result)

        self.assertEqual(values["segments"][0]["process_task_id"], task.id)
        self.assertEqual(values["segments"][0]["mock_chat_id"], task.mock_chat_id)
        self.assertEqual(values["knowledge_docs"][0]["created_by"], task.triggered_by)
        self.assertEqual(values["knowledge_docs"][0]["segment_no"], "seg_mock_chat_001_001")


if __name__ == "__main__":
    unittest.main()
