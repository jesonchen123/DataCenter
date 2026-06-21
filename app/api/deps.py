from dataclasses import dataclass

try:
    from fastapi import Header
except ModuleNotFoundError:  # pragma: no cover
    Header = None

from app.domain.enums import Role


@dataclass(frozen=True)
class CurrentUser:
    id: str
    username: str
    role: str


def get_current_user(
    x_user_id: str = "dev-user",
    x_username: str = "dev",
    x_role: str = Role.MANAGER.value,
) -> CurrentUser:
    return CurrentUser(id=x_user_id, username=x_username, role=x_role)


if Header is not None:

    def get_current_user(
        x_user_id: str = Header(default="dev-user"),
        x_username: str = Header(default="dev"),
        x_role: str = Header(default=Role.MANAGER.value),
    ) -> CurrentUser:
        return CurrentUser(id=x_user_id, username=x_username, role=x_role)
