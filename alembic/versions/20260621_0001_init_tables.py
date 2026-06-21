"""init tables

Revision ID: 20260621_0001
Revises:
Create Date: 2026-06-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260621_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("email", sa.String(255)),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('manager', 'normal_user')", name="ck_users_role"),
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_users_status"),
    )
    op.create_index("idx_users_role", "users", ["role"])
    op.create_index("idx_users_status", "users", ["status"])

    op.create_table(
        "mock_chats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("mock_chat_id", sa.String(100), nullable=False, unique=True),
        sa.Column("source_platform", sa.String(50), nullable=False),
        sa.Column("business_line", sa.String(100)),
        sa.Column("product_name", sa.String(100)),
        sa.Column("scenario_type", sa.String(100)),
        sa.Column("raw_content", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_mock_chats_source_platform", "mock_chats", ["source_platform"])
    op.create_index("idx_mock_chats_scenario_type", "mock_chats", ["scenario_type"])
    op.create_index("idx_mock_chats_raw_content_gin", "mock_chats", ["raw_content"], postgresql_using="gin")

    op.create_table(
        "process_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_no", sa.String(100), nullable=False, unique=True),
        sa.Column("mock_chat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mock_chats.id"), nullable=False),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("current_step", sa.String(100)),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("step_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_process_tasks_mock_chat_id", "process_tasks", ["mock_chat_id"])
    op.create_index("idx_process_tasks_triggered_by", "process_tasks", ["triggered_by"])
    op.create_index("idx_process_tasks_status", "process_tasks", ["status"])
    op.create_index("idx_process_tasks_created_at", "process_tasks", ["created_at"])

    op.create_table(
        "dialogue_segments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("segment_no", sa.String(100), nullable=False, unique=True),
        sa.Column("process_task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_tasks.id"), nullable=False),
        sa.Column("mock_chat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mock_chats.id"), nullable=False),
        sa.Column("original_content", sa.Text()),
        sa.Column("cleaned_content", sa.Text()),
        sa.Column("desensitized_content", sa.Text()),
        sa.Column("price_filtered_content", sa.Text()),
        sa.Column("customer_question", sa.Text()),
        sa.Column("staff_answer", sa.Text()),
        sa.Column("business_line", sa.String(100)),
        sa.Column("product_name", sa.String(100)),
        sa.Column("tags", postgresql.JSONB()),
        sa.Column("contains_sensitive_info", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("contains_price_info", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("price_filter_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("price_risk_level", sa.String(50), nullable=False, server_default="none"),
        sa.Column("status", sa.String(50), nullable=False, server_default="generated"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_dialogue_segments_task_id", "dialogue_segments", ["process_task_id"])
    op.create_index("idx_dialogue_segments_mock_chat_id", "dialogue_segments", ["mock_chat_id"])
    op.create_index("idx_dialogue_segments_price_risk", "dialogue_segments", ["price_risk_level"])
    op.create_index("idx_dialogue_segments_contains_price", "dialogue_segments", ["contains_price_info"])
    op.create_index("idx_dialogue_segments_tags_gin", "dialogue_segments", ["tags"], postgresql_using="gin")

    op.create_table(
        "knowledge_docs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("doc_no", sa.String(100), nullable=False, unique=True),
        sa.Column("dialogue_segment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dialogue_segments.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("question_examples", postgresql.JSONB()),
        sa.Column("tags", postgresql.JSONB()),
        sa.Column("business_line", sa.String(100)),
        sa.Column("product_name", sa.String(100)),
        sa.Column("risk_level", sa.String(50), nullable=False, server_default="low"),
        sa.Column("quality_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("review_status", sa.String(50), nullable=False, server_default="pending_review"),
        sa.Column("review_comment", sa.Text()),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("price_filtered", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("contains_price_intent", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("contains_original_price", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_desensitized", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_knowledge_docs_review_status", "knowledge_docs", ["review_status"])
    op.create_index("idx_knowledge_docs_risk_level", "knowledge_docs", ["risk_level"])
    op.create_index("idx_knowledge_docs_quality_score", "knowledge_docs", ["quality_score"])
    op.create_index("idx_knowledge_docs_price_filtered", "knowledge_docs", ["price_filtered"])
    op.create_index("idx_knowledge_docs_contains_original_price", "knowledge_docs", ["contains_original_price"])
    op.create_index("idx_knowledge_docs_tags_gin", "knowledge_docs", ["tags"], postgresql_using="gin")
    op.create_index("idx_knowledge_docs_created_at", "knowledge_docs", ["created_at"])

    op.create_table(
        "export_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("export_no", sa.String(100), nullable=False, unique=True),
        sa.Column("export_type", sa.String(100), nullable=False),
        sa.Column("filters", postgresql.JSONB()),
        sa.Column("export_content", postgresql.JSONB()),
        sa.Column("document_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_export_tasks_created_by", "export_tasks", ["created_by"])
    op.create_index("idx_export_tasks_status", "export_tasks", ["status"])
    op.create_index("idx_export_tasks_created_at", "export_tasks", ["created_at"])
    op.create_index("idx_export_tasks_content_gin", "export_tasks", ["export_content"], postgresql_using="gin")

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(100)),
        sa.Column("target_id", sa.String(100)),
        sa.Column("detail", postgresql.JSONB()),
        sa.Column("ip_address", sa.String(100)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_audit_logs_action", "audit_logs", ["action"])
    op.create_index("idx_audit_logs_target", "audit_logs", ["target_type", "target_id"])
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("idx_audit_logs_detail_gin", "audit_logs", ["detail"], postgresql_using="gin")

    op.create_table(
        "llm_call_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("related_type", sa.String(100)),
        sa.Column("related_id", postgresql.UUID(as_uuid=True)),
        sa.Column("provider", sa.String(100)),
        sa.Column("model_name", sa.String(100)),
        sa.Column("prompt", sa.Text()),
        sa.Column("request_payload", postgresql.JSONB()),
        sa.Column("response_payload", postgresql.JSONB()),
        sa.Column("parsed_output", postgresql.JSONB()),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_llm_call_logs_related", "llm_call_logs", ["related_type", "related_id"])
    op.create_index("idx_llm_call_logs_status", "llm_call_logs", ["status"])
    op.create_index("idx_llm_call_logs_created_at", "llm_call_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("llm_call_logs")
    op.drop_table("audit_logs")
    op.drop_table("export_tasks")
    op.drop_table("knowledge_docs")
    op.drop_table("dialogue_segments")
    op.drop_table("process_tasks")
    op.drop_table("mock_chats")
    op.drop_table("users")
