"""remove cbrf

Revision ID: 6ddabe9ee105
Revises: 898ec90733e2
Create Date: 2024-03-16 21:40:34.031312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ddabe9ee105'
down_revision = '898ec90733e2'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE settings SET src='oer' WHERE src='cbrf'")


def downgrade():
    pass
