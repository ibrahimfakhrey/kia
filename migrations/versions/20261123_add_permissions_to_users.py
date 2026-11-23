"""Add permissions column to users (per-section access for admins)

Revision ID: 20261123_permissions
Revises: 20260523_announcements
Create Date: 2026-11-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20261123_permissions'
down_revision = '20260523_announcements'
branch_labels = None
depends_on = None


def upgrade():
    # The app also adds this column at startup, so it may already be there.
    columns = {c['name'] for c in sa.inspect(op.get_bind()).get_columns('users')}
    if 'permissions' not in columns:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('permissions', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('permissions')
