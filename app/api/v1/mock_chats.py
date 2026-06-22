from app.api.deps import CurrentUser, get_current_user

try:
    from fastapi import APIRouter, Depends, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    router = None
else:
    from uuid import uuid4

    from fastapi import File, Form, UploadFile

    from app.db.session import get_db
    from app.models.mock_chat import MockChat
    from app.services.db_serializers import serialize_mock_chat, serialize_process_task
    from app.services.document_import_service import (
        build_document_chat_values,
        extract_text,
        normalize_messages,
    )
    from app.services.task_service import create_process_task
    from app.workers.tasks import process_mock_chat_task

    router = APIRouter(prefix="/mock-chats", tags=["mock-chats"])

    _ALLOWED_EXTENSIONS = {".json", ".docx", ".txt"}

    def _validate_file_extension(filename: str) -> None:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if f".{ext}" not in _ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '.{ext}'. Allowed: .json, .docx, .txt",
            )

    @router.get("")
    def list_mock_chats(
        _current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> list[dict]:
        chats = db.query(MockChat).order_by(MockChat.mock_chat_id).all()
        return [serialize_mock_chat(chat) for chat in chats]

    @router.post("/upload", status_code=201)
    async def upload_document(
        file: UploadFile = File(...),
        mock_chat_id: str | None = Form(None),
        source_platform: str | None = Form(None),
        business_line: str | None = Form(None),
        product_name: str | None = Form(None),
        scenario_type: str | None = Form(None),
        _current_user: CurrentUser = Depends(get_current_user),
        db=Depends(get_db),
    ) -> dict:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is required.")

        _validate_file_extension(file.filename)

        try:
            raw_bytes = await file.read()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}") from exc

        if not raw_bytes:
            raise HTTPException(status_code=400, detail="File is empty.")

        if len(raw_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File exceeds 10 MB limit.")

        try:
            raw_text = extract_text(raw_bytes, file.filename)
            messages, normalizer = normalize_messages(raw_text)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ImportError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        generated_id = mock_chat_id or f"doc_{uuid4().hex[:12]}"
        values = build_document_chat_values(messages, {
            "mock_chat_id": generated_id,
            "source_platform": source_platform,
            "business_line": business_line,
            "product_name": product_name,
            "scenario_type": scenario_type,
        })

        exists = db.query(MockChat).filter(
            MockChat.mock_chat_id == values["mock_chat_id"]
        ).first()
        if exists is not None:
            raise HTTPException(status_code=409, detail="Mock chat id already exists")

        chat = MockChat(**values)
        db.add(chat)
        db.commit()
        db.refresh(chat)

        result = serialize_mock_chat(chat)
        result["normalizer"] = normalizer
        return result

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
