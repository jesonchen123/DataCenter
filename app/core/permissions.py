from app.domain.enums import Role


def _is_manager(role: str) -> bool:
    return role == Role.MANAGER.value


def can_export(role: str) -> bool:
    return _is_manager(role)


def can_approve(role: str) -> bool:
    return _is_manager(role)


def can_view_audit_logs(role: str) -> bool:
    return _is_manager(role)
