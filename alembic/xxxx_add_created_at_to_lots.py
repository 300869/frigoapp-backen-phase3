import sqlalchemy as sa

from alembic import op

# Identifiants de révision
revision = "xxxx"  # <-- généré automatiquement
down_revision = "précédent_revision_id"  # remplace par l’ID de la migration précédente
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "lots", sa.Column("created_at", sa.Date, server_default=sa.func.current_date())
    )


def downgrade():
    op.drop_column("lots", "created_at")
