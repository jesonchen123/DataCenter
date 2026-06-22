import unittest

from app.services.llm_validation_service import extract_json_object, validate_llm_knowledge_doc


class LLMValidationServiceTest(unittest.TestCase):
    def test_extract_json_object_accepts_markdown_code_fence(self):
        text = """```json
{"title":"客户咨询流程","content":"先确认需求。","question_examples":["怎么使用？"],"tags":["产品咨询"],"risk_level":"low","need_human_review":false}
```"""

        result = extract_json_object(text)

        self.assertEqual(result["title"], "客户咨询流程")

    def test_validate_llm_knowledge_doc_normalizes_safe_output(self):
        segment = {
            "segment_no": "seg_001",
            "business_line": "默认业务线",
            "product_name": "默认产品",
            "contains_price_info": False,
            "price_risk_level": "none",
        }
        output = {
            "title": "客户咨询功能",
            "content": "客服应先确认客户的使用场景，并说明产品能力。",
            "question_examples": ["这个功能怎么用？"],
            "tags": ["产品咨询"],
            "risk_level": "low",
            "need_human_review": False,
        }

        doc = validate_llm_knowledge_doc(output, segment)

        self.assertEqual(doc["doc_no"], "kb_seg_001")
        self.assertEqual(doc["title"], "客户咨询功能")
        self.assertTrue(doc["price_filtered"])
        self.assertFalse(doc["contains_original_price"])
        self.assertTrue(doc["is_desensitized"])

    def test_validate_llm_knowledge_doc_rejects_missing_required_fields(self):
        with self.assertRaises(ValueError):
            validate_llm_knowledge_doc({"title": "缺少正文"}, {"segment_no": "seg_001"})

    def test_validate_llm_knowledge_doc_rejects_original_price(self):
        output = {
            "title": "价格说明",
            "content": "这个套餐报价是 9800 元。",
            "question_examples": ["多少钱？"],
            "tags": ["价格咨询"],
            "risk_level": "high",
            "need_human_review": True,
        }

        with self.assertRaises(ValueError):
            validate_llm_knowledge_doc(output, {"segment_no": "seg_001", "contains_price_info": True})

    def test_validate_llm_knowledge_doc_rejects_sensitive_info(self):
        output = {
            "title": "联系方式",
            "content": "客户手机号是 13812345678。",
            "question_examples": ["怎么联系？"],
            "tags": ["售后"],
            "risk_level": "low",
            "need_human_review": True,
        }

        with self.assertRaises(ValueError):
            validate_llm_knowledge_doc(output, {"segment_no": "seg_001"})


if __name__ == "__main__":
    unittest.main()
