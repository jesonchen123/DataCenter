import json
import re

from app.domain.enums import RiskLevel
from app.services.desensitization_service import desensitize_text
from app.services.price_filter_service import contains_original_price


_REQUIRED_FIELDS = {
    "title",
    "content",
    "question_examples",
    "tags",
    "risk_level",
    "need_human_review",
}
_RISK_ORDER = {
    RiskLevel.NONE.value: 0,
    RiskLevel.LOW.value: 1,
    RiskLevel.MEDIUM.value: 2,
    RiskLevel.HIGH.value: 3,
}


def extract_json_object(text: str) -> dict:
    candidate = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", candidate, re.S | re.I)
    if fenced:
        candidate = fenced.group(1).strip()
    parsed = json.loads(candidate)
    if not isinstance(parsed, dict):
        raise ValueError("LLM output must be a JSON object.")
    return parsed


def validate_llm_knowledge_doc(output: dict, segment: dict) -> dict:
    missing = sorted(_REQUIRED_FIELDS - set(output))
    if missing:
        raise ValueError(f"LLM output missing required fields: {', '.join(missing)}")

    title = _require_text(output.get("title"), "title")
    content = _require_text(output.get("content"), "content")
    question_examples = _require_text_list(output.get("question_examples"), "question_examples")
    tags = _require_text_list(output.get("tags"), "tags")
    risk_level = _normalize_risk_level(output.get("risk_level"), segment.get("price_risk_level"))

    combined_text = "\n".join([title, content, *question_examples, *tags])
    if contains_original_price(combined_text):
        raise ValueError("LLM output contains original price information.")
    _, contains_sensitive = desensitize_text(combined_text)
    if contains_sensitive:
        raise ValueError("LLM output contains sensitive information.")

    return {
        "doc_no": f"kb_{segment.get('segment_no', 'segment')}",
        "title": title,
        "content": content,
        "question_examples": question_examples,
        "tags": tags,
        "business_line": segment.get("business_line"),
        "product_name": segment.get("product_name"),
        "risk_level": risk_level,
        "quality_score": _quality_score(content, question_examples),
        "review_status": "pending_review",
        "price_filtered": True,
        "contains_price_intent": bool(segment.get("contains_price_info")),
        "contains_original_price": False,
        "is_desensitized": True,
        "need_human_review": bool(output.get("need_human_review"))
        or risk_level in {RiskLevel.MEDIUM.value, RiskLevel.HIGH.value},
    }


def _require_text(value, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"LLM output field {field_name} must not be empty.")
    return text


def _require_text_list(value, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"LLM output field {field_name} must be a list.")
    result = [str(item).strip() for item in value if str(item or "").strip()]
    if not result:
        raise ValueError(f"LLM output field {field_name} must not be empty.")
    return result


def _normalize_risk_level(output_level, segment_level) -> str:
    output_value = str(output_level or RiskLevel.LOW.value).strip()
    segment_value = str(segment_level or RiskLevel.NONE.value).strip()
    if output_value not in _RISK_ORDER:
        output_value = RiskLevel.LOW.value
    if segment_value not in _RISK_ORDER:
        segment_value = RiskLevel.NONE.value
    return output_value if _RISK_ORDER[output_value] >= _RISK_ORDER[segment_value] else segment_value


def _quality_score(content: str, question_examples: list[str]) -> int:
    score = 20
    if len(content) >= 20:
        score += 5
    if question_examples:
        score += 3
    return min(score, 30)
