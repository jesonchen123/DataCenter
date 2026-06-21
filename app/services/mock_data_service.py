from itertools import cycle


_SCENARIOS = [
    (
        "product_consulting",
        "客户咨询产品功能",
        "这个产品能做什么？",
        "产品可以帮助企业整理内部知识并支持客服快速问答。",
    ),
    (
        "usage_flow",
        "客户咨询使用流程",
        "产品怎么使用？",
        "先登录后台，创建知识库，再导入整理后的知识片段。",
    ),
    (
        "after_sales",
        "客户咨询售后问题",
        "使用时无法登录怎么办？",
        "可以先重置密码，仍无法登录时提交售后工单。",
    ),
    (
        "common_question",
        "客户提出常见疑问",
        "可以多人一起维护知识库吗？",
        "可以，多名用户可以协同编辑候选知识片段。",
    ),
    (
        "buying_intent",
        "客户表达购买意向",
        "我们想采购给客服团队使用。",
        "可以先确认使用人数和业务场景，再安排正式销售流程。",
    ),
    (
        "customer_objection",
        "客户提出异议",
        "我们担心上线后维护成本太高。",
        "可以先从高频问题开始整理，逐步扩展知识范围。",
    ),
    (
        "price_consulting",
        "客户咨询价格",
        "这个产品多少钱？有没有优惠？",
        "具体价格需要以公司正式报价为准。",
    ),
    (
        "usage_issue",
        "客户反馈使用问题",
        "知识库回答不准确怎么办？",
        "可以检查知识片段是否完整，并提交人工审核更新。",
    ),
]


def build_mock_chats() -> list[dict]:
    chats: list[dict] = []
    scenario_cycle = cycle(_SCENARIOS)

    for index in range(1, 21):
        scenario_type, scenario_name, customer_text, staff_text = next(scenario_cycle)
        platform = "mock_wechat" if index % 2 else "mock_qq"
        mock_chat_id = f"mock_chat_{index:03d}"
        chats.append(
            {
                "mock_chat_id": mock_chat_id,
                "source_platform": platform,
                "business_line": "默认业务线",
                "product_name": "默认产品",
                "scenario_type": scenario_type,
                "raw_content": {
                    "mock_chat_id": mock_chat_id,
                    "source_platform": platform,
                    "business_line": "默认业务线",
                    "product_name": "默认产品",
                    "scenario_name": scenario_name,
                    "messages": [
                        {
                            "message_id": f"{mock_chat_id}_msg_001",
                            "sender_role": "customer",
                            "sender_name": "客户",
                            "message_time": f"2026-01-{((index - 1) % 28) + 1:02d}T10:00:00+08:00",
                            "content": customer_text,
                        },
                        {
                            "message_id": f"{mock_chat_id}_msg_002",
                            "sender_role": "staff",
                            "sender_name": "员工A",
                            "message_time": f"2026-01-{((index - 1) % 28) + 1:02d}T10:01:00+08:00",
                            "content": _staff_text_for(index, scenario_type, staff_text),
                        },
                    ],
                },
            }
        )

    return chats


def _staff_text_for(index: int, scenario_type: str, default: str) -> str:
    if scenario_type == "price_consulting" and index % 2 == 0:
        return "历史聊天中曾出现基础版 999 元，但知识库必须过滤该报价。"
    return default
