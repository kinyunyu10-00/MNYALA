# migrations/versions/xxxx_add_is_active_field_to_users.py

"""Add is_active field to users

Revision ID: xxxx
Revises: b4ce9b0864c0
Create Date: 2026-08-21 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'xxxx'
down_revision = 'b4ce9b0864c0'
branch_labels = None
depends_on = None


def upgrade():
    # =============================================
    # CORRECT WAY - Add column with default value
    # =============================================
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.alter_column('users', 'is_active', nullable=False, server_default='true')


def downgrade():
    op.drop_column('users', 'is_active')