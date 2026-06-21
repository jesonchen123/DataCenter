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


if __name__ == "__main__":
    unittest.main()
