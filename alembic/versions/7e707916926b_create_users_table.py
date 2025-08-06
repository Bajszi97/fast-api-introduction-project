"""create users table

Revision ID: 7e707916926b
Revises:
Create Date: 2025-08-06 17:03:08.894908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e707916926b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
        op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('login', sa.String(64), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(256), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('users')