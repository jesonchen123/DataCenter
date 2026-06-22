from app.api.deps import CurrentUser, get_current_user
from app.core.permissions import can_export
from app.schemas import ExportRequest

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    from uuid import UUID

    from app.db.session import get_db
    from app.models.export_task import ExportTask
    from app.models.knowledge_doc import KnowledgeDoc
    from app.services.audit_service import write_audit_log
    from app.services.db_serializers import serialize_export_task, serialize_export_task_content
    from app.services.export_service import create_export_task as create_export_task_record
    from app.services.task_service import resolve_user_id

    router = APIRouter(prefix="/export-tasks", tags=["export-tasks"])

    @router.post("")
    def create_export_task(
        payload: ExportRequest,
        current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        if not can_export(current_user.role):
            raise HTTPException(status_code=403, detail="Only managers can export data")
        if not payload.knowledge_doc_ids:
            raise HTTPException(status_code=400, detail="knowledge_doc_ids is required")

        try:
            doc_ids = [UUID(str(doc_id)) for doc_id in payload.knowledge_doc_ids]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid knowledge document id")

        docs = db.query(KnowledgeDoc).filter(KnowledgeDoc.id.in_(doc_ids)).all()
        if len(docs) != len(doc_ids):
            raise HTTPException(status_code=404, detail="Knowledge document not found")

        user_id = resolve_user_id(db, current_user.id or current_user.username)
        try:
            task = create_export_task_record(db, docs, user_id)
        except (PermissionError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        write_audit_log(
            db,
            user_id=user_id,
            action="export_create",
            target_type="export_task",
            target_id=task.export_no,
            detail={"document_count": task.document_count},
        )
        db.commit()
        db.refresh(task)
        return serialize_export_task(task)

    @router.get("/{export_task_id}/content")
    def get_export_content(
        export_task_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        if not can_export(current_user.role):
            raise HTTPException(status_code=403, detail="Only managers can view export content")
        try:
            task_id = UUID(str(export_task_id))
        except ValueError:
            raise HTTPException(status_code=404, detail="Export task not found")
        task = db.query(ExportTask).filter(ExportTask.id == task_id).first()
        if task is None:
            raise HTTPException(status_code=404, detail="Export task not found")
        return serialize_export_task_content(task)
