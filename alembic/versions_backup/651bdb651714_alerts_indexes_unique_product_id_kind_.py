"""Add unique constraint and indexes on alerts (product_id, kind, due_date)"""

import sqlalchemy as sa

from alembic import op

# --- Identifiants de migration ---
revision = "651bdb651714"
# ⚠️ Remplace la valeur ci-dessous par l'ID de ta migration précédente (voir notes après le code)
down_revision = "bc2ca1948f5a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Indexes simples (accélèrent les filtres fréquents)
    op.create_index("ix_alerts_product_id", "alerts", ["product_id"])
    op.create_index("ix_alerts_kind", "alerts", ["kind"])
    op.create_index("ix_alerts_due_date", "alerts", ["due_date"])

    # Contrainte d'unicité pour empêcher les doublons fonctionnels
    op.create_unique_constraint(
        "uq_alerts_product_kind_due_date",
        "alerts",
        ["product_id", "kind", "due_date"],
    )


def downgrade() -> None:
    # Inverse de upgrade (ordre inverse conseillé)
    op.drop_constraint("uq_alerts_product_kind_due_date", "alerts", type_="unique")
    op.drop_index("ix_alerts_due_date", table_name="alerts")
    op.drop_index("ix_alerts_kind", table_name="alerts")
    op.drop_index("ix_alerts_product_id", table_name="alerts")
