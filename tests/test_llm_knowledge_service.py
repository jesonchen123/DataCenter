import unittest

from app.core.config import Settings
from app.services.llm_client_service import LLMChatResult, LLMClientError
from app.services.llm_knowledge_service import generate_knowledge_doc_with_llm


class FakeDB:
    def __init__(self):
        self.records = []
        self.flush_count = 0

    def add(self, record):
        self.records.append(record)

    def flush(self):
        self.flush_count += 1


class SuccessfulClient:
    settings = Settings(llm_model_name="model_001")

    def chat(self, messages, response_format=None):
        return LLMChatResult(
            content=(
                '{"title":"客户咨询功能","content":"客服应先确认客户使用场景，并说明产品能力。",'
                '"question_examples":["这个功能怎么使用？"],"tags":["产品咨询"],'
                '"risk_level":"low","need_human_review":false}'
            ),
            request_payload={"messages": messages, "response_format": response_format},
            response_payload={"id": "chatcmpl_success"},
            latency_ms=15,
        )


class FailingClient:
    settings = Settings(llm_model_name="model_001")

    def chat(self, messages, response_format=None):
        raise LLMClientError("timeout")


class UnsafeClient:
    settings = Settings(llm_model_name="model_001")

    def chat(self, messages, response_format=None):
        return LLMChatResult(
            content=(
                '{"title":"价格","content":"套餐报价 9800 元。",'
                '"question_examples":["多少钱？"],"tags":["价格咨询"],'
                '"risk_level":"high","need_human_review":true}'
            ),
            request_payload={"messages": messages, "response_format": response_format},
            response_payload={"id": "chatcmpl_unsafe"},
            latency_ms=9,
        )


class LLMKnowledgeServiceTest(unittest.TestCase):
    def test_generate_knowledge_doc_with_llm_returns_validated_doc(self):
        doc = generate_knowledge_doc_with_llm(_segment(), client=SuccessfulClient())

        self.assertEqual(doc["title"], "客户咨询功能")
        self.assertFalse(doc["contains_original_price"])
        self.assertTrue(doc["price_filtered"])

    def test_generate_knowledge_doc_with_llm_writes_success_log(self):
        db = FakeDB()

        generate_knowledge_doc_with_llm(
            _segment(),
            db=db,
            related_type="process_task",
            related_id="00000000-0000-0000-0000-000000000001",
            client=SuccessfulClient(),
        )

        self.assertEqual(db.records[0].status, "success")
        self.assertEqual(db.records[0].model_name, "model_001")
        self.assertEqual(db.records[0].parsed_output["title"], "客户咨询功能")
        self.assertEqual(db.flush_count, 1)

    def test_generate_knowledge_doc_with_llm_falls_back_and_logs_failure_on_client_error(self):
        db = FakeDB()

        doc = generate_knowledge_doc_with_llm(_segment(), db=db, client=FailingClient())

        self.assertEqual(doc["doc_no"], "kb_seg_001")
        self.assertEqual(db.records[0].status, "failed")
        self.assertIn("timeout", db.records[0].error_message)

    def test_generate_knowledge_doc_with_llm_falls_back_when_output_is_unsafe(self):
        db = FakeDB()

        doc = generate_knowledge_doc_with_llm(_segment(), db=db, client=UnsafeClient())

        self.assertEqual(doc["doc_no"], "kb_seg_001")
        self.assertEqual(db.records[0].status, "failed")
        self.assertIn("original price", db.records[0].error_message)


def _segment():
    return {
        "segment_no": "seg_001",
        "price_filtered_content": "客户咨询功能使用方法。",
        "customer_question": "这个功能怎么使用？",
        "business_line": "默认业务线",
        "product_name": "默认产品",
        "contains_price_info": False,
        "price_risk_level": "none",
        "staff_answer": "可以先确认使用场景。",
    }


if __name__ == "__main__":
    unittest.main()
