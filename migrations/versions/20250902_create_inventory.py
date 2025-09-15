"""create alerts table (with indexes + unique constraint)

Revision ID: 20250902163000
Revises: 20250902160000
Create Date: 2025-09-02 16:30:00
"""

import sqlalchemy as sa

from alembic import op

# IDs
revision = "20250902163000"
down_revision = "20250902160000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "kind", sa.String(length=32), nullable=False
        ),  # SOON, EXPIRED, OUT_OF_STOCK...
        sa.Column(
            "due_date", sa.Date(), nullable=True
        ),  # peut être NULL (ex: OUT_OF_STOCK legacy)
        sa.Column(
            "is_ack", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "product_id",
            "kind",
            "due_date",
            name="uq_alerts_product_kind_date",
        ),
    )

    # Index pour les filtres/tri utilisés par les routes
    op.create_index("ix_alerts_due_date", "alerts", ["due_date"])
    op.create_index("ix_alerts_kind_due_date", "alerts", ["kind", "due_date"])
    op.create_index("ix_alerts_product_kind", "alerts", ["product_id", "kind"])
    op.create_index("ix_alerts_is_ack", "alerts", ["is_ack"])


def downgrade() -> None:
    op.drop_index("ix_alerts_is_ack", table_name="alerts")
    op.drop_index("ix_alerts_product_kind", table_name="alerts")
    op.drop_index("ix_alerts_kind_due_date", table_name="alerts")
    op.drop_index("ix_alerts_due_date", table_name="alerts")
    op.drop_table("alerts")
