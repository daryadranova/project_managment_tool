"""new modifications

Revision ID: f9249e823104
Revises: f0377ff1daa2
Create Date: 2022-06-06 15:29:12.568146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9249e823104'
down_revision = 'f0377ff1daa2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('Costs', sa.Column('in_archive', sa.String(), nullable=True))
    pass


def downgrade() -> None:
    pass
