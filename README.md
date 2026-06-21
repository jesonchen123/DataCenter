# Data Platform Backend MVP

Backend MVP for a data middle platform that turns built-in Mock customer chats into reviewed, price-filtered RAG knowledge JSON.

## Scope

- FastAPI backend skeleton.
- PostgreSQL as the only long-term business database.
- Redis only for Celery queueing.
- Built-in Mock data only.
- Two roles: `manager` and `normal_user`.
- No frontend in this phase.

## Local Test

The dependency-free service tests run with the Python standard library:

```bash
python -m unittest discover -s tests
```

Full API and database integration requires installing `requirements.txt` or using Docker Compose.

## Local Development

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
```

Run migrations:

```bash
alembic upgrade head
```

Seed default users and Mock chats:

```bash
python -m app.db.init_db
```

Default development users:

- `manager / 123456`
- `user / 123456`

Start the API:

```bash
uvicorn app.main:app --reload
```

Start the Celery worker:

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
```

Or start the full backend stack:

```bash
docker compose up --build
```

## Docker Workflow

The Dockerfile uses the Tsinghua PyPI mirror by default to avoid slow downloads from `files.pythonhosted.org`. Override it when needed:

```bash
docker compose build --build-arg PIP_INDEX_URL=https://pypi.org/simple
```

Build and run tests in Docker:

```bash
docker compose build
docker compose run --rm backend python -m unittest discover -s tests
docker compose run --rm backend python -m compileall app tests
```

Run database migrations and seed data in Docker:

```bash
docker compose up -d postgres redis
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.db.init_db
```

Start the API and worker:

```bash
docker compose up -d backend celery_worker
```

Health check:

```bash
curl http://localhost:8000/health
```

## API Surface

- `GET /health`
- `POST /api/v1/auth/login`
- `GET /api/v1/mock-chats`
- `GET /api/v1/mock-chats/{mock_chat_id}`
- `POST /api/v1/mock-chats/{mock_chat_id}/process`
- `GET /api/v1/process-tasks/{process_task_id}`
- `GET /api/v1/knowledge-docs`
- `PATCH /api/v1/knowledge-docs/{knowledge_doc_id}`
- `POST /api/v1/knowledge-docs/{knowledge_doc_id}/submit-review`
- `POST /api/v1/knowledge-docs/{knowledge_doc_id}/review`
- `POST /api/v1/export-tasks`
- `GET /api/v1/export-tasks/{export_task_id}/content`
- `GET /api/v1/audit-logs`

For local development before JWT auth is finalized, protected routes read role information from headers:

- `x-user-id`
- `x-username`
- `x-role`, either `manager` or `normal_user`

## Verification Notes

The pure service layer is covered by standard-library `unittest`; dependency-backed API/database smoke checks can be run after `pip install -r requirements.txt` or inside Docker.
