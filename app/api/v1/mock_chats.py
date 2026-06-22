from app.api.deps import CurrentUser, get_current_user

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    from app.db.session import get_db
    from app.models.mock_chat import MockChat
    from app.schemas import ManualMockChatCreateRequest
    from app.services.db_serializers import serialize_mock_chat, serialize_process_task
    from app.services.manual_mock_chat_service import build_manual_mock_chat_values
    from app.services.task_service import create_process_task
    from app.workers.tasks import process_mock_chat_task

    router = APIRouter(prefix="/mock-chats", tags=["mock-chats"])

    @router.get("")
    def list_mock_chats(
        _current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> list[dict]:
        chats = db.query(MockChat).order_by(MockChat.mock_chat_id).all()
        return [serialize_mock_chat(chat) for chat in chats]

    @router.post("")
    def create_mock_chat(
        request: ManualMockChatCreateRequest,
        _current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        try:
            values = build_manual_mock_chat_values(request.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        exists = db.query(MockChat).filter(MockChat.mock_chat_id == values["mock_chat_id"]).first()
        if exists is not None:
            raise HTTPException(status_code=409, detail="Mock chat id already exists")

        chat = MockChat(**values)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return serialize_mock_chat(chat)

    @router.get("/{mock_chat_id}")
    def get_mock_chat(
        mock_chat_id: str,
        _current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        chat = db.query(MockChat).filter(MockChat.mock_chat_id == mock_chat_id).first()
        if chat is None:
            raise HTTPException(status_code=404, detail="Mock chat not found")
        return serialize_mock_chat(chat)

    @router.post("/{mock_chat_id}/process")
    def trigger_process(
        mock_chat_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        chat = db.query(MockChat).filter(MockChat.mock_chat_id == mock_chat_id).first()
        if chat is None:
            raise HTTPException(status_code=404, detail="Mock chat not found")

        task = create_process_task(db, chat, current_user.id or current_user.username)
        process_mock_chat_task.delay(str(task.id))
        db.refresh(task)
        return serialize_process_task(task)
