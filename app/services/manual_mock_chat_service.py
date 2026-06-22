_ALLOWED_SENDER_ROLES = {"customer", "staff", "system"}
_ALLOWED_MESSAGE_FIELDS = {"role", "sender", "text"}


def build_manual_mock_chat_values(payload: dict) -> dict:
    mock_chat_id = _required_text(payload.get("mock_chat_id"), "mock_chat_id")
    source_platform = str(payload.get("source_platform") or "manual_test").strip() or "manual_test"
    messages = payload.get("messages") or []
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must contain at least one message.")

    normalized_messages = [
        _normalize_message(mock_chat_id, message, index)
        for index, message in enumerate(messages, start=1)
    ]
    business_line = _optional_text(payload.get("business_line"))
    product_name = _optional_text(payload.get("product_name"))
    scenario_type = _optional_text(payload.get("scenario_type"))

    raw_content = {
        "mock_chat_id": mock_chat_id,
        "source_platform": source_platform,
        "business_line": business_line,
        "product_name": product_name,
        "scenario_type": scenario_type,
        "messages": normalized_messages,
    }

    return {
        "mock_chat_id": mock_chat_id,
        "source_platform": source_platform,
        "business_line": business_line,
        "product_name": product_name,
        "scenario_type": scenario_type,
        "raw_content": raw_content,
    }


def _normalize_message(mock_chat_id: str, message: dict, index: int) -> dict:
    if not isinstance(message, dict):
        raise ValueError("message must be an object.")
    unexpected_fields = sorted(set(message) - _ALLOWED_MESSAGE_FIELDS)
    if unexpected_fields:
        raise ValueError(f"message contains unsupported fields: {', '.join(unexpected_fields)}.")
    sender_role = _required_text(message.get("role"), "role")
    if sender_role not in _ALLOWED_SENDER_ROLES:
        raise ValueError("role must be customer, staff, or system.")
    return {
        "message_id": f"{mock_chat_id}_msg_{index:03d}",
        "sender_role": sender_role,
        "sender_name": _optional_text(message.get("sender")),
        "content": _required_text(message.get("text"), "text"),
    }


def _required_text(value, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required.")
    return text


def _optional_text(value) -> str | None:
    text = str(value or "").strip()
    return text or None
