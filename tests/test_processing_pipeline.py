import unittest

from app.domain.enums import RiskLevel
from app.services.processing_pipeline import process_mock_chat_payload


class ProcessingPipelineTest(unittest.TestCase):
    def test_processes_mock_chat_payload_through_core_steps(self):
        payload = {
            "mock_chat_id": "mock_chat_price",
            "business_line": "默认业务线",
            "product_name": "默认产品",
            "messages": [
                {"message_id": "m1", "sender_role": "customer", "content": "你好"},
                {"message_id": "m2", "sender_role": "customer", "content": "这个产品多少钱？我的电话 13812345678"},
                {"message_id": "m3", "sender_role": "staff", "content": "基础版 999 元，高级版 2999 元。"},
                {"message_id": "m4", "sender_role": "staff", "content": "产品支持企业内部知识库问答。"},
            ],
        }

        result = process_mock_chat_payload(payload)

        self.assertEqual(result["mock_chat_id"], "mock_chat_price")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["segments"]), 1)
        segment = result["segments"][0]
        doc = result["knowledge_docs"][0]
        self.assertIn("<PHONE>", segment["desensitized_content"])
        self.assertNotIn("999", segment["price_filtered_content"])
        self.assertTrue(segment["contains_price_info"])
        self.assertEqual(segment["price_risk_level"], RiskLevel.HIGH.value)
        self.assertFalse(doc["contains_original_price"])
        self.assertIn("具体价格以公司正式报价为准", doc["content"])

    def test_process_mock_chat_payload_uses_injected_knowledge_generator(self):
        calls = []

        def fake_generator(segment):
            calls.append(segment)
            return {
                "doc_no": f"kb_{segment['segment_no']}",
                "title": "LLM 生成标题",
                "content": "LLM 生成正文",
                "question_examples": ["如何使用？"],
                "tags": ["LLM"],
                "business_line": segment["business_line"],
                "product_name": segment["product_name"],
                "risk_level": "low",
                "quality_score": 30,
                "review_status": "pending_review",
                "price_filtered": True,
                "contains_price_intent": False,
                "contains_original_price": False,
                "is_desensitized": True,
                "need_human_review": False,
            }

        payload = {
            "mock_chat_id": "mock_chat_llm",
            "business_line": "默认业务线",
            "product_name": "默认产品",
            "messages": [
                {"message_id": "m1", "sender_role": "customer", "content": "如何使用？"},
                {"message_id": "m2", "sender_role": "staff", "content": "可以先创建知识库。"},
            ],
        }

        result = process_mock_chat_payload(payload, knowledge_generator=fake_generator)

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["segment_no"], "seg_mock_chat_llm_001")
        self.assertEqual(result["knowledge_docs"][0]["title"], "LLM 生成标题")

    def test_cleaned_segment_is_customer_staff_qa_without_metadata(self):
        payload = {
            "mock_chat_id": "mock_chat_clean_qa",
            "messages": [
                {
                    "message_id": "m1",
                    "sender_role": "customer",
                    "sender_name": "客户A",
                    "message_time": "2026-06-22T10:00:00+08:00",
                    "content": "产品怎么使用？",
                },
                {
                    "message_id": "m2",
                    "sender_role": "staff",
                    "sender_name": "销售A",
                    "message_time": "2026-06-22T10:01:00+08:00",
                    "content": "先登录后台，再创建知识库。",
                },
            ],
        }

        result = process_mock_chat_payload(payload)

        segment = result["segments"][0]
        self.assertEqual(segment["cleaned_content"], "客户问：产品怎么使用？\n销售答：先登录后台，再创建知识库。")
        self.assertNotIn("2026-06-22", segment["cleaned_content"])
        self.assertNotIn("客户A", segment["cleaned_content"])
        self.assertNotIn("销售A", segment["cleaned_content"])
        self.assertNotIn("message_id", segment["cleaned_content"])
        self.assertEqual(result["knowledge_docs"][0]["content"], "客户问：产品怎么使用？\n销售答：先登录后台，再创建知识库。")


if __name__ == "__main__":
    unittest.main()
