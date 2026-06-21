from app.domain.enums import Role
from app.schemas import LoginRequest, LoginResponse

try:
    from fastapi import APIRouter, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/login", response_model=LoginResponse)
    def login(payload: LoginRequest) -> LoginResponse:
        if payload.username == "manager" and payload.password == "123456":
            return LoginResponse(access_token="dev-manager-token", role=Role.MANAGER.value)
        if payload.username == "user" and payload.password == "123456":
            return LoginResponse(access_token="dev-user-token", role=Role.NORMAL_USER.value)
        raise HTTPException(status_code=401, detail="Invalid username or password")
