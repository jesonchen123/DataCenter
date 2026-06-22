from app.api.deps import CurrentUser, get_current_user
from app.schemas import KnowledgeDocUpdateRequest, ReviewRequest

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    from app.db.session import get_db
    from app.models.knowledge_doc import KnowledgeDoc
    from app.services.db_serializers import serialize_knowledge_doc
    from app.services.review_service import (
        apply_doc_update,
        apply_review,
        get_knowledge_doc_or_404,
        submit_for_review,
    )
    from app.services.task_service import resolve_user_id

    router = APIRouter(prefix="/knowledge-docs", tags=["knowledge-docs"])

    @router.get("")
    def list_knowledge_docs(
        _current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> list[dict]:
        docs = db.query(KnowledgeDoc).order_by(KnowledgeDoc.created_at.desc()).all()
        return [serialize_knowledge_doc(doc) for doc in docs]

    @router.patch("/{knowledge_doc_id}")
    def update_knowledge_doc(
        knowledge_doc_id: str,
        payload: KnowledgeDocUpdateRequest,
        current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        doc = get_knowledge_doc_or_404(db, knowledge_doc_id)
        user_id = resolve_user_id(db, current_user.id or current_user.username)
        apply_doc_update(doc, payload.model_dump(exclude_none=True), user_id)
        db.commit()
        db.refresh(doc)
        return serialize_knowledge_doc(doc)

    @router.post("/{knowledge_doc_id}/submit-review")
    def submit_review(
        knowledge_doc_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        doc = get_knowledge_doc_or_404(db, knowledge_doc_id)
        user_id = resolve_user_id(db, current_user.id or current_user.username)
        submit_for_review(doc, user_id)
        db.commit()
        db.refresh(doc)
        return serialize_knowledge_doc(doc)

    @router.post("/{knowledge_doc_id}/review")
    def review_knowledge_doc(
        knowledge_doc_id: str,
        payload: ReviewRequest,
        current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        doc = get_knowledge_doc_or_404(db, knowledge_doc_id)
        reviewer_id = resolve_user_id(db, current_user.id or current_user.username)
        try:
            apply_review(doc, payload.approved, payload.review_comment, reviewer_id, current_user.role)
        except PermissionError:
            raise HTTPException(status_code=403, detail="Only managers can review knowledge docs")
        db.commit()
        db.refresh(doc)
        return serialize_knowledge_doc(doc)
