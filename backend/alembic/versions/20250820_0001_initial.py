"""initial schema

Revision ID: 20250820_0001
Revises: 
Create Date: 2025-08-20 00:01:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250820_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("pipeline_spec", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("workflow_id", sa.Integer, sa.ForeignKey("workflows.id"), nullable=True),
        sa.Column("status", sa.Enum("queued", "running", "failed", "completed", name="runstatus"), nullable=False),
        sa.Column("metrics", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "run_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.Integer, sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("detail", sa.String(length=4000), nullable=True),
    )
    op.create_table(
        "models",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

def downgrade() -> None:
    op.drop_table("models")
    op.drop_table("run_events")
    op.drop_table("runs")
    op.drop_table("workflows")
    op.execute("DROP TYPE IF EXISTS runstatus")
