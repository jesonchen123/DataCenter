from app.domain.enums import PriceFilterStatus
from app.services.cleaning_service import clean_messages
from app.services.desensitization_service import desensitize_text
from app.services.knowledge_service import generate_knowledge_doc
from app.services.price_filter_service import filter_price_content


def process_mock_chat_payload(payload: dict, knowledge_generator=None) -> dict:
    generator = knowledge_generator or generate_knowledge_doc
    messages = clean_messages(payload.get("messages", []))
    original_content = _join_messages(messages, "content")
    desensitized_content, contains_sensitive = desensitize_text(original_content)
    price_result = filter_price_content(desensitized_content)

    segment = {
        "segment_no": f"seg_{payload.get('mock_chat_id', 'mock')}_001",
        "mock_chat_id": payload.get("mock_chat_id"),
        "original_content": original_content,
        "cleaned_content": original_content,
        "desensitized_content": desensitized_content,
        "price_filtered_content": price_result.filtered_text,
        "customer_question": _first_by_role(messages, "customer"),
        "staff_answer": _first_by_role(messages, "staff"),
        "business_line": payload.get("business_line"),
        "product_name": payload.get("product_name"),
        "tags": ["mock", "auto_generated"],
        "contains_sensitive_info": contains_sensitive,
        "contains_price_info": price_result.contains_price_info,
        "price_filter_status": PriceFilterStatus.SUCCESS.value,
        "price_risk_level": price_result.risk_level,
        "status": "generated",
    }
    knowledge_doc = generator(segment)

    return {
        "mock_chat_id": payload.get("mock_chat_id"),
        "status": "success",
        "steps": [
            "parse",
            "clean",
            "desensitize",
            "price_filter",
            "segment",
            "generate_knowledge",
            "quality_score",
        ],
        "segments": [segment],
        "knowledge_docs": [knowledge_doc],
    }


def _join_messages(messages: list[dict], field: str) -> str:
    return "。".join(str(message.get(field) or "").strip("。") for message in messages if message.get(field))


def _first_by_role(messages: list[dict], role: str) -> str:
    for message in messages:
        if message.get("sender_role") == role:
            return str(message.get("content") or "")
    return ""
