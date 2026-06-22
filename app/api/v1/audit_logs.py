from app.api.deps import CurrentUser, get_current_user
from app.core.permissions import can_view_audit_logs

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    from app.db.session import get_db
    from app.models.audit_log import AuditLog
    from app.services.db_serializers import serialize_audit_log

    router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])

    @router.get("")
    def list_audit_logs(current_user: CurrentUser = Depends(get_current_user), db=Depends(get_db)) -> list[dict]:
        if not can_view_audit_logs(current_user.role):
            raise HTTPException(status_code=403, detail="Only managers can view audit logs")
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
        return [serialize_audit_log(log) for log in logs]
