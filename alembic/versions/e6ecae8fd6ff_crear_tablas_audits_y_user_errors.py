"""Crear tablas audits y user_errors

Revision ID: 001
Revises:
Create Date: 2026-07-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'audits',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('domain', sa.String(255), nullable=False),
        sa.Column('score_overall', sa.Integer(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=False),
        sa.Column('screenshot_url', sa.String(500), nullable=True),
        sa.Column('customer_email', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_domain', 'audits', ['domain'])
    op.create_index('idx_created_at', 'audits', ['created_at'], unique=False)

    op.create_table(
        'user_errors',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('error_type', sa.String(50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_error_type', 'user_errors', ['error_type'])


def downgrade() -> None:
    op.drop_index('idx_error_type', table_name='user_errors')
    op.drop_table('user_errors')
    op.drop_index('idx_created_at', table_name='audits')
    op.drop_index('idx_domain', table_name='audits')
    op.drop_table('audits')