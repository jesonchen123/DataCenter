import unittest

from app.domain.enums import RiskLevel
from app.services.knowledge_service import generate_knowledge_doc


class KnowledgeServiceTest(unittest.TestCase):
    def test_generates_price_intent_doc_without_original_price(self):
        segment = {
            "segment_no": "seg_001",
            "price_filtered_content": "客户：这个产品多少钱？价格信息已过滤，具体价格以公司正式报价为准",
            "customer_question": "这个产品多少钱？",
            "business_line": "默认业务线",
            "product_name": "默认产品",
            "contains_price_info": True,
            "price_risk_level": RiskLevel.MEDIUM.value,
        }

        doc = generate_knowledge_doc(segment)

        self.assertEqual(doc["title"], "客户咨询价格时的标准回复")
        self.assertIn("具体价格以公司正式报价为准", doc["content"])
        self.assertTrue(doc["price_filtered"])
        self.assertTrue(doc["contains_price_intent"])
        self.assertFalse(doc["contains_original_price"])
        self.assertTrue(doc["need_human_review"])

    def test_generates_non_price_business_doc(self):
        segment = {
            "segment_no": "seg_002",
            "price_filtered_content": "客户咨询产品使用流程。客服说明先登录后台再创建知识库。",
            "customer_question": "产品怎么使用？",
            "staff_answer": "先登录后台再创建知识库。",
            "business_line": "默认业务线",
            "product_name": "默认产品",
            "contains_price_info": False,
            "price_risk_level": RiskLevel.LOW.value,
        }

        doc = generate_knowledge_doc(segment)

        self.assertEqual(doc["title"], "产品怎么使用？")
        self.assertIn("先登录后台再创建知识库", doc["content"])
        self.assertFalse(doc["contains_price_intent"])
        self.assertEqual(doc["risk_level"], RiskLevel.LOW.value)


if __name__ == "__main__":
    unittest.main()
