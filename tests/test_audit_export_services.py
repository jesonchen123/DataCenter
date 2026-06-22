import unittest
from types import SimpleNamespace
from uuid import UUID

from app.domain.enums import ReviewStatus, RiskLevel, Role
from app.services.audit_service import build_audit_log_values
from app.services.export_service import build_export_task_values


class AuditExportServicesTest(unittest.TestCase):
    def test_build_audit_log_values_records_actor_action_and_detail(self):
        user_id = UUID("00000000-0000-0000-0000-000000000001")

        values = build_audit_log_values(
            user_id=user_id,
            action="export_create",
            target_type="export_task",
            target_id="export_001",
            detail={"document_count": 1},
        )

        self.assertEqual(values["user_id"], user_id)
        self.assertEqual(values["action"], "export_create")
        self.assertEqual(values["detail"]["document_count"], 1)

    def test_build_export_task_values_contains_export_content_and_security_fields(self):
        user_id = UUID("00000000-0000-0000-0000-000000000001")
        doc = SimpleNamespace(
            doc_no="kb_001",
            title="产品使用流程",
            content="先登录后台。",
            question_examples=["怎么使用？"],
            tags=["产品咨询"],
            business_line="默认业务线",
            product_name="默认产品",
            review_status=ReviewStatus.APPROVED.value,
            risk_level=RiskLevel.LOW.value,
            quality_score=28,
            price_filtered=True,
            contains_price_intent=False,
            contains_original_price=False,
            is_desensitized=True,
            reviewer_id=user_id,
        )

        values = build_export_task_values([doc], created_by=user_id)

        self.assertEqual(values["export_type"], "rag_knowledge_base")
        self.assertEqual(values["document_count"], 1)
        self.assertEqual(values["status"], "success")
        exported_doc = values["export_content"]["documents"][0]
        self.assertTrue(exported_doc["security"]["price_filtered"])
        self.assertFalse(exported_doc["security"]["contains_original_price"])


if __name__ == "__main__":
    unittest.main()
