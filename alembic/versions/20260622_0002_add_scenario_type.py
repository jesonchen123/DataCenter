"""add scenario_type to dialogue_segments and knowledge_docs

Revision ID: 20260622_0002
Revises: 20260621_0001
Create Date: 2026-06-22
"""

from alembic import op
import sqlalchemy as sa

revision = "20260622_0002"
down_revision = "20260621_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dialogue_segments",
        sa.Column("scenario_type", sa.String(100), nullable=True),
    )
    op.create_index(
        "idx_dialogue_segments_scenario_type",
        "dialogue_segments",
        ["scenario_type"],
    )
    op.add_column(
        "knowledge_docs",
        sa.Column("scenario_type", sa.String(100), nullable=True),
    )
    op.create_index(
        "idx_knowledge_docs_scenario_type",
        "knowledge_docs",
        ["scenario_type"],
    )


def downgrade() -> None:
    op.drop_index("idx_knowledge_docs_scenario_type", "knowledge_docs")
    op.drop_column("knowledge_docs", "scenario_type")
    op.drop_index("idx_dialogue_segments_scenario_type", "dialogue_segments")
    op.drop_column("dialogue_segments", "scenario_type")
