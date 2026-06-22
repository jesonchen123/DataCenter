from app.services.processing_pipeline import process_mock_chat_payload
from app.services.persistence_service import persist_pipeline_result
from app.services.llm_knowledge_service import generate_knowledge_doc_with_llm
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
        result = process_mock_chat_payload(
            chat.raw_content,
            knowledge_generator=lambda segment: generate_knowledge_doc_with_llm(
                segment,
                db=db,
                related_type="process_task",
                related_id=task.id,
            ),
        )
        persist_pipeline_result(db, task, result)
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
