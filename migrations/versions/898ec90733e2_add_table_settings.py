"""add table settings

Revision ID: 898ec90733e2
Revises: 56df5c6b0df6
Create Date: 2022-02-07 23:45:54.212862

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '898ec90733e2'
down_revision = '56df5c6b0df6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'settings',
        sa.Column('chat_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('vals', sa.Text(), nullable=True),
        sa.Column('src', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.tg_id']),
        sa.PrimaryKeyConstraint('chat_id'),
    )


def downgrade():
    op.drop_table('settings')
