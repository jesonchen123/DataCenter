"""Dialogue segmentation service.

Splits a cleaned conversation into independent Q&A pairs.  Uses LLM when
available, falls back to rule-based turn-taking merging.
"""

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class QAPair:
    customer_question: str
    staff_answer: str
    scenario_type: str = "other"


SEGMENTATION_SYSTEM_PROMPT = (
    "你是客服对话分段与总结助手。分析对话记录，将其切分为独立问答对。\n"
    "规则：\n"
    "1. 识别对话中的主题转换，判断每个独立的客户提问\n"
    "2. 将同一客户的多条连续消息合并总结为一个完整问题\n"
    "3. 将同一销售的多条连续回复合并总结为一个完整答案\n"
    "4. 跳过纯问候语（\"你好\"\"您好\"\"在吗\"\"谢谢\"\"好的\"\"嗯\"\"哦\"）和无实质内容的确认词\n"
    "5. 每个问答对必须同时有 customer_question 和 staff_answer\n"
    "6. customer_question 和 staff_answer 必须是完整、通顺的中文句子\n"
    "7. 只输出 JSON 对象，不要输出其他文字或解释\n"
    "\n"
    "scenario_type 可选值（根据对话核心内容判断最合适的类型）：\n"
    "- price_consulting: 价格咨询（讨论价格、折扣、优惠、费用等）\n"
    "- product_inquiry: 产品咨询（了解产品功能、特性、适用场景等）\n"
    "- after_sales: 售后服务（退换货、维修、使用问题等）\n"
    "- technical_support: 技术支持（接入方式、系统对接、API等）\n"
    "- complaint: 投诉建议（客户不满、投诉、改进建议等）\n"
    "- other: 其他类型\n"
    "\n"
    "输出格式（严格 JSON 对象）：\n"
    '{"qa_pairs": [{"customer_question": "客户的核心问题", "staff_answer": "销售的完整回答", "scenario_type": "product_inquiry"}]}'
)

_VALID_SCENARIO_TYPES = {
    "price_consulting",
    "product_inquiry",
    "after_sales",
    "technical_support",
    "complaint",
    "other",
}


def segment_dialogue(messages: list[dict]) -> tuple[list[QAPair], str]:
    """Segment cleaned conversation messages into Q&A pairs.

    Returns (qa_pairs, strategy) where strategy is "llm" or "rule".
    """
    if not messages:
        raise ValueError("No messages to segment.")

    # Strategy 1: LLM segmentation
    if _is_llm_available():
        try:
            result = _segment_via_llm(messages)
            return result, "llm"
        except Exception:
            pass

    # Strategy 2: Rule-based fallback
    result = _segment_via_rules(messages)
    return result, "rule"


def _is_llm_available() -> bool:
    try:
        from app.services.llm_client_service import is_llm_configured

        return is_llm_configured()
    except Exception:
        return False


def _segment_via_llm(messages: list[dict]) -> list[QAPair]:
    from app.services.llm_client_service import OpenAICompatibleLLMClient

    # Build conversation text
    conversation_lines = []
    for msg in messages:
        role = msg.get("sender_role", "")
        content = str(msg.get("content") or "").strip()
        if not content or not role:
            continue
        role_label = "客户" if role == "customer" else ("销售" if role == "staff" else role)
        conversation_lines.append(f"{role_label}：{content}")

    if not conversation_lines:
        raise ValueError("No valid conversation content for LLM segmentation.")

    raw_text = "\n".join(conversation_lines)

    client = OpenAICompatibleLLMClient()
    llm_messages = [
        {"role": "system", "content": SEGMENTATION_SYSTEM_PROMPT},
        {"role": "user", "content": raw_text},
    ]
    result = client.chat(llm_messages, response_format={"type": "json_object"})

    parsed = _parse_json_output(result.content)
    if isinstance(parsed, list):
        candidates = parsed
    elif isinstance(parsed, dict) and "qa_pairs" in parsed:
        candidates = parsed["qa_pairs"]
    else:
        raise ValueError("LLM segmentation output must contain 'qa_pairs' array.")

    if not isinstance(candidates, list) or not candidates:
        raise ValueError("LLM returned no Q&A pairs.")

    qa_pairs = []
    for i, item in enumerate(candidates, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Q&A pair {i} must be an object.")
        question = str(item.get("customer_question") or "").strip()
        answer = str(item.get("staff_answer") or "").strip()
        if not question:
            raise ValueError(f"Q&A pair {i}: customer_question is required.")
        if not answer:
            raise ValueError(f"Q&A pair {i}: staff_answer is required.")
        scenario = str(item.get("scenario_type") or "other").strip()
        if scenario not in _VALID_SCENARIO_TYPES:
            scenario = "other"
        qa_pairs.append(
            QAPair(
                customer_question=question,
                staff_answer=answer,
                scenario_type=scenario,
            )
        )

    return qa_pairs


def _parse_json_output(text: str):
    """Parse LLM output, handling markdown code fences."""
    import re

    candidate = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", candidate, re.S | re.I)
    if fenced:
        candidate = fenced.group(1).strip()
    return json.loads(candidate)


def _segment_via_rules(messages: list[dict]) -> list[QAPair]:
    """Rule-based segmentation.

    Merges consecutive same-role messages, then pairs each customer
    block with the following staff block(s).
    """
    # Step 1: Merge consecutive same-role messages
    merged: list[dict] = []
    for msg in messages:
        role = msg.get("sender_role", "")
        content = str(msg.get("content") or "").strip()
        if not content or not role:
            continue

        if merged and merged[-1]["sender_role"] == role:
            merged[-1]["content"] += "，" + content
        else:
            merged.append({"sender_role": role, "content": content})

    # Step 2: Pair customer blocks with following staff blocks
    qa_pairs: list[QAPair] = []
    i = 0
    while i < len(merged):
        if merged[i]["sender_role"] == "customer":
            question = merged[i]["content"]
            answer_parts = []
            j = i + 1
            while j < len(merged) and merged[j]["sender_role"] == "staff":
                answer_parts.append(merged[j]["content"])
                j += 1
            if answer_parts:
                answer = "。".join(answer_parts)
                qa_pairs.append(
                    QAPair(
                        customer_question=question,
                        staff_answer=answer,
                        scenario_type="other",
                    )
                )
            i = j
        else:
            i += 1

    if not qa_pairs:
        raise ValueError(
            "No Q&A pairs found. Ensure conversation has customer→staff exchanges."
        )

    return qa_pairs
