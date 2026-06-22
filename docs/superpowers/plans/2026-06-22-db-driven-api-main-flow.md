# 数据库驱动 API 主流程实施计划

> **给 agent 工作者的说明：** 必须使用 `superpowers:executing-plans` 按任务逐项实施本计划。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** 把当前占位 API 改造成围绕 PostgreSQL 和 Celery 流转的后端主流程。

**架构：** API 路由通过 `Depends(get_db)` 访问 PostgreSQL，服务层封装任务、持久化、审核、导出和审计逻辑。Celery 任务运行现有处理流水线，并把结果写入 `dialogue_segments` 与 `knowledge_docs`。

**技术栈：** Python 3.12、FastAPI、SQLAlchemy、Alembic、PostgreSQL、Celery、Redis、unittest、Docker Compose。

## 全局约束

- 保持现有 API 路径不变。
- 当前用户继续使用开发态 header，不在本阶段实现正式 JWT。
- PostgreSQL 是唯一业务数据存储。
- Redis 只用于 Celery。
- 导出 JSON 只存入 `export_tasks.export_content`。
- 任何包含原始价格的知识文档不能导出。
- 新增计划和 todo 必须使用中文。

---

## 任务 11：数据库序列化与任务服务

**文件：**
- 创建：`app/services/db_serializers.py`
- 创建：`app/services/task_service.py`
- 创建：`tests/test_db_serializers.py`
- 修改：`app/api/v1/process_tasks.py`

**接口：**
- 产出：`serialize_mock_chat(chat) -> dict`
- 产出：`serialize_process_task(task) -> dict`
- 产出：`create_process_task(db, mock_chat, triggered_by: str)`
- 产出：`get_process_task_or_404(db, process_task_id: str)`

- [ ] 步骤 1：先写序列化失败测试。
- [ ] 步骤 2：运行 `python -m unittest tests.test_db_serializers`，确认失败。
- [ ] 步骤 3：实现序列化和任务服务。
- [ ] 步骤 4：运行 `python -m unittest tests.test_db_serializers`，确认通过。
- [ ] 步骤 5：提交，提交信息为 `feat: add database task services`。

## 任务 12：Mock 数据 API 读写 PostgreSQL

**文件：**
- 修改：`app/api/v1/mock_chats.py`
- 修改：`app/api/v1/process_tasks.py`

**接口：**
- `GET /api/v1/mock-chats` 从 `mock_chats` 表读取。
- `GET /api/v1/mock-chats/{mock_chat_id}` 从 `mock_chats` 表读取。
- `POST /api/v1/mock-chats/{mock_chat_id}/process` 创建 `process_tasks` 并触发 Celery。
- `GET /api/v1/process-tasks/{process_task_id}` 返回真实任务状态。

- [ ] 步骤 1：编写容器内 API 冒烟脚本，验证当前接口仍返回占位数据。
- [ ] 步骤 2：改造路由使用 `get_db` 和任务服务。
- [ ] 步骤 3：运行 Docker 容器内测试和接口冒烟检查。
- [ ] 步骤 4：提交，提交信息为 `feat: drive mock chat APIs from database`。

## 任务 13：处理结果持久化

**文件：**
- 创建：`app/services/persistence_service.py`
- 修改：`app/workers/tasks.py`
- 创建：`tests/test_persistence_service.py`

**接口：**
- 产出：`persist_pipeline_result(db, task, result: dict) -> dict`
- Celery 任务写入 `dialogue_segments` 和 `knowledge_docs`。

- [ ] 步骤 1：编写失败测试，验证流水线结果会转换为待持久化结构。
- [ ] 步骤 2：运行 `python -m unittest tests.test_persistence_service`，确认失败。
- [ ] 步骤 3：实现持久化服务并接入 worker。
- [ ] 步骤 4：运行单元测试和 Docker 数据库验证。
- [ ] 步骤 5：提交，提交信息为 `feat: persist processing results`。

## 任务 14：知识文档审核 API 落库

**文件：**
- 创建：`app/services/review_service.py`
- 修改：`app/api/v1/knowledge_docs.py`

**接口：**
- `GET /api/v1/knowledge-docs` 查询数据库。
- `PATCH /api/v1/knowledge-docs/{id}` 更新候选文档。
- `POST /api/v1/knowledge-docs/{id}/submit-review` 提交审核。
- `POST /api/v1/knowledge-docs/{id}/review` 仅 manager 可审核。

- [ ] 步骤 1：编写服务层失败测试。
- [ ] 步骤 2：实现 review service。
- [ ] 步骤 3：改造 knowledge docs 路由。
- [ ] 步骤 4：运行测试和 Docker API 验证。
- [ ] 步骤 5：提交，提交信息为 `feat: add database backed review APIs`。

## 任务 15：导出与审计 API 落库

**文件：**
- 创建：`app/services/audit_service.py`
- 修改：`app/services/export_service.py`
- 修改：`app/api/v1/export_tasks.py`
- 修改：`app/api/v1/audit_logs.py`

**接口：**
- `POST /api/v1/export-tasks` 从已审核知识文档构建并保存导出内容。
- `GET /api/v1/export-tasks/{id}/content` 从数据库返回导出内容。
- `GET /api/v1/audit-logs` 从数据库返回审计日志。

- [ ] 步骤 1：编写导出强校验和审计写入失败测试。
- [ ] 步骤 2：实现审计服务和数据库导出流程。
- [ ] 步骤 3：改造 export/audit 路由。
- [ ] 步骤 4：运行测试和 Docker API 验证。
- [ ] 步骤 5：提交，提交信息为 `feat: add database backed export and audit APIs`。

## 任务 16：最终 Docker 主流程验证与文档

**文件：**
- 修改：`README.md`
- 修改：`todo.md`

**接口：**
- 文档记录完整 Docker 主流程命令。

- [ ] 步骤 1：运行 `docker compose run --rm backend python -m unittest discover -s tests`。
- [ ] 步骤 2：运行 `docker compose run --rm backend python -m compileall app tests`。
- [ ] 步骤 3：运行数据库迁移、初始化、处理任务、审核和导出冒烟验证。
- [ ] 步骤 4：更新 README 和 todo。
- [ ] 步骤 5：提交，提交信息为 `docs: document database driven API flow`。
