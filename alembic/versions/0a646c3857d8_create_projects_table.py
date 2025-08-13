"""create projects table

Revision ID: 0a646c3857d8
Revises: 7e707916926b
Create Date: 2025-08-12 20:03:03.692112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a646c3857d8'
down_revision: Union[str, Sequence[str], None] = '7e707916926b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=False), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('projects')