"""empty message

Revision ID: 7791145dcee8
Revises: 40284a06f4f9
Create Date: 2022-01-10 11:05:21.008818

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7791145dcee8'
down_revision = '40284a06f4f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('death_stat', sa.Column('avg_deaths_m', sa.Float(), nullable=True))
    op.drop_column('death_stat', 'avg_deaths_s')
    op.add_column('kills_stat', sa.Column('avg_kills_m', sa.Float(), nullable=True))
    op.drop_column('kills_stat', 'avg_kill_s')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('kills_stat', sa.Column('avg_kill_s', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_column('kills_stat', 'avg_kills_m')
    op.add_column('death_stat', sa.Column('avg_deaths_s', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_column('death_stat', 'avg_deaths_m')
    # ### end Alembic commands ###
