# 真实 LLM 语义清洗与知识生成实施计划

> **给 agent 工作者的说明：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务逐项实施本计划。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** 在规则清洗、脱敏和价格过滤之后接入真实 LLM，生成更高质量的 RAG 知识候选，并保留安全回退和调用日志。

**架构：** LLM 客户端、Prompt、输出校验和知识生成编排拆成独立服务。处理流水线继续先执行规则安全层，再通过可注入知识生成器调用 LLM；Celery worker 负责注入数据库日志上下文。

**技术栈：** Python 3.12、FastAPI、SQLAlchemy、PostgreSQL、Celery、Redis、httpx、unittest、Docker Compose。

## 全局约束

- 真实 LLM Key 不允许提交到 Git。
- `.env.example` 只保留占位符，真实配置使用 `.env` 或部署环境变量。
- LLM 不接收 `original_content`。
- LLM 输出必须经过 JSON 校验、敏感信息检测和价格信息检测。
- LLM 失败必须回退确定性知识生成。
- 导出前继续使用现有强校验。
- 新增文档和 todo 使用中文。

---

## 任务 17：LLM 客户端与配置保护

**文件：**
- 创建：`app/services/llm_client_service.py`
- 创建：`tests/test_llm_client_service.py`
- 修改：`.env.example`
- 修改：`README.md`

**接口：**
- 产出：`LLMClientError`
- 产出：`LLMChatResult`
- 产出：`is_llm_configured(settings) -> bool`
- 产出：`OpenAICompatibleLLMClient.chat(messages: list[dict], response_format: dict | None = None) -> LLMChatResult`

- [ ] 步骤 1：编写失败测试，验证未配置 Key 时 `is_llm_configured` 返回 `False`。
- [ ] 步骤 2：编写失败测试，使用 fake HTTP 函数验证 Chat Completions 请求体、Authorization header 和响应解析。
- [ ] 步骤 3：运行 `python -m unittest tests.test_llm_client_service`，确认失败。
- [ ] 步骤 4：实现 LLM 客户端和配置判断。
- [ ] 步骤 5：把 `.env.example` 中真实 Key 改回占位符，并在 README 写明真实 Key 放 `.env`。
- [ ] 步骤 6：运行 `python -m unittest tests.test_llm_client_service` 和 `python -m unittest discover -s tests`。
- [ ] 步骤 7：提交，提交信息为 `feat: add openai compatible llm client`。

## 任务 18：安全 Prompt 与 LLM 输出校验

**文件：**
- 创建：`app/services/llm_prompt_service.py`
- 创建：`app/services/llm_validation_service.py`
- 创建：`tests/test_llm_prompt_service.py`
- 创建：`tests/test_llm_validation_service.py`

**接口：**
- 产出：`build_knowledge_generation_messages(segment: dict) -> list[dict]`
- 产出：`extract_json_object(text: str) -> dict`
- 产出：`validate_llm_knowledge_doc(output: dict, segment: dict) -> dict`

- [ ] 步骤 1：编写失败测试，验证 Prompt 不包含 `original_content`，并包含 `price_filtered_content`。
- [ ] 步骤 2：编写失败测试，验证 Markdown code fence 中的 JSON 可以被解析。
- [ ] 步骤 3：编写失败测试，验证缺少必填字段、包含原始价格、包含敏感信息时校验失败。
- [ ] 步骤 4：运行 `python -m unittest tests.test_llm_prompt_service tests.test_llm_validation_service`，确认失败。
- [ ] 步骤 5：实现 Prompt 构造和输出校验。
- [ ] 步骤 6：运行 `python -m unittest tests.test_llm_prompt_service tests.test_llm_validation_service`。
- [ ] 步骤 7：提交，提交信息为 `feat: add safe llm prompt and validation`。

## 任务 19：LLM 知识生成服务与调用日志

**文件：**
- 创建：`app/services/llm_knowledge_service.py`
- 创建：`tests/test_llm_knowledge_service.py`

**接口：**
- 产出：`generate_knowledge_doc_with_llm(segment: dict, db=None, related_type: str | None = None, related_id=None, client=None) -> dict`

- [ ] 步骤 1：编写失败测试，验证 LLM 成功时返回校验后的知识文档。
- [ ] 步骤 2：编写失败测试，验证 LLM 调用成功会向 fake db 写入 `LLMCallLog(status="success")`。
- [ ] 步骤 3：编写失败测试，验证 LLM 抛错或输出不安全时回退确定性 `generate_knowledge_doc`，并写入失败日志。
- [ ] 步骤 4：运行 `python -m unittest tests.test_llm_knowledge_service`，确认失败。
- [ ] 步骤 5：实现 LLM 知识生成服务和日志写入。
- [ ] 步骤 6：运行 `python -m unittest tests.test_llm_knowledge_service` 和 `python -m unittest discover -s tests`。
- [ ] 步骤 7：提交，提交信息为 `feat: add llm knowledge generation service`。

## 任务 20：处理流水线接入 LLM

**文件：**
- 修改：`app/services/processing_pipeline.py`
- 修改：`app/workers/tasks.py`
- 修改：`tests/test_processing_pipeline.py`

**接口：**
- 修改：`process_mock_chat_payload(payload: dict, knowledge_generator=None) -> dict`

- [ ] 步骤 1：编写失败测试，验证 `process_mock_chat_payload` 会调用注入的 `knowledge_generator(segment)`。
- [ ] 步骤 2：运行 `python -m unittest tests.test_processing_pipeline`，确认失败。
- [ ] 步骤 3：改造流水线支持可注入知识生成器，默认保持确定性生成。
- [ ] 步骤 4：改造 Celery worker，在任务执行时注入 `generate_knowledge_doc_with_llm`。
- [ ] 步骤 5：运行 `python -m unittest tests.test_processing_pipeline tests.test_llm_knowledge_service`。
- [ ] 步骤 6：提交，提交信息为 `feat: connect llm generation to processing pipeline`。

## 任务 21：Docker LLM 主流程验证

**文件：**
- 修改：`README.md`
- 修改：`todo.md`

**接口：**
- 文档记录真实 LLM 配置、Docker 启动、处理、日志查询和回退验证命令。

- [ ] 步骤 1：运行 `docker compose run --rm backend python -m unittest discover -s tests`。
- [ ] 步骤 2：运行 `docker compose run --rm backend python -m compileall app tests`。
- [ ] 步骤 3：使用 Docker API 冒烟验证处理任务可调用 LLM 或安全回退。
- [ ] 步骤 4：使用 PostgreSQL 查询验证 `llm_call_logs` 有成功或失败记录。
- [ ] 步骤 5：更新 README 和 todo。
- [ ] 步骤 6：提交，提交信息为 `docs: document llm semantic cleaning flow`。

## 任务 22：最终安全回归

**文件：**
- 修改：`todo.md`

**接口：**
- 验证价格过滤、脱敏、导出强校验和 LLM 回退链路没有回归。

- [ ] 步骤 1：运行 `python -m unittest discover -s tests`。
- [ ] 步骤 2：运行 `docker compose run --rm backend python -m unittest discover -s tests`。
- [ ] 步骤 3：运行一次价格咨询 Mock 聊天处理、审核、导出冒烟。
- [ ] 步骤 4：确认导出 JSON 中 `security.contains_original_price` 为 `false`。
- [ ] 步骤 5：提交，提交信息为 `test: verify llm cleaning safety regression`。
