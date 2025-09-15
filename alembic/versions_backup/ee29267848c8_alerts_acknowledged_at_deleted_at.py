"""Revision ID: ee29267848c8
Revises:    fe2c47df04f6
Create Date: 2025-09-07 14:43:43.832414
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ee29267848c8"
down_revision = "fe2c47df04f6"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass


op.add_column(
    "alerts", sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True)
)
op.add_column(
    "alerts", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
)
