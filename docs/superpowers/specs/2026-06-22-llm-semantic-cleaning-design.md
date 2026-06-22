# 真实 LLM 语义清洗与知识生成设计

## 范围

本阶段在现有 PostgreSQL 驱动主流程上接入真实 LLM，用于语义级清洗和知识片段生成。LLM 不直接处理未脱敏、未过滤的原始聊天内容；原始数据仍只存放在 PostgreSQL 的 `mock_chats.raw_content` 和 `dialogue_segments.original_content` 中。

本阶段不实现正式 JWT、不做前端、不接入真实微信或 QQ 导入、不接入向量数据库。

## 目标

- 在现有规则清洗、脱敏、价格过滤之后调用真实 LLM。
- LLM 负责把已安全处理的对话片段整理为 RAG 知识候选。
- LLM 输出必须经过 JSON 结构校验、敏感信息检测和价格信息检测。
- LLM 调用全量写入 `llm_call_logs`，包含请求、响应、解析结果、状态、错误和耗时。
- LLM 不可用、超时、返回非法 JSON 或输出不安全内容时，自动回退到当前确定性知识生成逻辑。

## 最终数据清洗流程

1. 原始 Mock 或上传聊天数据入库。
2. 基础解析与规范化，删除空消息、重复消息、系统消息和纯寒暄。
3. 敏感信息脱敏，处理手机号、邮箱、QQ、微信号、订单号、身份证号等内容。
4. 价格信息硬过滤，删除金额、报价、折扣、优惠价、套餐价、定金、账期、返点、佣金和合同金额。
5. 构造对话片段，只把 `price_filtered_content` 等安全字段传给 LLM。
6. LLM 生成知识候选，输出固定 JSON 字段。
7. 后端校验 LLM JSON，重新检测敏感信息和原始价格。
8. 校验通过后写入 `dialogue_segments` 和 `knowledge_docs`。
9. 人工编辑并提交审核。
10. 管理层审核通过。
11. 导出前再次执行强校验，然后写入 `export_tasks.export_content`。

## LLM 接入边界

LLM 可以做：

- 判断对话是否有业务价值。
- 提取标题、知识正文、问题示例和标签。
- 标记是否需要人工补充。
- 为价格咨询生成安全标准回复。
- 输出风险等级建议。

LLM 不能做：

- 不能接收未脱敏原始聊天全文。
- 不能作为唯一的价格过滤手段。
- 不能决定最终导出权限。
- 不能绕过人工审核。
- 不能把模型输出直接作为可导出内容。

## 服务拆分

### `app/services/llm_client_service.py`

封装 OpenAI-compatible Chat Completions HTTP 调用。使用现有 `httpx` 依赖，不新增 SDK 依赖。

产出：

- `LLMClientError`
- `LLMChatResult`
- `OpenAICompatibleLLMClient`
- `is_llm_configured(settings) -> bool`

### `app/services/llm_prompt_service.py`

构造知识生成 Prompt。Prompt 只包含已脱敏、已价格过滤字段，不包含 `original_content`。

产出：

- `build_knowledge_generation_messages(segment: dict) -> list[dict]`

### `app/services/llm_validation_service.py`

解析和校验 LLM 输出。校验失败时抛出 `ValueError`，调用方回退确定性知识生成。

产出：

- `extract_json_object(text: str) -> dict`
- `validate_llm_knowledge_doc(output: dict, segment: dict) -> dict`

### `app/services/llm_knowledge_service.py`

组合 Prompt、Client、Validation 和 `llm_call_logs`。失败时回退到 `generate_knowledge_doc(segment)`。

产出：

- `generate_knowledge_doc_with_llm(segment, db=None, related_type=None, related_id=None, client=None) -> dict`

## 流水线改造

`process_mock_chat_payload(payload, knowledge_generator=None)` 增加可注入知识生成器。默认仍使用确定性 `generate_knowledge_doc`，保证单元测试和无 LLM 环境稳定。

Celery worker 在读取 `process_tasks` 后注入 LLM 生成器：

- 有有效 LLM 配置时调用真实 LLM。
- 调用成功时写入成功日志。
- 调用失败或输出不安全时写入失败日志，并回退确定性生成。

## 安全约束

- `.env.example` 只能保存占位符，真实 LLM Key 必须放入 `.env` 或部署环境变量。
- LLM 请求不得包含 `original_content`。
- LLM 输出中只要检测到原始价格或敏感信息，就不能作为知识文档内容使用。
- `contains_original_price` 必须由后端规则检测结果决定，不能信任 LLM 自报。
- 导出前继续使用现有 `validate_exportable` 强校验。

## 测试策略

- LLM 客户端测试使用 fake HTTP 函数，不访问真实网络。
- Prompt 测试验证不包含 `original_content`，只包含价格过滤后的安全内容。
- Validation 测试覆盖合法 JSON、Markdown code fence、缺字段、原始价格泄露、敏感信息泄露。
- Pipeline 测试验证可注入 LLM 生成器。
- Worker/服务层测试验证 LLM 成功、LLM 失败回退、LLM 调用日志写入。
- Docker 冒烟测试使用用户本地 `.env` 中的真实 LLM 配置执行一次完整处理链路；如果外部模型不可用，系统仍应回退并完成任务。

## 验收标准

- Docker 中触发 Mock 聊天处理后，可以调用真实 LLM 生成知识片段。
- `llm_call_logs` 中能看到成功或失败记录。
- LLM 不可用时处理任务仍能成功完成。
- LLM 输出包含价格或敏感信息时不会进入最终知识文档正文。
- 全量 `unittest` 和 `compileall` 通过。
