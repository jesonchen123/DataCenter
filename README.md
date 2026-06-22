# Data Platform Backend MVP

Backend MVP for a data middle platform that imports customer chat documents (JSON/Word/TXT), processes them through a cleaning and LLM pipeline, and exports reviewed, price-filtered RAG knowledge JSON.

## Scope

- FastAPI backend skeleton.
- PostgreSQL as the only long-term business database.
- Redis only for Celery queueing.
- Document import via file upload (`.json`, `.docx`, `.txt`).
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

Seed default users:

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

Real LLM credentials must be stored in `.env` or deployment environment variables. Keep `.env.example` as placeholders only, because it is tracked by Git.

For OpenAI-compatible providers, configure:

```powershell
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_real_key
LLM_MODEL_NAME=gpt-4o-mini
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=60
```

Docker Compose reads these LLM values from `.env` automatically and passes them to `backend` and `celery_worker`. If `.env` is absent or `LLM_API_KEY` is still `your_api_key`, processing safely falls back to deterministic knowledge generation and writes a failed `llm_call_logs` row.

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

## Docker 数据库驱动主流程

完整启动后，PostgreSQL 和 Redis 都运行在 Docker 容器中，业务数据写入 `postgres_data` volume。PostgreSQL 已映射到宿主机 `5432`，可以用本地数据库客户端连接。

启动和初始化：

```powershell
docker compose build
docker compose up -d postgres redis
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.db.init_db
docker compose up -d backend celery_worker
```

容器内验证：

```powershell
docker compose run --rm backend python -m unittest discover -s tests
docker compose run --rm backend python -m compileall app tests
```

API 主流程冒烟验证示例（先上传文件再处理）：

```powershell
$headersUser = @{ 'x-username' = 'normal_user'; 'x-role' = 'normal_user' }
$headersManager = @{ 'x-username' = 'manager'; 'x-role' = 'manager' }

# Step 1: Create a test JSON file and upload it
$tempJson = @'
[
  {"role":"customer","text":"这个产品怎么使用？","sender":"客户A"},
  {"role":"staff","text":"先确认使用场景，然后说明产品能力。","sender":"销售B"}
]
'@
$tempFile = New-TemporaryFile | Rename-Item -PassThru -NewName { $_.Name + '.json' }
Set-Content -Path $tempFile -Value $tempJson -Encoding UTF8

$upload = Invoke-RestMethod -Method Post -Form @{
  file = Get-Item -Path $tempFile
  mock_chat_id = 'smoke_test_001'
} -Headers $headersUser `
  http://localhost:8000/api/v1/mock-chats/upload

# Step 2: Trigger processing
$process = Invoke-RestMethod -Method Post -Headers $headersUser `
  http://localhost:8000/api/v1/mock-chats/smoke_test_001/process

do {
  Start-Sleep -Seconds 1
  $task = Invoke-RestMethod -Headers $headersUser `
    "http://localhost:8000/api/v1/process-tasks/$($process.id)"
} while ($task.status -eq 'pending' -or $task.status -eq 'processing')

# Step 3: Review the generated knowledge doc
$docsRaw = Invoke-RestMethod -Headers $headersManager `
  http://localhost:8000/api/v1/knowledge-docs
$docs = @()
foreach ($item in $docsRaw) { $docs += $item }

$doc = $docs | Sort-Object { [DateTime]$_.created_at } -Descending | Select-Object -First 1
if ($doc.review_status -ne 'pending_review') {
  $doc = Invoke-RestMethod -Method Post -Headers $headersUser `
    "http://localhost:8000/api/v1/knowledge-docs/$($doc.id)/submit-review"
}

$doc = Invoke-RestMethod -Method Post -ContentType 'application/json' `
  -Body '{"approved":true,"review_comment":"smoke"}' `
  -Headers $headersManager `
  "http://localhost:8000/api/v1/knowledge-docs/$($doc.id)/review"

# Step 4: Export and verify
$body = @{ knowledge_doc_ids = @($doc.id) } | ConvertTo-Json
$export = Invoke-RestMethod -Method Post -ContentType 'application/json' `
  -Body $body `
  -Headers $headersManager `
  http://localhost:8000/api/v1/export-tasks

Invoke-RestMethod -Headers $headersManager `
  "http://localhost:8000/api/v1/export-tasks/$($export.id)/content"

Invoke-RestMethod -Headers $headersManager `
  http://localhost:8000/api/v1/audit-logs
```

`GET /api/v1/export-tasks/{export_task_id}/content` returns only QA document content:

```json
{
  "documents": [
    {
      "content": "客户问：产品怎么使用？\n销售答：先登录后台再创建知识库。"
    }
  ]
}
```

## Document Import

Import customer chat data by uploading `.json`, `.docx`, or `.txt` files. The API auto-detects the format and normalizes content to the standard internal message structure.

### Upload a document

```powershell
$headersUser = @{ 'x-username' = 'normal_user'; 'x-role' = 'normal_user' }

# Upload a JSON message array
$result = Invoke-RestMethod -Method Post -Form @{
  file = Get-Item -Path '.\chat_data.json'
  mock_chat_id = 'import_001'
  business_line = '测试业务线'
  product_name = '测试产品'
  scenario_type = 'price_consulting'
} -Headers $headersUser `
  http://localhost:8000/api/v1/mock-chats/upload

Write-Host "normalizer: $($result.normalizer)"

# Trigger processing on the imported chat
Invoke-RestMethod -Method Post -Headers $headersUser `
  http://localhost:8000/api/v1/mock-chats/import_001/process
```

### Supported file formats

**JSON** (`.json`): Message array `[{"role":"customer","text":"...","sender":"..."}, ...]`. Also accepts `{"messages": [...]}` wrapper. `role` must be `customer`, `staff`, or `system`.

**TXT** (`.txt`): Line-based conversation with role prefixes:
```
客户：这个产品怎么使用？
销售：可以先确认使用场景，然后说明产品能力。
```

**Word** (`.docx`): Paragraphs extracted from the document, parsed as role-prefixed conversation. Requires `python-docx`.

When LLM is configured, unstructured text formats are normalized via AI for best results. The API response includes a `normalizer` field indicating which strategy was used: `"json_direct"`, `"llm"`, or `"rule"`.

Check LLM call logs:

```powershell
docker compose exec -T postgres psql -U postgres -d chat_data_platform `
  -c "select status, model_name, error_message, related_type, related_id from llm_call_logs order by created_at desc limit 5;"
```

## API Surface

- `GET /health`
- `POST /api/v1/auth/login`
- `GET /api/v1/mock-chats`
- `POST /api/v1/mock-chats/upload`
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
