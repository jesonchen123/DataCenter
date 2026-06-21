import unittest

from app.domain.enums import RiskLevel
from app.services.price_filter_service import (
    contains_original_price,
    detect_price_info,
    filter_price_content,
)


class PriceFilterServiceTest(unittest.TestCase):
    def test_detects_explicit_amount_as_high_risk_original_price(self):
        result = detect_price_info("销售：基础版 999 元，高级版 2999 元。")

        self.assertTrue(result.contains_price_info)
        self.assertTrue(result.contains_original_price)
        self.assertEqual(result.risk_level, RiskLevel.HIGH.value)

    def test_detects_discount_preferential_price_contract_payment_rebate_and_commission(self):
        examples = [
            "给你打八折。",
            "今天优惠价 399。",
            "合同总价 5 万。",
            "可以先付 30% 定金。",
            "月结 30 天。",
            "返点 10%。",
            "佣金 5%。",
        ]

        for text in examples:
            with self.subTest(text=text):
                result = detect_price_info(text)
                self.assertTrue(result.contains_price_info)
                self.assertTrue(result.contains_original_price)
                self.assertEqual(result.risk_level, RiskLevel.HIGH.value)

    def test_detects_customer_price_intent_as_medium_risk_without_original_price(self):
        result = detect_price_info("客户：这个产品多少钱？有没有优惠？")

        self.assertTrue(result.contains_price_info)
        self.assertTrue(result.contains_price_intent)
        self.assertFalse(result.contains_original_price)
        self.assertEqual(result.risk_level, RiskLevel.MEDIUM.value)

    def test_filters_price_sentences_and_keeps_standard_price_guidance(self):
        result = filter_price_content(
            "客户：这个产品多少钱？销售：基础版 999 元，高级版 2999 元。"
            "产品支持企业内部知识库问答。"
        )

        self.assertNotIn("999", result.filtered_text)
        self.assertNotIn("2999", result.filtered_text)
        self.assertIn("具体价格以公司正式报价为准", result.filtered_text)
        self.assertIn("产品支持企业内部知识库问答", result.filtered_text)
        self.assertTrue(result.contains_price_intent)
        self.assertTrue(result.contains_original_price)
        self.assertEqual(result.risk_level, RiskLevel.HIGH.value)

    def test_contains_original_price_rejects_export_unsafe_text(self):
        self.assertTrue(contains_original_price("合同总价 5 万，月结 30 天。"))
        self.assertFalse(contains_original_price("具体价格以公司正式报价为准。"))


if __name__ == "__main__":
    unittest.main()
