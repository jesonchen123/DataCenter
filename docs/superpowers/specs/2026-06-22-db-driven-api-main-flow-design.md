# 数据库驱动 API 主流程设计

## 范围

本阶段把第一版后端从“可运行骨架”推进到“数据库驱动的 API 主流程”。前端、真实 JWT 登录、真实 LLM 调用仍不进入本阶段。

## 目标

- Mock 数据 API 从 PostgreSQL 的 `mock_chats` 表读取。
- 触发处理时创建真实 `process_tasks` 记录，并调用 Celery 任务。
- Celery 任务处理 Mock 聊天后，把结果写入 `dialogue_segments` 与 `knowledge_docs`。
- `process_tasks`、`knowledge_docs`、`export_tasks`、`audit_logs` API 从 PostgreSQL 读写真实数据。
- 导出仍遵守已审核、已脱敏、已价格过滤、无原始价格、高风险由管理层审核的强校验。

## 当前断点

当前 `init_db` 会把用户和 Mock 聊天写入 PostgreSQL，但 `mock_chats` API 仍直接调用 `build_mock_chats()` 返回内存数据。触发处理 API 只返回假的 pending 结果。Celery 任务可以读取 `process_tasks` 和 `mock_chats`，但只把处理结果写入 `process_tasks.step_result`，没有持久化到 `dialogue_segments` 和 `knowledge_docs`。知识文档、导出和审计 API 仍是占位返回。

## 设计

新增数据库服务层，集中封装 API 和 worker 共用的 SQLAlchemy 操作：

- `app/services/db_serializers.py`：把 ORM 对象序列化为 API dict，避免路由重复拼字段。
- `app/services/task_service.py`：创建处理任务、查询任务、写任务状态。
- `app/services/persistence_service.py`：把流水线输出持久化为 `dialogue_segments` 和 `knowledge_docs`。
- `app/services/review_service.py`：知识文档编辑、提交审核、管理层审核。
- `app/services/audit_service.py`：写入和查询审计日志。

API 路由保持现有路径不变，但改为使用 `Depends(get_db)` 注入数据库 session。当前用户仍来自开发态 header；真实 JWT 放到后续阶段。

Celery 任务改为完整落库：读取任务与 Mock 聊天，运行 `process_mock_chat_payload()`，写入片段和知识文档，更新任务状态，并记录审计日志。为方便本地和测试，本阶段 API 触发任务时直接调用 `process_mock_chat_task.delay()`；如果 Celery 不可用，则仍返回已创建的任务，worker 可手动执行。

## 测试策略

继续使用 TDD。纯业务序列化和持久化辅助逻辑尽量用 `unittest` 测。数据库/容器行为通过 Docker 命令验证：

- `docker compose run --rm backend python -m unittest discover -s tests`
- `docker compose run --rm backend alembic upgrade head`
- `docker compose run --rm backend python -m app.db.init_db`
- 使用容器内 Python 脚本调用服务层，验证任务创建、处理落库、审核和导出。

## 非目标

- 不实现正式 JWT。
- 不实现前端。
- 不接入真实 LLM。
- 不做分页、复杂筛选和全文检索。
