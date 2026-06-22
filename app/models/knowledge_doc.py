from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"
    __table_args__ = (
        Index("idx_knowledge_docs_review_status", "review_status"),
        Index("idx_knowledge_docs_risk_level", "risk_level"),
        Index("idx_knowledge_docs_quality_score", "quality_score"),
        Index("idx_knowledge_docs_price_filtered", "price_filtered"),
        Index("idx_knowledge_docs_contains_original_price", "contains_original_price"),
        Index("idx_knowledge_docs_tags_gin", "tags", postgresql_using="gin"),
        Index("idx_knowledge_docs_scenario_type", "scenario_type"),
        Index("idx_knowledge_docs_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    doc_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    dialogue_segment_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("dialogue_segments.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    question_examples: Mapped[list | None] = mapped_column(JSONB)
    tags: Mapped[list | None] = mapped_column(JSONB)
    scenario_type: Mapped[str | None] = mapped_column(String(100))
    business_line: Mapped[str | None] = mapped_column(String(100))
    product_name: Mapped[str | None] = mapped_column(String(100))
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, server_default="low")
    quality_score: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    review_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pending_review")
    review_comment: Mapped[str | None] = mapped_column(Text)
    reviewer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = mapped_column(DateTime(timezone=True))
    price_filtered: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    contains_price_intent: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    contains_original_price: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_desensitized: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
