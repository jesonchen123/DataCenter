from dataclasses import dataclass, field
import re

from app.domain.enums import RiskLevel


STANDARD_PRICE_GUIDANCE = "具体价格以公司正式报价为准"

_INTENT_RE = re.compile(r"(多少钱|价格|报价|优惠|便宜|费用|收费|套餐)")
_AMOUNT_RE = re.compile(
    r"(¥\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:元|块|万|万元|人民币))"
)
_DISCOUNT_RE = re.compile(r"([一二三四五六七八九]\s*折|\d+(?:\.\d+)?\s*折|折扣|打折)")
_PREFERENTIAL_RE = re.compile(r"(优惠价|活动价|特价|最低价|促销价)")
_CONTRACT_RE = re.compile(r"(合同|总价|合同金额).{0,12}\d+(?:\.\d+)?\s*(?:元|万|万元)?")
_PAYMENT_RE = re.compile(r"(定金|首付|预付|先付|月结|账期).{0,12}(\d+(?:\.\d+)?\s*%?|\d+\s*天)")
_REBATE_RE = re.compile(r"(返点|返佣|返利).{0,12}\d+(?:\.\d+)?\s*%?")
_COMMISSION_RE = re.compile(r"(佣金|提成).{0,12}\d+(?:\.\d+)?\s*%?")

_HIGH_RISK_PATTERNS = {
    "amount": _AMOUNT_RE,
    "discount": _DISCOUNT_RE,
    "preferential_price": _PREFERENTIAL_RE,
    "contract_amount": _CONTRACT_RE,
    "payment_term": _PAYMENT_RE,
    "rebate": _REBATE_RE,
    "commission": _COMMISSION_RE,
}


@dataclass(frozen=True)
class PriceFilterResult:
    original_text: str
    filtered_text: str
    contains_price_info: bool
    contains_price_intent: bool
    contains_original_price: bool
    risk_level: str
    matched_categories: list[str] = field(default_factory=list)


def detect_price_info(text: str) -> PriceFilterResult:
    matched_categories = [
        name for name, pattern in _HIGH_RISK_PATTERNS.items() if pattern.search(text)
    ]
    has_intent = bool(_INTENT_RE.search(text))
    has_original_price = bool(matched_categories)
    has_price_info = has_intent or has_original_price

    if has_original_price:
        risk_level = RiskLevel.HIGH.value
    elif has_intent:
        risk_level = RiskLevel.MEDIUM.value
    else:
        risk_level = RiskLevel.NONE.value

    return PriceFilterResult(
        original_text=text,
        filtered_text=text,
        contains_price_info=has_price_info,
        contains_price_intent=has_intent,
        contains_original_price=has_original_price,
        risk_level=risk_level,
        matched_categories=matched_categories,
    )


def contains_original_price(text: str) -> bool:
    return detect_price_info(text).contains_original_price


def filter_price_content(text: str) -> PriceFilterResult:
    detection = detect_price_info(text)
    if not detection.contains_price_info:
        return detection

    retained_sentences: list[str] = []
    removed_original_price = False
    for sentence in _split_sentences(text):
        sentence_detection = detect_price_info(sentence)
        if sentence_detection.contains_original_price:
            removed_original_price = True
            continue
        retained_sentences.append(sentence)

    filtered_text = "。".join(s for s in retained_sentences if s).strip("。")
    if detection.contains_price_intent or removed_original_price:
        filtered_text = _append_guidance(filtered_text)

    return PriceFilterResult(
        original_text=text,
        filtered_text=filtered_text,
        contains_price_info=detection.contains_price_info,
        contains_price_intent=detection.contains_price_intent,
        contains_original_price=detection.contains_original_price,
        risk_level=detection.risk_level,
        matched_categories=detection.matched_categories,
    )


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[。！？!?；;\n]+", text) if part.strip()]


def _append_guidance(text: str) -> str:
    guidance = f"价格信息已过滤，{STANDARD_PRICE_GUIDANCE}"
    if not text:
        return guidance
    if STANDARD_PRICE_GUIDANCE in text:
        return text
    return f"{text}。{guidance}"
