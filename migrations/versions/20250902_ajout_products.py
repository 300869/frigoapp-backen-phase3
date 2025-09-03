"""create products table

Revision ID: 20250902160000
Revises: 
Create Date: 2025-09-02 16:00:00
"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration
revision = '20250902160000'
down_revision = '20250902130515'  # si tu as déjà une migration "users", mets son revision ID ici 
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('barcode', sa.String(length=64), nullable=True),
        sa.Column('default_shelf_life_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_products_barcode', 'products', ['barcode'])

def downgrade() -> None:
    op.drop_index('ix_products_barcode', table_name='products')
    op.drop_index('ix_products_name', table_name='products')
    op.drop_index('ix_products_id', table_name='products')
    op.drop_table('products')
