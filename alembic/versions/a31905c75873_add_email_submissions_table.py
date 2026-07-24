"""add_email_submissions_table

Revision ID: a31905c75873
Revises: 001
Create Date: 2026-07-24 12:31:31.522806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a31905c75873'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'email_submissions',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('audit_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('sent_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ondelete='CASCADE')
    )
    op.create_index('idx_audit_email', 'email_submissions', ['audit_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_audit_email', table_name='email_submissions')

    op.drop_table('email_submissions')