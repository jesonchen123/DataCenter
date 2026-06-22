# 自定义 Mock 聊天记录创建接口设计

## 范围

本阶段新增一个开发态接口，用于手动写入原始聊天记录，方便通过现有处理、LLM 清洗、审核和导出流程做测试。

## 接口

新增：

```text
POST /api/v1/mock-chats
```

请求体：

```json
{
  "mock_chat_id": "custom_chat_001",
  "source_platform": "manual_test",
  "business_line": "测试业务线",
  "product_name": "测试产品",
  "scenario_type": "price_consulting",
  "messages": [
    {
      "message_id": "msg_001",
      "sender_role": "customer",
      "sender_name": "客户A",
      "message_time": "2026-06-22T10:00:00+08:00",
      "content": "这个产品多少钱？"
    }
  ]
}
```

响应复用现有 `serialize_mock_chat` 格式。创建成功后可继续调用：

```text
POST /api/v1/mock-chats/{mock_chat_id}/process
```

## 规则

- `mock_chat_id` 必填且唯一。
- `source_platform` 默认为 `manual_test`。
- `messages` 必须至少包含一条消息。
- 每条消息必须包含 `message_id`、`sender_role`、`content`。
- `sender_role` 只允许 `customer`、`staff`、`system`。
- 原始请求组装后写入 `mock_chats.raw_content`。
- 重复 `mock_chat_id` 返回 HTTP 409。
- 当前阶段 `manager` 和 `normal_user` 都可以创建，便于调试。

## 非目标

- 不做文件上传。
- 不做批量导入。
- 不接入真实微信或 QQ。
- 不在本阶段实现正式 JWT 权限。

## 验收标准

- 可以通过 API 新建一条自定义聊天记录。
- 新建记录可以通过 `GET /api/v1/mock-chats/{mock_chat_id}` 查询。
- 新建记录可以触发 `/process` 并进入现有处理流程。
- 重复 `mock_chat_id` 返回 409。
