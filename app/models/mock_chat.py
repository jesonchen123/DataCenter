from sqlalchemy import DateTime, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MockChat(Base):
    __tablename__ = "mock_chats"
    __table_args__ = (
        Index("idx_mock_chats_source_platform", "source_platform"),
        Index("idx_mock_chats_scenario_type", "scenario_type"),
        Index("idx_mock_chats_raw_content_gin", "raw_content", postgresql_using="gin"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    mock_chat_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    business_line: Mapped[str | None] = mapped_column(String(100))
    product_name: Mapped[str | None] = mapped_column(String(100))
    scenario_type: Mapped[str | None] = mapped_column(String(100))
    raw_content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
