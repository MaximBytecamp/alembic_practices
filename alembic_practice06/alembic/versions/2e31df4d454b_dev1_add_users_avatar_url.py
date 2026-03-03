"""dev1: add users.avatar_url

Revision ID: 2e31df4d454b
Revises: 9c12fbed2297
Create Date: 2026-03-03 20:35:35.187344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e31df4d454b'
down_revision: Union[str, Sequence[str], None] = '9c12fbed2297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('avatar_url', sa.String(512), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
