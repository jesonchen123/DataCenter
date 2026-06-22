import unittest
from unittest.mock import patch

from app.services.segmentation_service import (
    QAPair,
    _segment_via_rules,
    segment_dialogue,
)


class SegmentationServiceTest(unittest.TestCase):
    # ── Rule-based segmentation ─────────────────────────────────

    def test_segment_single_qa_pair(self):
        messages = [
            {"sender_role": "customer", "content": "这个产品怎么使用？"},
            {"sender_role": "staff", "content": "先登录后台再创建知识库。"},
        ]
        pairs = _segment_via_rules(messages)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0].customer_question, "这个产品怎么使用？")
        self.assertEqual(pairs[0].staff_answer, "先登录后台再创建知识库。")
        self.assertEqual(pairs[0].scenario_type, "other")

    def test_segment_multiple_qa_rounds(self):
        messages = [
            {"sender_role": "customer", "content": "这个产品怎么使用？"},
            {"sender_role": "staff", "content": "先登录后台再创建知识库。"},
            {"sender_role": "customer", "content": "支持API接入吗？"},
            {"sender_role": "staff", "content": "支持，提供REST API。"},
        ]
        pairs = _segment_via_rules(messages)
        self.assertEqual(len(pairs), 2)
        self.assertEqual(pairs[0].customer_question, "这个产品怎么使用？")
        self.assertEqual(pairs[0].staff_answer, "先登录后台再创建知识库。")
        self.assertEqual(pairs[1].customer_question, "支持API接入吗？")
        self.assertEqual(pairs[1].staff_answer, "支持，提供REST API。")

    def test_segment_merges_consecutive_same_role(self):
        messages = [
            {"sender_role": "customer", "content": "你好，我想了解一下AI客服系统"},
            {"sender_role": "customer", "content": "它主要能解决什么问题？"},
            {"sender_role": "staff", "content": "您好。这个系统主要用于自动回答客户常见问题。"},
            {"sender_role": "staff", "content": "也可以把人工客服历史问答整理成知识库。"},
        ]
        pairs = _segment_via_rules(messages)
        self.assertEqual(len(pairs), 1)
        self.assertIn("你好，我想了解一下AI客服系统", pairs[0].customer_question)
        self.assertIn("主要能解决什么问题", pairs[0].customer_question)
        self.assertIn("自动回答客户常见问题", pairs[0].staff_answer)
        self.assertIn("人工客服历史问答整理成知识库", pairs[0].staff_answer)

    def test_segment_skips_staff_first_messages(self):
        messages = [
            {"sender_role": "staff", "content": "欢迎光临"},
            {"sender_role": "customer", "content": "我想咨询一下"},
            {"sender_role": "staff", "content": "好的请说"},
        ]
        pairs = _segment_via_rules(messages)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0].customer_question, "我想咨询一下")
        self.assertEqual(pairs[0].staff_answer, "好的请说")

    def test_segment_skips_empty_content(self):
        messages = [
            {"sender_role": "customer", "content": ""},
            {"sender_role": "customer", "content": "有效问题"},
            {"sender_role": "staff", "content": "有效回答"},
        ]
        pairs = _segment_via_rules(messages)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0].customer_question, "有效问题")

    def test_segment_multiple_staff_after_one_customer(self):
        messages = [
            {"sender_role": "customer", "content": "怎么接入？"},
            {"sender_role": "staff", "content": "可以通过API接入。"},
            {"sender_role": "staff", "content": "也支持SDK。"},
            {"sender_role": "staff", "content": "还有网页插件。"},
            {"sender_role": "customer", "content": "价格多少？"},
            {"sender_role": "staff", "content": "具体价格以报价为准。"},
        ]
        pairs = _segment_via_rules(messages)
        self.assertEqual(len(pairs), 2)
        self.assertEqual(pairs[0].customer_question, "怎么接入？")
        self.assertIn("API接入", pairs[0].staff_answer)
        self.assertIn("SDK", pairs[0].staff_answer)
        self.assertIn("网页插件", pairs[0].staff_answer)
        self.assertEqual(pairs[1].customer_question, "价格多少？")
        self.assertEqual(pairs[1].staff_answer, "具体价格以报价为准。")

    def test_segment_raises_when_no_qa_found(self):
        messages = [
            {"sender_role": "staff", "content": "欢迎"},
            {"sender_role": "staff", "content": "请问有什么可以帮助您"},
        ]
        with self.assertRaises(ValueError):
            _segment_via_rules(messages)

    def test_segment_raises_on_empty_input(self):
        with self.assertRaises(ValueError):
            segment_dialogue([])

    # ── segment_dialogue dispatcher ──────────────────────────────

    @patch("app.services.segmentation_service._is_llm_available", return_value=False)
    def test_segment_dialogue_uses_rule_strategy_when_no_llm(self, _mock):
        messages = [
            {"sender_role": "customer", "content": "问题"},
            {"sender_role": "staff", "content": "回答"},
        ]
        pairs, strategy = segment_dialogue(messages)
        self.assertEqual(strategy, "rule")
        self.assertEqual(len(pairs), 1)

    # ── QAPair dataclass ─────────────────────────────────────────

    def test_qa_pair_defaults(self):
        pair = QAPair(customer_question="Q", staff_answer="A")
        self.assertEqual(pair.scenario_type, "other")

    def test_qa_pair_with_scenario(self):
        pair = QAPair(
            customer_question="Q",
            staff_answer="A",
            scenario_type="product_inquiry",
        )
        self.assertEqual(pair.scenario_type, "product_inquiry")


if __name__ == "__main__":
    unittest.main()
