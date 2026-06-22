import json
import unittest
from unittest.mock import patch

from app.services.document_import_service import (
    build_document_chat_values,
    extract_text,
    normalize_messages,
    validate_message_array,
)


class DocumentImportServiceTest(unittest.TestCase):
    # ── extract_text ──────────────────────────────────────────────

    def test_extract_text_from_json_file(self):
        content = json.dumps(
            [{"role": "customer", "text": "你好"}], ensure_ascii=False
        ).encode("utf-8")
        text = extract_text(content, "chat.json")
        parsed = json.loads(text)
        self.assertEqual(parsed[0]["role"], "customer")

    def test_extract_text_from_txt_file(self):
        content = "客户：你好\n销售：你好，请问有什么可以帮助您？".encode("utf-8")
        text = extract_text(content, "chat.txt")
        self.assertIn("客户：你好", text)

    def test_extract_text_rejects_unsupported_format(self):
        with self.assertRaises(ValueError):
            extract_text(b"dummy", "chat.pdf")

    def test_extract_text_from_empty_txt(self):
        text = extract_text(b"  \n  ", "chat.txt")
        self.assertEqual(text, "")

    # ── normalize_messages: JSON direct ───────────────────────────

    def test_normalize_json_array_direct(self):
        raw = json.dumps(
            [
                {"role": "customer", "text": "这个产品怎么使用？", "sender": "客户A"},
                {"role": "staff", "text": "先确认使用场景。", "sender": "销售B"},
            ],
            ensure_ascii=False,
        )
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "json_direct")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "customer")
        self.assertEqual(messages[0]["text"], "这个产品怎么使用？")
        self.assertEqual(messages[0]["sender"], "客户A")

    def test_normalize_json_object_with_messages_key(self):
        raw = json.dumps(
            {
                "messages": [
                    {"role": "customer", "text": "你好"},
                    {"role": "staff", "text": "你好"},
                ]
            },
            ensure_ascii=False,
        )
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "json_direct")
        self.assertEqual(len(messages), 2)

    def test_normalize_json_direct_rejects_invalid_role(self):
        raw = json.dumps(
            [{"role": "admin", "text": "hello"}], ensure_ascii=False
        )
        with self.assertRaises(ValueError):
            normalize_messages(raw)

    def test_normalize_json_direct_rejects_legacy_fields(self):
        raw = json.dumps(
            [
                {
                    "message_id": "msg_001",
                    "sender_role": "customer",
                    "content": "旧格式",
                }
            ],
            ensure_ascii=False,
        )
        # JSON direct will try to validate but the legacy fields won't match
        # It will have role missing → ValueError
        with self.assertRaises(ValueError):
            normalize_messages(raw)

    # ── normalize_messages: rule fallback ─────────────────────────

    @patch("app.services.document_import_service._is_llm_available", return_value=False)
    def test_normalize_rules_basic_chinese_prefix(self, _mock):
        raw = (
            "客户：这个产品怎么使用？\n"
            "销售：可以先确认使用场景，然后说明产品能力。\n"
            "客户：有什么优惠吗？\n"
            "销售：具体价格以公司正式报价为准。"
        )
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "rule")
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0]["role"], "customer")
        self.assertEqual(messages[0]["text"], "这个产品怎么使用？")
        self.assertEqual(messages[0]["sender"], "客户")
        self.assertEqual(messages[1]["role"], "staff")
        self.assertEqual(messages[3]["text"], "具体价格以公司正式报价为准。")

    @patch("app.services.document_import_service._is_llm_available", return_value=False)
    def test_normalize_rules_timestamped_chat_log(self, _mock):
        raw = (
            "[2026-01-05 09:10] 客户（客户A001）：你好，我想了解一下\n"
            "[2026-01-05 09:11] 销售（销售S001）：您好。这个系统主要用于自动回答\n"
            "[2026-01-05 09:12] 客户（客户A001）：它可以接入我们现有的网站客服入口吗？\n"
            "[2026-01-05 09:13] 销售（销售S001）：可以。系统支持通过接口接入。"
        )
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "rule")
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0]["role"], "customer")
        self.assertEqual(messages[0]["sender"], "客户A001")
        self.assertEqual(messages[0]["text"], "你好，我想了解一下")
        self.assertEqual(messages[1]["role"], "staff")
        self.assertEqual(messages[1]["sender"], "销售S001")
        self.assertEqual(messages[1]["text"], "您好。这个系统主要用于自动回答")
        self.assertEqual(messages[2]["text"], "它可以接入我们现有的网站客服入口吗？")
        self.assertEqual(messages[3]["text"], "可以。系统支持通过接口接入。")

    @patch("app.services.document_import_service._is_llm_available", return_value=False)
    def test_normalize_rules_timestamped_skips_metadata_lines(self, _mock):
        raw = (
            "客服会话记录\n"
            "导出时间：2026-01-05\n"
            "\n"
            "[2026-01-05 09:10] 客户（客户A001）：你好\n"
            "[2026-01-05 09:11] 销售（销售S001）：您好\n"
            "\n"
            "--- 会话结束 ---"
        )
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "rule")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["text"], "你好")
        self.assertEqual(messages[1]["text"], "您好")

    @patch("app.services.document_import_service._is_llm_available", return_value=False)
    def test_normalize_rules_multi_line_message(self, _mock):
        raw = (
            "客户：这个产品怎么使用？\n"
            "我想了解一下具体的操作流程。\n"
            "销售：可以先确认使用场景。\n"
            "然后我们会安排专人对接。"
        )
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "rule")
        self.assertEqual(len(messages), 2)
        self.assertIn("具体的操作流程", messages[0]["text"])

    @patch("app.services.document_import_service._is_llm_available", return_value=False)
    def test_normalize_rules_english_prefix(self, _mock):
        raw = "customer: How to use this?\nstaff: Let me show you."
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "rule")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "customer")
        self.assertEqual(messages[1]["role"], "staff")

    @patch("app.services.document_import_service._is_llm_available", return_value=False)
    def test_normalize_rules_no_recognizable_messages(self, _mock):
        raw = "这是一段没有任何角色前缀的文本。\n它只是普通的段落。"
        with self.assertRaises(ValueError):
            normalize_messages(raw)

    @patch("app.services.document_import_service._is_llm_available", return_value=False)
    def test_normalize_rules_skips_empty_roles(self, _mock):
        raw = "客户：\n销售：有效回复。"
        messages, normalizer = normalize_messages(raw)
        self.assertEqual(normalizer, "rule")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["text"], "有效回复。")

    # ── normalize_messages: empty input ───────────────────────────

    def test_normalize_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            normalize_messages("   ")

    # ── validate_message_array ────────────────────────────────────

    def test_validate_accepts_minimal_messages(self):
        result = validate_message_array(
            [{"role": "customer", "text": "你好"}]
        )
        self.assertEqual(len(result), 1)

    def test_validate_rejects_non_list(self):
        with self.assertRaises(ValueError):
            validate_message_array({"role": "customer"})

    def test_validate_rejects_empty_list(self):
        with self.assertRaises(ValueError):
            validate_message_array([])

    def test_validate_rejects_missing_role(self):
        with self.assertRaises(ValueError):
            validate_message_array([{"text": "hello"}])

    def test_validate_rejects_invalid_role(self):
        with self.assertRaises(ValueError):
            validate_message_array([{"role": "admin", "text": "hello"}])

    def test_validate_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            validate_message_array([{"role": "customer", "text": ""}])

    def test_validate_rejects_unexpected_fields(self):
        with self.assertRaises(ValueError):
            validate_message_array(
                [{"role": "customer", "text": "hi", "message_id": "x"}]
            )

    # ── build_document_chat_values ────────────────────────────────

    def test_build_converts_simplified_to_internal_format(self):
        messages = [
            {"role": "customer", "text": "这个产品多少钱？", "sender": "客户A"},
            {"role": "staff", "text": "具体价格以报价为准。"},
        ]
        metadata = {
            "mock_chat_id": "imp_001",
            "business_line": "测试线",
            "product_name": "测试产品",
            "scenario_type": "price_consulting",
        }
        values = build_document_chat_values(messages, metadata)

        self.assertEqual(values["mock_chat_id"], "imp_001")
        self.assertEqual(values["source_platform"], "document_import")
        self.assertEqual(values["business_line"], "测试线")
        self.assertEqual(values["raw_content"]["messages"][0]["message_id"], "imp_001_msg_001")
        self.assertEqual(values["raw_content"]["messages"][0]["sender_role"], "customer")
        self.assertEqual(values["raw_content"]["messages"][0]["sender_name"], "客户A")
        self.assertEqual(values["raw_content"]["messages"][0]["content"], "这个产品多少钱？")
        self.assertEqual(values["raw_content"]["messages"][1]["sender_name"], "员工")

    def test_build_uses_default_metadata(self):
        messages = [{"role": "customer", "text": "hello"}]
        values = build_document_chat_values(messages)
        self.assertEqual(values["source_platform"], "document_import")
        self.assertEqual(values["raw_content"]["messages"][0]["message_id"], "_msg_001")


if __name__ == "__main__":
    unittest.main()
