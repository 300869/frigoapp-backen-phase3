"""create products table

Revision ID: 20250902160000
Revises: 20250902130515
Create Date: 2025-09-02 16:00:00
"""

import sqlalchemy as sa

from alembic import op

# IDs
revision = "20250902160000"
down_revision = "20250902130515"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        # champs réellement utilisés par l’app / tes tests
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default="0", nullable=False),
        # timestamps (pratique)
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
    )

    # Index utiles
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_expiry_date", "products", ["expiry_date"])


def downgrade() -> None:
    op.drop_index("ix_products_expiry_date", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")
