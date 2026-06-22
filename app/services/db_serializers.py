from datetime import date, datetime
from uuid import UUID


def serialize_mock_chat(chat) -> dict:
    return {
        "id": _to_json(chat.id),
        "mock_chat_id": chat.mock_chat_id,
        "source_platform": chat.source_platform,
        "business_line": chat.business_line,
        "product_name": chat.product_name,
        "scenario_type": chat.scenario_type,
        "raw_content": chat.raw_content,
        "created_at": _to_json(chat.created_at),
        "updated_at": _to_json(chat.updated_at),
    }


def serialize_process_task(task) -> dict:
    return {
        "id": _to_json(task.id),
        "task_no": task.task_no,
        "mock_chat_id": _to_json(task.mock_chat_id),
        "triggered_by": _to_json(task.triggered_by),
        "status": task.status,
        "current_step": task.current_step,
        "progress": task.progress,
        "error_message": task.error_message,
        "retry_count": task.retry_count,
        "step_result": task.step_result,
        "created_at": _to_json(task.created_at),
        "updated_at": _to_json(task.updated_at),
        "completed_at": _to_json(task.completed_at),
    }


def serialize_dialogue_segment(segment) -> dict:
    return {
        "id": _to_json(segment.id),
        "segment_no": segment.segment_no,
        "process_task_id": _to_json(segment.process_task_id),
        "mock_chat_id": _to_json(segment.mock_chat_id),
        "original_content": segment.original_content,
        "cleaned_content": segment.cleaned_content,
        "desensitized_content": segment.desensitized_content,
        "price_filtered_content": segment.price_filtered_content,
        "customer_question": segment.customer_question,
        "staff_answer": segment.staff_answer,
        "business_line": segment.business_line,
        "product_name": segment.product_name,
        "tags": segment.tags,
        "contains_sensitive_info": segment.contains_sensitive_info,
        "contains_price_info": segment.contains_price_info,
        "price_filter_status": segment.price_filter_status,
        "price_risk_level": segment.price_risk_level,
        "status": segment.status,
        "created_at": _to_json(segment.created_at),
        "updated_at": _to_json(segment.updated_at),
    }


def serialize_knowledge_doc(doc) -> dict:
    return {
        "id": _to_json(doc.id),
        "doc_no": doc.doc_no,
        "dialogue_segment_id": _to_json(doc.dialogue_segment_id),
        "title": doc.title,
        "content": doc.content,
        "question_examples": doc.question_examples,
        "tags": doc.tags,
        "business_line": doc.business_line,
        "product_name": doc.product_name,
        "risk_level": doc.risk_level,
        "quality_score": doc.quality_score,
        "review_status": doc.review_status,
        "review_comment": doc.review_comment,
        "reviewer_id": _to_json(doc.reviewer_id),
        "reviewed_at": _to_json(doc.reviewed_at),
        "price_filtered": doc.price_filtered,
        "contains_price_intent": doc.contains_price_intent,
        "contains_original_price": doc.contains_original_price,
        "is_desensitized": doc.is_desensitized,
        "created_by": _to_json(doc.created_by),
        "updated_by": _to_json(doc.updated_by),
        "created_at": _to_json(doc.created_at),
        "updated_at": _to_json(doc.updated_at),
    }


def serialize_export_task(task) -> dict:
    return {
        "id": _to_json(task.id),
        "export_no": task.export_no,
        "export_type": task.export_type,
        "filters": task.filters,
        "export_content": task.export_content,
        "document_count": task.document_count,
        "created_by": _to_json(task.created_by),
        "status": task.status,
        "error_message": task.error_message,
        "created_at": _to_json(task.created_at),
        "completed_at": _to_json(task.completed_at),
    }


def serialize_audit_log(log) -> dict:
    return {
        "id": _to_json(log.id),
        "user_id": _to_json(log.user_id),
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "detail": log.detail,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "created_at": _to_json(log.created_at),
    }


def _to_json(value):
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    return value
