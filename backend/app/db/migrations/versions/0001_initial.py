"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-07 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("temporal_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("temporal_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("spatial_extent", sa.JSON(), nullable=True),
        sa.Column("resolution_km", sa.Float(), nullable=True),
        sa.Column("grid_type", sa.String(length=50), nullable=True),
        sa.Column("storage_path", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "extraction_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("time_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("time_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("geometry_type", sa.String(length=40), nullable=False),
        sa.Column("geometry_payload", sa.JSON(), nullable=False),
        sa.Column("variable_selection", sa.JSON(), nullable=False),
        sa.Column("output_format", sa.String(length=30), nullable=False),
        sa.Column("processing_options", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "variables",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_staggered", sa.Boolean(), nullable=False),
        sa.Column("dimensions", sa.JSON(), nullable=True),
        sa.Column("available_levels", sa.JSON(), nullable=True),
        sa.Column("is_derived", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "extraction_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["extraction_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )


def downgrade() -> None:
    op.drop_table("extraction_results")
    op.drop_table("variables")
    op.drop_table("extraction_jobs")
    op.drop_table("datasets")
