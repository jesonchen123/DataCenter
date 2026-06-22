import unittest
from types import SimpleNamespace
from uuid import UUID

from app.domain.enums import ReviewStatus, Role
from app.services.review_service import apply_doc_update, apply_review, submit_for_review


class ReviewServiceTest(unittest.TestCase):
    def test_apply_doc_update_changes_allowed_fields_and_updated_by(self):
        doc = SimpleNamespace(title="旧标题", content="旧内容", question_examples=[], tags=[], updated_by=None)
        user_id = UUID("00000000-0000-0000-0000-000000000001")

        apply_doc_update(
            doc,
            {"title": "新标题", "content": "新内容", "tags": ["产品咨询"]},
            user_id,
        )

        self.assertEqual(doc.title, "新标题")
        self.assertEqual(doc.content, "新内容")
        self.assertEqual(doc.tags, ["产品咨询"])
        self.assertEqual(doc.updated_by, user_id)

    def test_submit_for_review_sets_pending_review(self):
        doc = SimpleNamespace(review_status=ReviewStatus.NEED_EDIT.value, updated_by=None)
        user_id = UUID("00000000-0000-0000-0000-000000000001")

        submit_for_review(doc, user_id)

        self.assertEqual(doc.review_status, ReviewStatus.PENDING_REVIEW.value)
        self.assertEqual(doc.updated_by, user_id)

    def test_apply_review_requires_manager(self):
        doc = SimpleNamespace(review_status=ReviewStatus.PENDING_REVIEW.value)

        with self.assertRaises(PermissionError):
            apply_review(doc, approved=True, comment=None, reviewer_id=None, reviewer_role=Role.NORMAL_USER.value)

    def test_apply_review_approves_or_rejects_with_reviewer_metadata(self):
        doc = SimpleNamespace(review_status=ReviewStatus.PENDING_REVIEW.value, review_comment=None, reviewer_id=None)
        reviewer_id = UUID("00000000-0000-0000-0000-000000000002")

        apply_review(doc, approved=True, comment="通过", reviewer_id=reviewer_id, reviewer_role=Role.MANAGER.value)

        self.assertEqual(doc.review_status, ReviewStatus.APPROVED.value)
        self.assertEqual(doc.review_comment, "通过")
        self.assertEqual(doc.reviewer_id, reviewer_id)


if __name__ == "__main__":
    unittest.main()
