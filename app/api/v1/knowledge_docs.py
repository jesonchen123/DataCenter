from app.api.deps import CurrentUser, get_current_user
from app.core.permissions import can_approve
from app.domain.enums import ReviewStatus
from app.schemas import KnowledgeDocUpdateRequest, ReviewRequest

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    router = APIRouter(prefix="/knowledge-docs", tags=["knowledge-docs"])

    @router.get("")
    def list_knowledge_docs(_current_user: CurrentUser = Depends(get_current_user)) -> list[dict]:
        return []

    @router.patch("/{knowledge_doc_id}")
    def update_knowledge_doc(
        knowledge_doc_id: str,
        payload: KnowledgeDocUpdateRequest,
        current_user: CurrentUser = Depends(get_current_user),
    ) -> dict:
        return {"id": knowledge_doc_id, "updated_by": current_user.id, "changes": payload.model_dump(exclude_none=True)}

    @router.post("/{knowledge_doc_id}/submit-review")
    def submit_review(knowledge_doc_id: str, current_user: CurrentUser = Depends(get_current_user)) -> dict:
        return {
            "id": knowledge_doc_id,
            "submitted_by": current_user.id,
            "review_status": ReviewStatus.PENDING_REVIEW.value,
        }

    @router.post("/{knowledge_doc_id}/review")
    def review_knowledge_doc(
        knowledge_doc_id: str,
        payload: ReviewRequest,
        current_user: CurrentUser = Depends(get_current_user),
    ) -> dict:
        if not can_approve(current_user.role):
            raise HTTPException(status_code=403, detail="Only managers can review knowledge docs")
        return {
            "id": knowledge_doc_id,
            "reviewer_id": current_user.id,
            "review_status": ReviewStatus.APPROVED.value if payload.approved else ReviewStatus.REJECTED.value,
            "review_comment": payload.review_comment,
        }
