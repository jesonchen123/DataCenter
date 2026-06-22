def build_audit_log_values(
    user_id,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    return {
        "user_id": user_id,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "detail": detail or {},
        "ip_address": ip_address,
        "user_agent": user_agent,
    }


def write_audit_log(
    db,
    user_id,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail: dict | None = None,
):
    from app.models.audit_log import AuditLog

    log = AuditLog(
        **build_audit_log_values(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )
    )
    db.add(log)
    return log
