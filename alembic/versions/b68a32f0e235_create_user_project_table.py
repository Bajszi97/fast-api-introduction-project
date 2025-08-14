"""create_user_project_table

Revision ID: b68a32f0e235
Revises: 0a646c3857d8
Create Date: 2025-08-14 18:40:39.335693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b68a32f0e235'
down_revision: Union[str, Sequence[str], None] = '0a646c3857d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'user_project',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True, nullable=False),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id'), primary_key=True, nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('admin', 'participant')", name='ck_user_project_role')
    )


def downgrade():
    op.drop_table('user_project')