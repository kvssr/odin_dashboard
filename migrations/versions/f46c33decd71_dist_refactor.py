"""dist refactor

Revision ID: f46c33decd71
Revises: 4dfb9c636e9d
Create Date: 2022-08-16 14:46:20.315723

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f46c33decd71'
down_revision = '4dfb9c636e9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dist_stat', 'avg_dist_s')
    op.drop_column('dist_stat', 'total_dist')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dist_stat', sa.Column('total_dist', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('dist_stat', sa.Column('avg_dist_s', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
