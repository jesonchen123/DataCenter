try:
    from fastapi import APIRouter, Depends
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    from app.db.session import get_db
    from app.services.db_serializers import serialize_process_task
    from app.services.task_service import get_process_task_or_404

    router = APIRouter(prefix="/process-tasks", tags=["process-tasks"])

    @router.get("/{process_task_id}")
    def get_process_task(process_task_id: str, db=Depends(get_db)) -> dict:
        return serialize_process_task(get_process_task_or_404(db, process_task_id))
