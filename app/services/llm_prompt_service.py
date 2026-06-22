import json

from app.services.price_filter_service import filter_price_content


SYSTEM_PROMPT = (
    "你是企业内部知识库数据整理助手。"
    "你只能基于输入中的安全字段生成 RAG 知识片段。"
    "不要输出手机号、微信号、QQ、邮箱、订单号、身份证号、地址、姓名等敏感信息。"
    "不要输出任何具体价格、报价、折扣、优惠价、套餐价、合同金额、账期、返点或佣金。"
    "如果客户咨询价格，只保留价格咨询意图，并说明具体价格以公司正式报价为准。"
    "content 字段必须只使用“客户问：...\\n销售答：...”的问答格式。"
    "不要输出时间、发送人姓名、消息 ID、原始聊天记录或字段名。"
    "输出必须是单个 JSON 对象，字段包括 title、content、question_examples、tags、risk_level、need_human_review。"
)


def build_knowledge_generation_messages(segment: dict) -> list[dict]:
    safe_question = filter_price_content(str(segment.get("customer_question") or "")).filtered_text
    safe_answer = filter_price_content(str(segment.get("staff_answer") or "")).filtered_text
    payload = {
        "customer_question": safe_question,
        "staff_answer": safe_answer,
        "business_line": segment.get("business_line"),
        "product_name": segment.get("product_name"),
        "contains_price_info": bool(segment.get("contains_price_info")),
        "price_risk_level": segment.get("price_risk_level") or "none",
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, sort_keys=True),
        },
    ]
