"""add dataset coverage geometry

Revision ID: 0002_dataset_coverage_geom
Revises: 0001_initial
Create Date: 2026-04-07 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


revision: str = "0002_dataset_coverage_geom"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.add_column(
        "datasets",
        sa.Column("coverage_geom", Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True),
    )
    op.create_index("ix_datasets_coverage_geom_gist", "datasets", ["coverage_geom"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("ix_datasets_coverage_geom_gist", table_name="datasets")
    op.drop_column("datasets", "coverage_geom")
