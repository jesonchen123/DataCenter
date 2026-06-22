# 数据中台后端 MVP 实施计划

> **给 agent 工作者的说明：** 必须使用 `superpowers:executing-plans` 按任务逐项实施本计划。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** 构建数据中台第一版 MVP 的 FastAPI 后端骨架和核心 Mock 数据处理流程。

**架构：** FastAPI 对外提供认证、Mock 聊天、处理任务、知识审核、导出和审计 API。PostgreSQL 是唯一业务数据存储；Redis 只用于 Celery。核心处理逻辑实现为纯服务，便于在安装第三方依赖前先进行测试。

**技术栈：** Python 3.12 目标版本、FastAPI、Pydantic、SQLAlchemy、Alembic、PostgreSQL、Celery、Redis、python-jose、passlib/bcrypt、pytest，以及用于无依赖核心服务测试的 unittest。

## 全局约束

- 第一版只包含两个角色：`manager` 和 `normal_user`。
- 第一版不接入真实微信或 QQ 数据。
- 第一版使用内置 Mock 数据驱动完整流程。
- 所有长期业务数据都存储在 PostgreSQL。
- Redis 只用于 Celery 队列和任务状态缓存。
- 导出的 JSON 存储在 `export_tasks.export_content`，不写入本地文件。
- 价格过滤必须发生在知识文档生成之前。
- 导出 JSON 入库前必须再次校验。
- 普通用户不能导出数据。
- 只有管理层可以审核和导出数据。
- 任何包含原始价格的知识文档都不能导出。
- 前端不在本计划范围内。

---

## 任务 1：项目骨架与依赖契约

**文件：**
- 创建：`README.md`
- 创建：`.env.example`
- 创建：`.gitignore`
- 创建：`requirements.txt`
- 创建：`docker-compose.yml`
- 创建：`Dockerfile`
- 创建：`app/__init__.py`
- 创建：`app/main.py`
- 创建：`app/api/__init__.py`
- 创建：`app/api/v1/__init__.py`
- 创建：`app/core/__init__.py`
- 创建：`app/core/config.py`
- 创建：`tests/__init__.py`

**接口：**
- 产出：`app.main:create_app() -> FastAPI`
- 产出：`app.core.config.Settings`

- [x] 步骤 1：创建依赖和环境文件。
- [x] 步骤 2：创建应用包骨架。
- [x] 步骤 3：创建带健康检查接口的 FastAPI app 工厂。
- [x] 步骤 4：运行 `python -m unittest discover -s tests`。
- [x] 步骤 5：提交，提交信息为 `chore: scaffold backend project`。

## 任务 2：核心领域类型与权限规则

**文件：**
- 创建：`app/domain/__init__.py`
- 创建：`app/domain/enums.py`
- 创建：`app/core/permissions.py`
- 创建：`tests/test_permissions.py`

**接口：**
- 产出：`Role`、`ReviewStatus`、`RiskLevel`、`PriceFilterStatus`
- 产出：`can_export(role: str) -> bool`
- 产出：`can_approve(role: str) -> bool`
- 产出：`can_view_audit_logs(role: str) -> bool`

- [x] 步骤 1：为 `manager` 和 `normal_user` 编写失败的权限测试。
- [x] 步骤 2：运行 `python -m unittest tests.test_permissions`。
- [x] 步骤 3：实现枚举和权限辅助函数。
- [x] 步骤 4：运行 `python -m unittest tests.test_permissions`。
- [x] 步骤 5：提交，提交信息为 `feat: add role permission rules`。

## 任务 3：价格过滤服务

**文件：**
- 创建：`app/services/__init__.py`
- 创建：`app/services/price_filter_service.py`
- 创建：`tests/test_price_filter_service.py`

**接口：**
- 产出：`PriceFilterResult`
- 产出：`detect_price_info(text: str) -> PriceFilterResult`
- 产出：`filter_price_content(text: str) -> PriceFilterResult`
- 产出：`contains_original_price(text: str) -> bool`

- [x] 步骤 1：为金额、折扣、优惠价、合同金额、账期、返点、佣金和客户询价意图编写失败测试。
- [x] 步骤 2：运行 `python -m unittest tests.test_price_filter_service`。
- [x] 步骤 3：实现基于正则的价格识别和句子过滤。
- [x] 步骤 4：运行 `python -m unittest tests.test_price_filter_service`。
- [x] 步骤 5：提交，提交信息为 `feat: add price filtering service`。

## 任务 4：清洗与脱敏服务

**文件：**
- 创建：`app/services/cleaning_service.py`
- 创建：`app/services/desensitization_service.py`
- 创建：`tests/test_cleaning_service.py`
- 创建：`tests/test_desensitization_service.py`

**接口：**
- 产出：`clean_messages(messages: list[dict]) -> list[dict]`
- 产出：`normalize_text(text: str) -> str`
- 产出：`desensitize_text(text: str) -> tuple[str, bool]`

- [x] 步骤 1：为空消息、重复消息、系统提示、简单寒暄和标点归一化编写失败的清洗测试。
- [x] 步骤 2：为手机号、邮箱、QQ、微信号、订单号和身份证号编写失败的脱敏测试。
- [x] 步骤 3：运行 `python -m unittest tests.test_cleaning_service tests.test_desensitization_service`。
- [x] 步骤 4：实现清洗和脱敏服务。
- [x] 步骤 5：运行 `python -m unittest tests.test_cleaning_service tests.test_desensitization_service`。
- [x] 步骤 6：提交，提交信息为 `feat: add cleaning and desensitization services`。

## 任务 5：确定性知识生成与导出校验

**文件：**
- 创建：`app/services/knowledge_service.py`
- 创建：`app/services/export_service.py`
- 创建：`tests/test_knowledge_service.py`
- 创建：`tests/test_export_service.py`

**接口：**
- 产出：`generate_knowledge_doc(segment: dict) -> dict`
- 产出：`validate_exportable(doc: dict, requester_role: str) -> None`
- 产出：`build_export_content(docs: list[dict], created_by: str) -> dict`

- [x] 步骤 1：为价格咨询意图知识文档和非价格业务文档编写失败测试。
- [x] 步骤 2：为角色、审核状态、脱敏、价格过滤、原始价格和高风险审批编写失败的导出校验测试。
- [x] 步骤 3：运行 `python -m unittest tests.test_knowledge_service tests.test_export_service`。
- [x] 步骤 4：实现确定性知识生成和导出校验。
- [x] 步骤 5：运行 `python -m unittest tests.test_knowledge_service tests.test_export_service`。
- [x] 步骤 6：提交，提交信息为 `feat: add knowledge generation and export validation`。

## 任务 6：SQLAlchemy 模型与 Alembic 迁移

**文件：**
- 创建：`app/db/__init__.py`
- 创建：`app/db/base.py`
- 创建：`app/db/session.py`
- 创建：`app/models/__init__.py`
- 创建：`app/models/user.py`
- 创建：`app/models/mock_chat.py`
- 创建：`app/models/process_task.py`
- 创建：`app/models/dialogue_segment.py`
- 创建：`app/models/knowledge_doc.py`
- 创建：`app/models/export_task.py`
- 创建：`app/models/audit_log.py`
- 创建：`app/models/llm_call_log.py`
- 创建：`alembic.ini`
- 创建：`alembic/env.py`
- 创建：`alembic/versions/20260621_0001_init_tables.py`

**接口：**
- 按技术实现文档产出 PostgreSQL 数据表。

- [x] 步骤 1：创建与文档中 PostgreSQL schema 匹配的 SQLAlchemy 模型文件。
- [x] 步骤 2：创建 Alembic 配置和初始迁移，包含 `pgcrypto`、数据表、外键和索引。
- [x] 步骤 3：依赖安装后运行导入冒烟检查：`python -c "from app.models import User, MockChat, ProcessTask, DialogueSegment, KnowledgeDoc, ExportTask, AuditLog, LLMCallLog"`（已延后到依赖安装后执行）。
- [x] 步骤 4：提交，提交信息为 `feat: add database models and migration`。

## 任务 7：Mock 数据初始化

**文件：**
- 创建：`app/db/init_db.py`
- 创建：`app/services/mock_data_service.py`
- 创建：`tests/test_mock_data_service.py`

**接口：**
- 产出：`build_mock_chats() -> list[dict]`
- 产出：`python -m app.db.init_db`

- [x] 步骤 1：编写失败测试，验证至少生成 20 条 Mock 聊天，并覆盖产品咨询、售后问题、价格咨询和客户异议。
- [x] 步骤 2：运行 `python -m unittest tests.test_mock_data_service`。
- [x] 步骤 3：实现确定性的 Mock 数据构造器和数据库初始化命令。
- [x] 步骤 4：运行 `python -m unittest tests.test_mock_data_service`。
- [x] 步骤 5：提交，提交信息为 `feat: add mock data seed builder`。

## 任务 8：处理流水线与 Celery 任务

**文件：**
- 创建：`app/services/processing_pipeline.py`
- 创建：`app/workers/__init__.py`
- 创建：`app/workers/celery_app.py`
- 创建：`app/workers/tasks.py`
- 创建：`tests/test_processing_pipeline.py`

**接口：**
- 产出：`process_mock_chat_payload(payload: dict) -> dict`
- 产出：Celery 任务 `process_mock_chat_task(process_task_id: str) -> dict`

- [x] 步骤 1：为解析、清洗、脱敏、价格过滤、分段和知识输出编写失败的流水线测试。
- [x] 步骤 2：运行 `python -m unittest tests.test_processing_pipeline`。
- [x] 步骤 3：实现无第三方依赖的 payload 处理流水线。
- [x] 步骤 4：添加 Celery app 和面向数据库执行的任务包装。
- [x] 步骤 5：运行 `python -m unittest tests.test_processing_pipeline`。
- [x] 步骤 6：提交，提交信息为 `feat: add mock chat processing pipeline`。

## 任务 9：API Schema 与路由

**文件：**
- 创建：`app/schemas/__init__.py`
- 创建：`app/api/v1/auth.py`
- 创建：`app/api/v1/mock_chats.py`
- 创建：`app/api/v1/process_tasks.py`
- 创建：`app/api/v1/knowledge_docs.py`
- 创建：`app/api/v1/export_tasks.py`
- 创建：`app/api/v1/audit_logs.py`
- 修改：`app/main.py`

**接口：**
- 产出：`/api/v1/auth/login`
- 产出：`/api/v1/mock-chats`
- 产出：`/api/v1/mock-chats/{id}`
- 产出：`/api/v1/mock-chats/{id}/process`
- 产出：`/api/v1/process-tasks/{id}`
- 产出：`/api/v1/knowledge-docs`
- 产出：`/api/v1/knowledge-docs/{id}/submit-review`
- 产出：`/api/v1/knowledge-docs/{id}/review`
- 产出：`/api/v1/export-tasks`
- 产出：`/api/v1/export-tasks/{id}/content`
- 产出：`/api/v1/audit-logs`

- [x] 步骤 1：添加请求和响应对象的 Pydantic schema。
- [x] 步骤 2：添加路由，并为数据库 session 和当前用户保留依赖占位。
- [x] 步骤 3：在路由入口执行角色检查。
- [x] 步骤 4：依赖安装后运行导入冒烟检查（已延后到依赖安装后执行）。
- [x] 步骤 5：提交，提交信息为 `feat: add backend API routers`。

## 任务 10：最终验证与文档

**文件：**
- 修改：`README.md`
- 修改：`todo.md`

**接口：**
- 产出本地测试、Docker、迁移、种子数据、API、worker 和导出的运行命令文档。

- [x] 步骤 1：运行 `python -m unittest discover -s tests`。
- [x] 步骤 2：更新 README，补充本地和 Docker 用法。
- [x] 步骤 3：标记 `todo.md` 中所有已完成任务。
- [x] 步骤 4：运行 `git status --short`。
- [x] 步骤 5：提交，提交信息为 `docs: document backend mvp usage`。

---

# 第二阶段：数据库驱动 API 主流程

> 设计文档：`docs/superpowers/specs/2026-06-22-db-driven-api-main-flow-design.md`
>
> 详细计划：`docs/superpowers/plans/2026-06-22-db-driven-api-main-flow.md`

## 任务 11：数据库序列化与任务服务

- [x] 步骤 1：先写序列化失败测试。
- [x] 步骤 2：运行 `python -m unittest tests.test_db_serializers`，确认失败。
- [x] 步骤 3：实现序列化和任务服务。
- [x] 步骤 4：运行 `python -m unittest tests.test_db_serializers`，确认通过。
- [x] 步骤 5：提交，提交信息为 `feat: add database task services`。

## 任务 12：Mock 数据 API 读写 PostgreSQL

- [x] 步骤 1：编写容器内 API 冒烟脚本，验证当前接口仍返回占位数据。
- [x] 步骤 2：改造路由使用 `get_db` 和任务服务。
- [x] 步骤 3：运行 Docker 容器内测试和接口冒烟检查。
- [x] 步骤 4：提交，提交信息为 `feat: drive mock chat APIs from database`。

## 任务 13：处理结果持久化

- [x] 步骤 1：编写失败测试，验证流水线结果会转换为待持久化结构。
- [x] 步骤 2：运行 `python -m unittest tests.test_persistence_service`，确认失败。
- [x] 步骤 3：实现持久化服务并接入 worker。
- [x] 步骤 4：运行单元测试和 Docker 数据库验证。
- [x] 步骤 5：提交，提交信息为 `feat: persist processing results`。

## 任务 14：知识文档审核 API 落库

- [x] 步骤 1：编写服务层失败测试。
- [x] 步骤 2：实现 review service。
- [x] 步骤 3：改造 knowledge docs 路由。
- [x] 步骤 4：运行测试和 Docker API 验证。
- [x] 步骤 5：提交，提交信息为 `feat: add database backed review APIs`。

## 任务 15：导出与审计 API 落库

- [x] 步骤 1：编写导出强校验和审计写入失败测试。
- [x] 步骤 2：实现审计服务和数据库导出流程。
- [x] 步骤 3：改造 export/audit 路由。
- [x] 步骤 4：运行测试和 Docker API 验证。
- [x] 步骤 5：提交，提交信息为 `feat: add database backed export and audit APIs`。

## 任务 16：最终 Docker 主流程验证与文档

- [x] 步骤 1：运行 `docker compose run --rm backend python -m unittest discover -s tests`。
- [x] 步骤 2：运行 `docker compose run --rm backend python -m compileall app tests`。
- [x] 步骤 3：运行数据库迁移、初始化、处理任务、审核和导出冒烟验证。
- [x] 步骤 4：更新 README 和 todo。
- [x] 步骤 5：提交，提交信息为 `docs: document database driven API flow`。
