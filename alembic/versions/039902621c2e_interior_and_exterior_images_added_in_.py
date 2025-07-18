"""interior and exterior images added in Images

Revision ID: 039902621c2e
Revises: 776356efc3ba
Create Date: 2025-07-02 15:17:22.645361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '039902621c2e'
down_revision: Union[str, None] = '776356efc3ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('image_exterior', sa.Text(), nullable=True))
    op.alter_column('images', 'image',
               existing_type=mysql.VARCHAR(length=2000),
               type_=sa.Text(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('images', 'image',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(length=2000),
               existing_nullable=True)
    op.drop_column('images', 'image_exterior')
    # ### end Alembic commands ###
