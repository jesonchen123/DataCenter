import unittest

from app.domain.enums import ReviewStatus, RiskLevel, Role
from app.services.export_service import build_export_content, build_qa_export_content, validate_exportable


def approved_doc(**overrides):
    doc = {
        "doc_no": "kb_001",
        "title": "产品使用流程",
        "content": "先登录后台再创建知识库。",
        "question_examples": ["产品怎么使用？"],
        "tags": ["产品咨询"],
        "business_line": "默认业务线",
        "product_name": "默认产品",
        "review_status": ReviewStatus.APPROVED.value,
        "risk_level": RiskLevel.LOW.value,
        "price_filtered": True,
        "contains_price_intent": False,
        "contains_original_price": False,
        "is_desensitized": True,
        "reviewer_role": Role.MANAGER.value,
    }
    doc.update(overrides)
    return doc


class ExportServiceTest(unittest.TestCase):
    def test_manager_can_export_approved_safe_doc(self):
        validate_exportable(approved_doc(), Role.MANAGER.value)

    def test_rejects_normal_user_export(self):
        with self.assertRaisesRegex(PermissionError, "Only managers"):
            validate_exportable(approved_doc(), Role.NORMAL_USER.value)

    def test_rejects_unapproved_unsafe_or_unfiltered_docs(self):
        invalid_docs = [
            approved_doc(review_status=ReviewStatus.PENDING_REVIEW.value),
            approved_doc(is_desensitized=False),
            approved_doc(price_filtered=False),
            approved_doc(contains_original_price=True),
            approved_doc(content="套餐 999 元", contains_original_price=False),
        ]

        for doc in invalid_docs:
            with self.subTest(doc=doc):
                with self.assertRaises(ValueError):
                    validate_exportable(doc, Role.MANAGER.value)

    def test_rejects_high_risk_doc_without_manager_reviewer(self):
        doc = approved_doc(risk_level=RiskLevel.HIGH.value, reviewer_role=Role.NORMAL_USER.value)

        with self.assertRaisesRegex(ValueError, "High-risk"):
            validate_exportable(doc, Role.MANAGER.value)

    def test_build_export_content_contains_required_security_fields(self):
        content = build_export_content([approved_doc()], created_by="manager")

        exported_doc = content["documents"][0]
        self.assertEqual(content["export_type"], "rag_knowledge_base")
        self.assertTrue(exported_doc["security"]["price_filtered"])
        self.assertFalse(exported_doc["security"]["contains_original_price"])

    def test_build_qa_export_content_returns_only_document_content(self):
        export_content = build_export_content(
            [
                approved_doc(
                    content="客户问：产品怎么使用？\n销售答：先登录后台再创建知识库。",
                )
            ],
            created_by="manager",
        )

        result = build_qa_export_content(export_content)

        self.assertEqual(
            result,
            {
                "documents": [
                    {
                        "content": "客户问：产品怎么使用？\n销售答：先登录后台再创建知识库。",
                    }
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
