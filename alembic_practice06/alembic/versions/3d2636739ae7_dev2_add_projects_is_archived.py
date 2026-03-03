"""dev2: add projects.is_archived

Revision ID: 3d2636739ae7
Revises: 2e31df4d454b
Create Date: 2026-03-03 20:35:40.907384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d2636739ae7'
down_revision: Union[str, Sequence[str], None] = '9c12fbed2297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('is_archived', sa.Boolean(), server_default=sa.text('0'), nullable=False))

def downgrade() -> None:
    op.drop_column('projects', 'is_archived')