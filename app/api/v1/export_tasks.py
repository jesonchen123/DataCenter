from app.api.deps import CurrentUser, get_current_user
from app.core.permissions import can_export
from app.schemas import ExportRequest

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    router = APIRouter(prefix="/export-tasks", tags=["export-tasks"])

    @router.post("")
    def create_export_task(
        payload: ExportRequest,
        current_user: CurrentUser = Depends(get_current_user),
    ) -> dict:
        if not can_export(current_user.role):
            raise HTTPException(status_code=403, detail="Only managers can export data")
        return {
            "export_no": "export_pending",
            "status": "pending",
            "document_count": len(payload.knowledge_doc_ids),
            "created_by": current_user.id,
        }

    @router.get("/{export_task_id}/content")
    def get_export_content(export_task_id: str, current_user: CurrentUser = Depends(get_current_user)) -> dict:
        if not can_export(current_user.role):
            raise HTTPException(status_code=403, detail="Only managers can view export content")
        return {"id": export_task_id, "export_content": None}
