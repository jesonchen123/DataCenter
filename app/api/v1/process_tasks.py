try:
    from fastapi import APIRouter
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    router = APIRouter(prefix="/process-tasks", tags=["process-tasks"])

    @router.get("/{process_task_id}")
    def get_process_task(process_task_id: str) -> dict:
        return {
            "id": process_task_id,
            "task_no": process_task_id,
            "status": "pending",
            "current_step": "queued",
            "progress": 0,
        }
