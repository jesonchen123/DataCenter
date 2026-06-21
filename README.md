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
