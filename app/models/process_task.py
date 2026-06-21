from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProcessTask(Base):
    __tablename__ = "process_tasks"
    __table_args__ = (
        Index("idx_process_tasks_mock_chat_id", "mock_chat_id"),
        Index("idx_process_tasks_triggered_by", "triggered_by"),
        Index("idx_process_tasks_status", "status"),
        Index("idx_process_tasks_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    task_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    mock_chat_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("mock_chats.id"), nullable=False)
    triggered_by: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pending")
    current_step: Mapped[str | None] = mapped_column(String(100))
    progress: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    step_result: Mapped[dict | None] = mapped_column(JSONB)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = mapped_column(DateTime(timezone=True))
