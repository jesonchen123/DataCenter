import re


_GREETING_ONLY = {"你好", "您好", "在吗", "在不在", "谢谢", "好的", "嗯", "哦"}


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"\s*\n+\s*", "，", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    normalized = normalized.replace(",", "，").replace("?", "？").replace("!", "！")
    normalized = re.sub(r"，{2,}", "，", normalized)
    normalized = re.sub(r"\s+([，。！？])", r"\1", normalized)
    return normalized


def clean_messages(messages: list[dict]) -> list[dict]:
    cleaned: list[dict] = []
    seen_contents: set[str] = set()

    for message in messages:
        content = normalize_text(str(message.get("content") or ""))
        if not content:
            continue
        if _is_system_message(message, content):
            continue
        if content in _GREETING_ONLY:
            continue
        if content in seen_contents:
            continue

        seen_contents.add(content)
        cleaned_message = dict(message)
        cleaned_message["content"] = content
        cleaned.append(cleaned_message)

    return cleaned


def _is_system_message(message: dict, content: str) -> bool:
    sender_role = str(message.get("sender_role") or "").lower()
    return sender_role == "system" or content.startswith("系统提示")
