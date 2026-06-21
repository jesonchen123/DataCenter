from app.services.processing_pipeline import process_mock_chat_payload
from app.workers.celery_app import celery_app


if celery_app is not None:

    @celery_app.task(name="process_mock_chat_task")
    def process_mock_chat_task(process_task_id: str) -> dict:
        return _process_mock_chat_task(process_task_id)

else:

    def process_mock_chat_task(process_task_id: str) -> dict:
        return _process_mock_chat_task(process_task_id)


def _process_mock_chat_task(process_task_id: str) -> dict:
    from app.db.session import SessionLocal
    from app.models.mock_chat import MockChat
    from app.models.process_task import ProcessTask

    db = SessionLocal()
    try:
        task = db.query(ProcessTask).filter(ProcessTask.id == process_task_id).one()
        chat = db.query(MockChat).filter(MockChat.id == task.mock_chat_id).one()
        result = process_mock_chat_payload(chat.raw_content)
        task.status = "success"
        task.current_step = "completed"
        task.progress = 100
        task.step_result = result
        db.commit()
        return result
    except Exception as exc:
        db.rollback()
        try:
            task.status = "failed"
            task.error_message = str(exc)
            db.commit()
        except Exception:
            db.rollback()
        raise
    finally:
        db.close()
