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

    return api


app = create_app() if FastAPI is not None else None
