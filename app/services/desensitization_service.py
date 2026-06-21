import re


_PATTERNS = [
    ("<EMAIL>", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("<ID_CARD>", re.compile(r"\b\d{17}[\dXx]\b")),
    ("<PHONE>", re.compile(r"\b1[3-9]\d{9}\b")),
    ("<ORDER_ID>", re.compile(r"\b(?:ORD|ORDER|订单号[:：]?)\s*[A-Za-z0-9_-]{8,}\b", re.I)),
    ("<WECHAT>", re.compile(r"(微信|wx|wechat)[:：\s]*[A-Za-z][A-Za-z0-9_-]{5,19}", re.I)),
    ("<QQ>", re.compile(r"(QQ|qq)[:：\s]*[1-9]\d{4,11}")),
]


def desensitize_text(text: str) -> tuple[str, bool]:
    result = text
    changed = False
    for replacement, pattern in _PATTERNS:
        result, count = pattern.subn(replacement, result)
        changed = changed or count > 0
    return result, changed
