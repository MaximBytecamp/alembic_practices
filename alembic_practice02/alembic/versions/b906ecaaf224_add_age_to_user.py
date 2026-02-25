"""add age to user

Revision ID: b906ecaaf224
Revises: c63bbc8e7381
Create Date: 2026-02-25 17:56:57.539888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b906ecaaf224'
down_revision: Union[str, Sequence[str], None] = 'c63bbc8e7381'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Шаг 1: добавляем колонку как nullable
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))

    # Шаг 2: заполняем дефолтным значением для существующих строк
    op.execute("UPDATE users SET age = 0 WHERE age IS NULL")

    # Шаг 3: делаем колонку NOT NULL
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('age', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'age')