_ALLOWED_SENDER_ROLES = {"customer", "staff", "system"}


def build_manual_mock_chat_values(payload: dict) -> dict:
    mock_chat_id = _required_text(payload.get("mock_chat_id"), "mock_chat_id")
    source_platform = str(payload.get("source_platform") or "manual_test").strip() or "manual_test"
    messages = payload.get("messages") or []
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must contain at least one message.")

    normalized_messages = [_normalize_message(message) for message in messages]
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


def _normalize_message(message: dict) -> dict:
    if not isinstance(message, dict):
        raise ValueError("message must be an object.")
    sender_role = _required_text(message.get("sender_role"), "sender_role")
    if sender_role not in _ALLOWED_SENDER_ROLES:
        raise ValueError("sender_role must be customer, staff, or system.")
    return {
        "message_id": _required_text(message.get("message_id"), "message_id"),
        "sender_role": sender_role,
        "sender_name": _optional_text(message.get("sender_name")),
        "message_time": _optional_text(message.get("message_time")),
        "content": _required_text(message.get("content"), "content"),
    }


def _required_text(value, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required.")
    return text


def _optional_text(value) -> str | None:
    text = str(value or "").strip()
    return text or None
