import sqlalchemy as sa

from alembic import op

# revision = 'xxxx'              # <-- la valeur générée par Alembic
# down_revision = 'yyyy'         # <-- la valeur générée par Alembic
branch_labels = None
depends_on = None


def upgrade():
    # Ajoute si absent (Postgres)
    op.execute("ALTER TABLE products   ADD COLUMN IF NOT EXISTS aliases     JSONB")
    op.execute("ALTER TABLE products   ADD COLUMN IF NOT EXISTS shelf_life  JSONB")
    op.execute("ALTER TABLE categories ADD COLUMN IF NOT EXISTS shelf_life  JSONB")


def downgrade():
    op.execute("ALTER TABLE products   DROP COLUMN IF EXISTS aliases")
    op.execute("ALTER TABLE products   DROP COLUMN IF EXISTS shelf_life")
    op.execute("ALTER TABLE categories DROP COLUMN IF EXISTS shelf_life")
