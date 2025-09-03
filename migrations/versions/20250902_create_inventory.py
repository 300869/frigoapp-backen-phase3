"""create inventory table

Revision ID: 20250902170000
Revises: 20250902160000
Create Date: 2025-09-02 17:00:00
"""
from alembic import op
import sqlalchemy as sa

# Identifiants
revision = '20250902170000'
down_revision = '20250902160000'  # ← mets l'ID exact de ta migration "products"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'inventory',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('product_id', sa.Integer(), nullable=False, index=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.Date(), nullable=True),
        sa.Column('note', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_inventory_id', 'inventory', ['id'])
    op.create_index('ix_inventory_user', 'inventory', ['user_id'])
    op.create_index('ix_inventory_product', 'inventory', ['product_id'])

def downgrade() -> None:
    op.drop_index('ix_inventory_product', table_name='inventory')
    op.drop_index('ix_inventory_user', table_name='inventory')
    op.drop_index('ix_inventory_id', table_name='inventory')
    op.drop_table('inventory')
