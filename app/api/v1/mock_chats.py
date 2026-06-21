from app.api.deps import CurrentUser, get_current_user
from app.services.mock_data_service import build_mock_chats

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    router = APIRouter(prefix="/mock-chats", tags=["mock-chats"])

    @router.get("")
    def list_mock_chats(_current_user: CurrentUser = Depends(get_current_user)) -> list[dict]:
        return build_mock_chats()

    @router.get("/{mock_chat_id}")
    def get_mock_chat(mock_chat_id: str, _current_user: CurrentUser = Depends(get_current_user)) -> dict:
        for chat in build_mock_chats():
            if chat["mock_chat_id"] == mock_chat_id:
                return chat
        raise HTTPException(status_code=404, detail="Mock chat not found")

    @router.post("/{mock_chat_id}/process")
    def trigger_process(mock_chat_id: str, current_user: CurrentUser = Depends(get_current_user)) -> dict:
        return {
            "task_no": f"task_{mock_chat_id}",
            "mock_chat_id": mock_chat_id,
            "triggered_by": current_user.id,
            "status": "pending",
        }
