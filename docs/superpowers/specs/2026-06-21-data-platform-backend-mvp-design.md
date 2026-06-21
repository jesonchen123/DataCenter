# Data Platform Backend MVP Design

## Scope

Build the first backend slice of the data middle platform. This slice includes the complete backend skeleton and the core data-processing flow, but does not include a frontend.

The MVP uses built-in Mock chat data only. It does not integrate real WeChat, QQ, object storage, Elasticsearch, MongoDB, vector databases, or local files for exported business data.

## Architecture

The backend is a FastAPI monolith with a Celery worker for asynchronous processing. PostgreSQL is the only long-term business data store. Redis is used only as Celery broker and result backend.

Business data is stored in PostgreSQL tables for users, Mock chats, process tasks, dialogue segments, knowledge documents, export tasks, audit logs, and LLM call logs. JSONB is used for semi-structured payloads such as raw Mock content, tags, question examples, export content, audit detail, and LLM payloads.

## Roles And Permissions

The first version implements two roles:

- `manager`: full access, including audit logs, review approval, user management, and export.
- `normal_user`: can view Mock data and processed/desensitized results, edit candidate knowledge docs, submit review, and view own submission status.

Only managers can approve knowledge docs and export RAG JSON. Normal users cannot export, approve, view audit logs, manage users, or delete system data.

## Processing Flow

The main flow is:

1. Seed PostgreSQL with default users and at least 20 Mock chat records.
2. User triggers processing for a Mock chat.
3. API creates a `process_tasks` row.
4. Celery runs the processing pipeline.
5. Pipeline parses messages, performs text cleaning, desensitization, price filtering, segmentation, deterministic knowledge generation, and quality scoring.
6. Pipeline writes `dialogue_segments` and `knowledge_docs`.
7. User edits or submits generated knowledge docs.
8. Manager reviews and approves or rejects docs.
9. Manager exports approved docs to `export_tasks.export_content`.

The first version keeps the LLM boundary but uses deterministic generation. `llm_call_logs` exists for later replacement with real model calls.

## Price Filtering

Price filtering is a first-class service. It runs before knowledge document generation and again during export validation.

The service must detect amounts, quotations, discounts, preferential prices, package prices, payment deposits, commissions, rebates, contract amounts, and payment terms. The exported JSON must not contain original prices, discounts, payment terms, rebates, commissions, or contract amounts.

Conversations with only customer price intent are `medium` risk. Conversations containing staff quotation, discount commitment, contract amount, rebate, commission, deposit, or payment term are `high` risk. High-risk docs cannot be exported unless approved by a manager.

## Export Rules

Exported JSON is stored in PostgreSQL, not written to local files. Export validation requires:

- requester role is `manager`
- `review_status` is `approved`
- `is_desensitized` is `true`
- `price_filtered` is `true`
- `contains_original_price` is `false`
- high-risk data has manager approval

The exported content contains `security.price_filtered`, `security.contains_price_intent`, and `security.contains_original_price`.

## Testing

Implementation follows test-first development. Core pure-Python services use standard-library `unittest` so they can run before third-party dependencies are installed. API, ORM, and Celery integration tests are added once dependencies are available through Docker or local installation.

Priority test coverage:

- price detection and filtering
- desensitization
- export validation
- role permission checks
- deterministic knowledge generation
- processing pipeline orchestration

## Out Of Scope

- Frontend pages
- Real WeChat or QQ import
- Real LLM generation
- Local JSON export files
- Object storage
- Vector database or RAG retrieval test UI
- Elasticsearch or MongoDB
