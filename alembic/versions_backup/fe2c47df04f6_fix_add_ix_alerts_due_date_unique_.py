import sqlalchemy as sa

from alembic import op

revision = "fe2c47df04f6"
down_revision = "995bb476cab6"  # ton head actuel (mergepoint)
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent-ish : crÃ©e l'index s'il n'existe pas dÃ©jÃ  cÃ´tÃ© DB
    op.create_index("ix_alerts_due_date", "alerts", ["due_date"], unique=False)
    # Contrainte unique (si dÃ©jÃ  crÃ©Ã©e manuellement, Alembic lÃ¨vera une erreur â€” dans ce cas tu peux commenter cette ligne)
    op.create_unique_constraint(
        "uq_alerts_product_kind_due_date",
        "alerts",
        ["product_id", "kind", "due_date"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_alerts_product_kind_due_date", "alerts", type_="unique")
    op.drop_index("ix_alerts_due_date", table_name="alerts")
