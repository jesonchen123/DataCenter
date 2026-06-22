import unittest

from app.services.llm_prompt_service import build_knowledge_generation_messages


class LLMPromptServiceTest(unittest.TestCase):
    def test_prompt_uses_customer_staff_qa_and_excludes_original_content(self):
        segment = {
            "original_content": "客户问价格，销售报价 9800 元。",
            "price_filtered_content": "客户咨询价格。价格信息已过滤，具体价格以公司正式报价为准",
            "customer_question": "这个产品多少钱？",
            "staff_answer": "基础版 9800 元。",
            "business_line": "默认业务线",
            "product_name": "默认产品",
            "contains_price_info": True,
            "price_risk_level": "high",
        }

        messages = build_knowledge_generation_messages(segment)
        prompt_text = "\n".join(message["content"] for message in messages)

        self.assertIn("customer_question", prompt_text)
        self.assertIn("staff_answer", prompt_text)
        self.assertIn("具体价格以公司正式报价为准", prompt_text)
        self.assertNotIn("price_filtered_content", prompt_text)
        self.assertNotIn("9800", prompt_text)
        self.assertNotIn("销售报价 9800 元", prompt_text)


if __name__ == "__main__":
    unittest.main()
