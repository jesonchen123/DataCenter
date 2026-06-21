# Data Platform Backend MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the FastAPI backend skeleton and core Mock-data processing flow for the first data middle platform MVP.

**Architecture:** FastAPI exposes auth, Mock chat, processing, knowledge review, export, and audit APIs. PostgreSQL is the only business data store; Redis is only for Celery. Core processing logic is implemented as pure services so it can be tested before third-party dependencies are installed.

**Tech Stack:** Python 3.12 target, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Celery, Redis, python-jose, passlib/bcrypt, pytest, unittest for dependency-free core service tests.

## Global Constraints

- First version has only two roles: `manager` and `normal_user`.
- First version does not integrate real WeChat or QQ data.
- First version uses built-in Mock data to drive the complete flow.
- All long-term business data is stored in PostgreSQL.
- Redis is only used for Celery queueing and task status cache.
- Exported JSON is stored in `export_tasks.export_content`, not local files.
- Price filtering must happen before knowledge document generation.
- Export JSON must be revalidated before storage.
- Normal users cannot export data.
- Only managers can approve and export data.
- Any knowledge document containing original prices cannot be exported.
- Frontend is out of scope for this plan.

---

## Task 1: Project Skeleton And Dependency Contract

**Files:**
- Create: `README.md`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/api/__init__.py`
- Create: `app/api/v1/__init__.py`
- Create: `app/core/__init__.py`
- Create: `app/core/config.py`
- Create: `tests/__init__.py`

**Interfaces:**
- Produces: `app.main:create_app() -> FastAPI`
- Produces: `app.core.config.Settings`

- [x] Step 1: Create dependency and environment files.
- [x] Step 2: Create app package skeleton.
- [x] Step 3: Create FastAPI app factory with health endpoint.
- [x] Step 4: Run `python -m unittest discover -s tests`.
- [x] Step 5: Commit with `chore: scaffold backend project`.

## Task 2: Core Domain Types And Permission Rules

**Files:**
- Create: `app/domain/__init__.py`
- Create: `app/domain/enums.py`
- Create: `app/core/permissions.py`
- Create: `tests/test_permissions.py`

**Interfaces:**
- Produces: `Role`, `ReviewStatus`, `RiskLevel`, `PriceFilterStatus`
- Produces: `can_export(role: str) -> bool`
- Produces: `can_approve(role: str) -> bool`
- Produces: `can_view_audit_logs(role: str) -> bool`

- [x] Step 1: Write failing permission tests for `manager` and `normal_user`.
- [x] Step 2: Run `python -m unittest tests.test_permissions`.
- [x] Step 3: Implement enums and permission helpers.
- [x] Step 4: Run `python -m unittest tests.test_permissions`.
- [x] Step 5: Commit with `feat: add role permission rules`.

## Task 3: Price Filtering Service

**Files:**
- Create: `app/services/__init__.py`
- Create: `app/services/price_filter_service.py`
- Create: `tests/test_price_filter_service.py`

**Interfaces:**
- Produces: `PriceFilterResult`
- Produces: `detect_price_info(text: str) -> PriceFilterResult`
- Produces: `filter_price_content(text: str) -> PriceFilterResult`
- Produces: `contains_original_price(text: str) -> bool`

- [x] Step 1: Write failing tests for amount, discount, preferential price, contract amount, payment term, rebate, commission, and customer price intent.
- [x] Step 2: Run `python -m unittest tests.test_price_filter_service`.
- [x] Step 3: Implement regex-based price detection and sentence filtering.
- [x] Step 4: Run `python -m unittest tests.test_price_filter_service`.
- [x] Step 5: Commit with `feat: add price filtering service`.

## Task 4: Cleaning And Desensitization Services

**Files:**
- Create: `app/services/cleaning_service.py`
- Create: `app/services/desensitization_service.py`
- Create: `tests/test_cleaning_service.py`
- Create: `tests/test_desensitization_service.py`

**Interfaces:**
- Produces: `clean_messages(messages: list[dict]) -> list[dict]`
- Produces: `normalize_text(text: str) -> str`
- Produces: `desensitize_text(text: str) -> tuple[str, bool]`

- [x] Step 1: Write failing cleaning tests for empty messages, duplicates, system prompts, simple greetings, and punctuation normalization.
- [x] Step 2: Write failing desensitization tests for phone, email, QQ, WeChat ID, order number, and ID card.
- [x] Step 3: Run `python -m unittest tests.test_cleaning_service tests.test_desensitization_service`.
- [x] Step 4: Implement cleaning and desensitization services.
- [x] Step 5: Run `python -m unittest tests.test_cleaning_service tests.test_desensitization_service`.
- [x] Step 6: Commit with `feat: add cleaning and desensitization services`.

## Task 5: Deterministic Knowledge Generation And Export Validation

**Files:**
- Create: `app/services/knowledge_service.py`
- Create: `app/services/export_service.py`
- Create: `tests/test_knowledge_service.py`
- Create: `tests/test_export_service.py`

**Interfaces:**
- Produces: `generate_knowledge_doc(segment: dict) -> dict`
- Produces: `validate_exportable(doc: dict, requester_role: str) -> None`
- Produces: `build_export_content(docs: list[dict], created_by: str) -> dict`

- [x] Step 1: Write failing tests for price-intent knowledge docs and non-price business docs.
- [x] Step 2: Write failing export validation tests for role, review status, desensitization, price filtering, original price, and high-risk approval.
- [x] Step 3: Run `python -m unittest tests.test_knowledge_service tests.test_export_service`.
- [x] Step 4: Implement deterministic knowledge generation and export validation.
- [x] Step 5: Run `python -m unittest tests.test_knowledge_service tests.test_export_service`.
- [x] Step 6: Commit with `feat: add knowledge generation and export validation`.

## Task 6: SQLAlchemy Models And Alembic Migration

**Files:**
- Create: `app/db/__init__.py`
- Create: `app/db/base.py`
- Create: `app/db/session.py`
- Create: `app/models/__init__.py`
- Create: `app/models/user.py`
- Create: `app/models/mock_chat.py`
- Create: `app/models/process_task.py`
- Create: `app/models/dialogue_segment.py`
- Create: `app/models/knowledge_doc.py`
- Create: `app/models/export_task.py`
- Create: `app/models/audit_log.py`
- Create: `app/models/llm_call_log.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/20260621_0001_init_tables.py`

**Interfaces:**
- Produces PostgreSQL tables from the technical design document.

- [x] Step 1: Create SQLAlchemy model files matching the documented PostgreSQL schema.
- [x] Step 2: Create Alembic configuration and initial migration with `pgcrypto`, tables, foreign keys, and indexes.
- [x] Step 3: Run import smoke check once dependencies are installed: `python -c "from app.models import User, MockChat, ProcessTask, DialogueSegment, KnowledgeDoc, ExportTask, AuditLog, LLMCallLog"` (deferred until dependencies are installed).
- [x] Step 4: Commit with `feat: add database models and migration`.

## Task 7: Mock Data Seeding

**Files:**
- Create: `app/db/init_db.py`
- Create: `app/services/mock_data_service.py`
- Create: `tests/test_mock_data_service.py`

**Interfaces:**
- Produces: `build_mock_chats() -> list[dict]`
- Produces: `python -m app.db.init_db`

- [ ] Step 1: Write failing tests that at least 20 Mock chats are generated and cover product consulting, after-sales, price consulting, and customer objections.
- [ ] Step 2: Run `python -m unittest tests.test_mock_data_service`.
- [ ] Step 3: Implement deterministic Mock data builder and database seeding command.
- [ ] Step 4: Run `python -m unittest tests.test_mock_data_service`.
- [ ] Step 5: Commit with `feat: add mock data seed builder`.

## Task 8: Processing Pipeline And Celery Task

**Files:**
- Create: `app/services/processing_pipeline.py`
- Create: `app/workers/__init__.py`
- Create: `app/workers/celery_app.py`
- Create: `app/workers/tasks.py`
- Create: `tests/test_processing_pipeline.py`

**Interfaces:**
- Produces: `process_mock_chat_payload(payload: dict) -> dict`
- Produces: Celery task `process_mock_chat_task(process_task_id: str) -> dict`

- [ ] Step 1: Write failing pipeline tests for parse, clean, desensitize, price filter, segment, and knowledge output.
- [ ] Step 2: Run `python -m unittest tests.test_processing_pipeline`.
- [ ] Step 3: Implement dependency-free payload pipeline.
- [ ] Step 4: Add Celery app and task wrapper for database-backed execution.
- [ ] Step 5: Run `python -m unittest tests.test_processing_pipeline`.
- [ ] Step 6: Commit with `feat: add mock chat processing pipeline`.

## Task 9: API Schemas And Routers

**Files:**
- Create: `app/schemas/__init__.py`
- Create: `app/api/v1/auth.py`
- Create: `app/api/v1/mock_chats.py`
- Create: `app/api/v1/process_tasks.py`
- Create: `app/api/v1/knowledge_docs.py`
- Create: `app/api/v1/export_tasks.py`
- Create: `app/api/v1/audit_logs.py`
- Modify: `app/main.py`

**Interfaces:**
- Produces: `/api/v1/auth/login`
- Produces: `/api/v1/mock-chats`
- Produces: `/api/v1/mock-chats/{id}`
- Produces: `/api/v1/mock-chats/{id}/process`
- Produces: `/api/v1/process-tasks/{id}`
- Produces: `/api/v1/knowledge-docs`
- Produces: `/api/v1/knowledge-docs/{id}/submit-review`
- Produces: `/api/v1/knowledge-docs/{id}/review`
- Produces: `/api/v1/export-tasks`
- Produces: `/api/v1/export-tasks/{id}/content`
- Produces: `/api/v1/audit-logs`

- [ ] Step 1: Add Pydantic schemas for request and response objects.
- [ ] Step 2: Add routers with dependency placeholders for database sessions and current user.
- [ ] Step 3: Enforce role checks in router entry points.
- [ ] Step 4: Run import smoke check once dependencies are installed.
- [ ] Step 5: Commit with `feat: add backend API routers`.

## Task 10: Final Verification And Documentation

**Files:**
- Modify: `README.md`
- Modify: `todo.md`

**Interfaces:**
- Produces documented local commands for tests, Docker, migrations, seed data, API, worker, and export.

- [ ] Step 1: Run `python -m unittest discover -s tests`.
- [ ] Step 2: Update README with local and Docker usage.
- [ ] Step 3: Mark all completed `todo.md` tasks.
- [ ] Step 4: Run `git status --short`.
- [ ] Step 5: Commit with `docs: document backend mvp usage`.
