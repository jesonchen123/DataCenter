from app.api.deps import CurrentUser, get_current_user
from app.core.permissions import can_view_audit_logs

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])

    @router.get("")
    def list_audit_logs(current_user: CurrentUser = Depends(get_current_user)) -> list[dict]:
        if not can_view_audit_logs(current_user.role):
            raise HTTPException(status_code=403, detail="Only managers can view audit logs")
        return []
