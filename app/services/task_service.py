from datetime import UTC, datetime
from uuid import UUID


def create_process_task(db, mock_chat, triggered_by: str):
    from app.models.process_task import ProcessTask

    task = ProcessTask(
        task_no=f"task_{mock_chat.mock_chat_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}",
        mock_chat_id=mock_chat.id,
        triggered_by=_resolve_user_id(db, triggered_by),
        status="pending",
        current_step="queued",
        progress=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_process_task_or_404(db, process_task_id: str):
    from fastapi import HTTPException
    from app.models.process_task import ProcessTask

    try:
        task_id = UUID(str(process_task_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Process task not found")

    task = db.query(ProcessTask).filter(ProcessTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Process task not found")
    return task


def _resolve_user_id(db, user_hint: str):
    from app.models.user import User

    try:
        return UUID(str(user_hint))
    except ValueError:
        pass

    user = db.query(User).filter(User.username == user_hint).first()
    if user is not None:
        return user.id

    manager = db.query(User).filter(User.username == "manager").first()
    if manager is not None:
        return manager.id

    raise ValueError("No valid user found for process task trigger")


def resolve_user_id(db, user_hint: str):
    return _resolve_user_id(db, user_hint)
