from datetime import UTC, datetime
from uuid import UUID

from app.core.permissions import can_approve
from app.domain.enums import ReviewStatus


def apply_doc_update(doc, changes: dict, user_id) -> None:
    for field in ["title", "content", "question_examples", "tags", "scenario_type"]:
        if field in changes and changes[field] is not None:
            setattr(doc, field, changes[field])
    doc.updated_by = user_id


def submit_for_review(doc, user_id) -> None:
    doc.review_status = ReviewStatus.PENDING_REVIEW.value
    doc.updated_by = user_id


def apply_review(doc, approved: bool, comment: str | None, reviewer_id, reviewer_role: str, scenario_type: str | None = None) -> None:
    if not can_approve(reviewer_role):
        raise PermissionError("Only managers can review knowledge docs")
    doc.review_status = ReviewStatus.APPROVED.value if approved else ReviewStatus.REJECTED.value
    doc.review_comment = comment
    if scenario_type is not None and scenario_type.strip():
        doc.scenario_type = scenario_type.strip()
    doc.reviewer_id = reviewer_id
    doc.reviewed_at = datetime.now(UTC)
    doc.updated_by = reviewer_id


def get_knowledge_doc_or_404(db, knowledge_doc_id: str):
    from fastapi import HTTPException
    from app.models.knowledge_doc import KnowledgeDoc

    try:
        doc_id = UUID(str(knowledge_doc_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Knowledge document not found")

    doc = db.query(KnowledgeDoc).filter(KnowledgeDoc.id == doc_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Knowledge document not found")
    return doc
