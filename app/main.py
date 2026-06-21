from app.core.config import settings

try:
    from fastapi import FastAPI
except ModuleNotFoundError:  # pragma: no cover - used only before dependencies are installed
    FastAPI = None


def create_app():
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install requirements.txt first.")

    api = FastAPI(title=settings.app_name)

    @api.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    from app.api.v1.audit_logs import router as audit_logs_router
    from app.api.v1.auth import router as auth_router
    from app.api.v1.export_tasks import router as export_tasks_router
    from app.api.v1.knowledge_docs import router as knowledge_docs_router
    from app.api.v1.mock_chats import router as mock_chats_router
    from app.api.v1.process_tasks import router as process_tasks_router

    for router in [
        auth_router,
        mock_chats_router,
        process_tasks_router,
        knowledge_docs_router,
        export_tasks_router,
        audit_logs_router,
    ]:
        api.include_router(router, prefix="/api/v1")

    return api


app = create_app() if FastAPI is not None else None
