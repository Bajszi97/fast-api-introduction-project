"""Create documents table

Revision ID: aed117a75179
Revises: b68a32f0e235
Create Date: 2025-08-17 14:57:07.360235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aed117a75179'
down_revision: Union[str, Sequence[str], None] = 'b68a32f0e235'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id', ondelete="CASCADE"), nullable=False),
        sa.Column('filename', sa.String(length=128), nullable=False),
        sa.Column('file_type', sa.String(length=16), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('documents')
