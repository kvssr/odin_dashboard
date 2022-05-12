"""empty message

Revision ID: 896e287ba12c
Revises: 6bdc635b6a8e
Create Date: 2022-05-12 07:43:11.954411

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '896e287ba12c'
down_revision = '6bdc635b6a8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('log_date', sa.Date(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['raid.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('log')
    # ### end Alembic commands ###
