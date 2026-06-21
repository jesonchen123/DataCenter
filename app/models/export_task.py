from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExportTask(Base):
    __tablename__ = "export_tasks"
    __table_args__ = (
        Index("idx_export_tasks_created_by", "created_by"),
        Index("idx_export_tasks_status", "status"),
        Index("idx_export_tasks_created_at", "created_at"),
        Index("idx_export_tasks_content_gin", "export_content", postgresql_using="gin"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    export_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    export_type: Mapped[str] = mapped_column(String(100), nullable=False)
    filters: Mapped[dict | None] = mapped_column(JSONB)
    export_content: Mapped[dict | None] = mapped_column(JSONB)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = mapped_column(DateTime(timezone=True))
