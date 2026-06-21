from datetime import UTC, datetime
from uuid import uuid4

from app.core.permissions import can_export
from app.domain.enums import ReviewStatus, RiskLevel, Role
from app.services.price_filter_service import contains_original_price


def validate_exportable(doc: dict, requester_role: str) -> None:
    if not can_export(requester_role):
        raise PermissionError("Only managers can export knowledge documents.")
    if doc.get("review_status") != ReviewStatus.APPROVED.value:
        raise ValueError("Only approved knowledge documents can be exported.")
    if not doc.get("is_desensitized"):
        raise ValueError("Knowledge document must be desensitized before export.")
    if not doc.get("price_filtered"):
        raise ValueError("Knowledge document must be price filtered before export.")
    if doc.get("contains_original_price") or contains_original_price(str(doc.get("content") or "")):
        raise ValueError("Knowledge document contains original price information.")
    if (
        doc.get("risk_level") == RiskLevel.HIGH.value
        and doc.get("reviewer_role") != Role.MANAGER.value
    ):
        raise ValueError("High-risk knowledge documents must be reviewed by a manager.")


def build_export_content(docs: list[dict], created_by: str) -> dict:
    for doc in docs:
        validate_exportable(doc, Role.MANAGER.value)

    return {
        "export_id": f"export_{uuid4().hex}",
        "export_type": "rag_knowledge_base",
        "version": "v1",
        "created_at": datetime.now(UTC).isoformat(),
        "created_by": created_by,
        "filters": {
            "review_status": ReviewStatus.APPROVED.value,
            "price_filtered": True,
            "contains_original_price": False,
        },
        "documents": [_serialize_doc(doc) for doc in docs],
    }


def _serialize_doc(doc: dict) -> dict:
    return {
        "doc_id": doc.get("doc_no"),
        "title": doc.get("title"),
        "content": doc.get("content"),
        "question_examples": doc.get("question_examples", []),
        "tags": doc.get("tags", []),
        "business_line": doc.get("business_line"),
        "product_name": doc.get("product_name"),
        "security": {
            "is_desensitized": bool(doc.get("is_desensitized")),
            "price_filtered": bool(doc.get("price_filtered")),
            "contains_price_intent": bool(doc.get("contains_price_intent")),
            "contains_original_price": bool(doc.get("contains_original_price")),
        },
        "metadata": {
            "language": "zh-CN",
            "review_status": doc.get("review_status"),
            "risk_level": doc.get("risk_level"),
            "quality_score": doc.get("quality_score", 0),
        },
    }
