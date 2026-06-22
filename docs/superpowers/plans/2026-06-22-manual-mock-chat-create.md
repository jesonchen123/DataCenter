# 自定义 Mock 聊天记录创建接口实施计划

> **给 agent 工作者的说明：** 必须使用 `superpowers:executing-plans` 按任务逐项实施本计划。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** 新增开发态 `POST /api/v1/mock-chats`，允许手动新增原始聊天记录并复用现有处理链路。

**架构：** 纯服务负责请求数据标准化和基础校验；API 路由负责重复检查、写入 PostgreSQL 和序列化返回。

**技术栈：** Python 3.12、FastAPI、Pydantic、SQLAlchemy、PostgreSQL、unittest、Docker Compose。

## 全局约束

- 新增文档和 todo 使用中文。
- 不提交 `.env`。
- 不接入真实微信或 QQ。
- 保持现有处理接口路径不变。

---

## 任务 23：自定义 Mock 聊天记录创建接口

**文件：**
- 创建：`app/services/manual_mock_chat_service.py`
- 创建：`tests/test_manual_mock_chat_service.py`
- 修改：`app/schemas/__init__.py`
- 修改：`app/api/v1/mock_chats.py`
- 修改：`README.md`
- 修改：`todo.md`

**接口：**
- 产出：`build_manual_mock_chat_values(payload: dict) -> dict`
- 新增：`POST /api/v1/mock-chats`

- [ ] 步骤 1：编写失败测试，验证手动聊天请求会被转换为 `mock_chats` 入库字段。
- [ ] 步骤 2：编写失败测试，验证空消息列表和非法 `sender_role` 会报错。
- [ ] 步骤 3：运行 `python -m unittest tests.test_manual_mock_chat_service`，确认失败。
- [ ] 步骤 4：实现 `manual_mock_chat_service`。
- [ ] 步骤 5：新增 Pydantic 请求 schema 和 `POST /api/v1/mock-chats` 路由。
- [ ] 步骤 6：运行 `python -m unittest tests.test_manual_mock_chat_service` 和 `python -m unittest discover -s tests`。
- [ ] 步骤 7：运行 Docker API 冒烟，验证创建、自定义记录查询、触发处理。
- [ ] 步骤 8：更新 README 和 todo。
- [ ] 步骤 9：提交，提交信息为 `feat: add manual mock chat creation API`。
