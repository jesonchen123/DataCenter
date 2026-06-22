from app.domain.enums import RiskLevel
from app.services.price_filter_service import contains_original_price


def generate_knowledge_doc(segment: dict) -> dict:
    contains_price_info = bool(segment.get("contains_price_info"))
    content = str(segment.get("price_filtered_content") or "").strip()
    customer_question = str(segment.get("customer_question") or "").strip()
    risk_level = str(segment.get("price_risk_level") or RiskLevel.LOW.value)

    if contains_price_info:
        title = "客户咨询价格时的标准回复"
        doc_content = _qa_content(customer_question or "这个产品多少钱？", "具体价格以公司正式报价为准。")
        tags = ["价格咨询", "售前", "需人工确认"]
        question_examples = [customer_question or "这个产品多少钱？", "有没有优惠？", "可以便宜一点吗？"]
        need_human_review = True
    else:
        title = customer_question or "客户业务咨询"
        staff_answer = str(segment.get("staff_answer") or "").strip()
        doc_content = _qa_content(customer_question, staff_answer) if customer_question and staff_answer else content or "需要人工补充"
        tags = ["产品咨询"]
        question_examples = [customer_question] if customer_question else []
        need_human_review = doc_content == "需要人工补充"
        if risk_level == RiskLevel.NONE.value:
            risk_level = RiskLevel.LOW.value

    return {
        "doc_no": f"kb_{segment.get('segment_no', 'segment')}",
        "title": title,
        "content": doc_content,
        "question_examples": question_examples,
        "tags": tags,
        "business_line": segment.get("business_line"),
        "product_name": segment.get("product_name"),
        "risk_level": risk_level,
        "quality_score": _quality_score(doc_content, question_examples),
        "review_status": "pending_review",
        "price_filtered": True,
        "contains_price_intent": contains_price_info,
        "contains_original_price": contains_original_price(doc_content),
        "is_desensitized": True,
        "need_human_review": need_human_review,
    }


def _quality_score(content: str, question_examples: list[str]) -> int:
    score = 20
    if len(content) >= 20:
        score += 5
    if question_examples:
        score += 3
    return min(score, 30)


def _qa_content(customer_question: str, staff_answer: str) -> str:
    return f"客户问：{customer_question}\n销售答：{staff_answer}"
