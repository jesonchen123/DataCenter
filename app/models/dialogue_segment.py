from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DialogueSegment(Base):
    __tablename__ = "dialogue_segments"
    __table_args__ = (
        Index("idx_dialogue_segments_task_id", "process_task_id"),
        Index("idx_dialogue_segments_mock_chat_id", "mock_chat_id"),
        Index("idx_dialogue_segments_price_risk", "price_risk_level"),
        Index("idx_dialogue_segments_contains_price", "contains_price_info"),
        Index("idx_dialogue_segments_tags_gin", "tags", postgresql_using="gin"),
        Index("idx_dialogue_segments_scenario_type", "scenario_type"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    segment_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    process_task_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("process_tasks.id"), nullable=False)
    mock_chat_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("mock_chats.id"), nullable=False)
    original_content: Mapped[str | None] = mapped_column(Text)
    cleaned_content: Mapped[str | None] = mapped_column(Text)
    desensitized_content: Mapped[str | None] = mapped_column(Text)
    price_filtered_content: Mapped[str | None] = mapped_column(Text)
    customer_question: Mapped[str | None] = mapped_column(Text)
    staff_answer: Mapped[str | None] = mapped_column(Text)
    business_line: Mapped[str | None] = mapped_column(String(100))
    product_name: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list | None] = mapped_column(JSONB)
    scenario_type: Mapped[str | None] = mapped_column(String(100))
    contains_sensitive_info: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    contains_price_info: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    price_filter_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pending")
    price_risk_level: Mapped[str] = mapped_column(String(50), nullable=False, server_default="none")
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="generated")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
