from app.domain.enums import PriceFilterStatus
from app.services.cleaning_service import clean_messages
from app.services.desensitization_service import desensitize_text
from app.services.knowledge_service import generate_knowledge_doc
from app.services.price_filter_service import filter_price_content
from app.services.segmentation_service import segment_dialogue


def process_mock_chat_payload(payload: dict, knowledge_generator=None) -> dict:
    generator = knowledge_generator or generate_knowledge_doc
    messages = clean_messages(payload.get("messages", []))
    original_content = _join_messages(messages, "content")

    # Segment into independent Q&A pairs (LLM or rule-based)
    qa_pairs, segmentation_strategy = segment_dialogue(messages)

    segments = []
    knowledge_docs = []

    for idx, qa in enumerate(qa_pairs, start=1):
        customer_question = qa.customer_question
        staff_answer = qa.staff_answer
        cleaned_content = _qa_content(customer_question, staff_answer)
        desensitized_content, contains_sensitive = desensitize_text(cleaned_content)
        price_result = filter_price_content(desensitized_content)

        segment = {
            "segment_no": f"seg_{payload.get('mock_chat_id', 'mock')}_{idx:03d}",
            "mock_chat_id": payload.get("mock_chat_id"),
            "original_content": original_content,
            "cleaned_content": cleaned_content,
            "desensitized_content": desensitized_content,
            "price_filtered_content": price_result.filtered_text,
            "customer_question": customer_question,
            "staff_answer": staff_answer,
            "business_line": payload.get("business_line"),
            "product_name": payload.get("product_name"),
            "scenario_type": qa.scenario_type,
            "tags": _segment_tags(qa.scenario_type),
            "contains_sensitive_info": contains_sensitive,
            "contains_price_info": price_result.contains_price_info,
            "price_filter_status": PriceFilterStatus.SUCCESS.value,
            "price_risk_level": price_result.risk_level,
            "status": "generated",
        }
        knowledge_doc = generator(segment)
        segments.append(segment)
        knowledge_docs.append(knowledge_doc)

    return {
        "mock_chat_id": payload.get("mock_chat_id"),
        "status": "success",
        "steps": [
            "parse",
            "clean",
            "segment",
            "desensitize",
            "price_filter",
            "generate_knowledge",
        ],
        "segments": segments,
        "knowledge_docs": knowledge_docs,
        "segmentation_strategy": segmentation_strategy,
    }


def _segment_tags(scenario_type: str) -> list[str]:
    tags = ["auto_segmented"]
    if scenario_type and scenario_type != "other":
        tags.append(scenario_type)
    return tags


def _join_messages(messages: list[dict], field: str) -> str:
    return "。".join(str(message.get(field) or "").strip("。") for message in messages if message.get(field))


def _qa_content(customer_question: str, staff_answer: str) -> str:
    parts = []
    if customer_question:
        parts.append(f"客户问：{customer_question}")
    if staff_answer:
        parts.append(f"销售答：{staff_answer}")
    return "\n".join(parts)
