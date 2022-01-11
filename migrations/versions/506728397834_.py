"""empty message

Revision ID: 506728397834
Revises: 
Create Date: 2022-01-07 15:30:28.417367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '506728397834'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profession',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('abbreviation', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('raid_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('character',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('profession_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['profession_id'], ['profession.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'profession_id', name='name_profession_idx')
    )
    op.create_table('raid',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('raid_date', sa.Date(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('raid_type', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['raid_type'], ['raid_type.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fight',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('raid_id', sa.Integer(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('fight_date', sa.Date(), nullable=True),
    sa.Column('start_time', sa.TIMESTAMP(), nullable=True),
    sa.Column('end_time', sa.TIMESTAMP(), nullable=True),
    sa.Column('skipped', sa.Boolean(), nullable=True),
    sa.Column('num_allies', sa.Integer(), nullable=True),
    sa.Column('num_enemies', sa.Integer(), nullable=True),
    sa.Column('damage', sa.Integer(), nullable=True),
    sa.Column('boonrips', sa.Integer(), nullable=True),
    sa.Column('cleanses', sa.Integer(), nullable=True),
    sa.Column('stability', sa.Integer(), nullable=True),
    sa.Column('healing', sa.Integer(), nullable=True),
    sa.Column('deaths', sa.Integer(), nullable=True),
    sa.Column('kills', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['raid_id'], ['raid.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('raid_id', sa.Integer(), nullable=True),
    sa.Column('character_id', sa.Integer(), nullable=True),
    sa.Column('attendance_count', sa.Integer(), nullable=True),
    sa.Column('attendance_duration', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['character_id'], ['character.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['raid_id'], ['raid.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('aegis_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_aegis', sa.Integer(), nullable=True),
    sa.Column('avg_aegis_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('barrier_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_barrier', sa.Integer(), nullable=True),
    sa.Column('avg_barrier_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cleanse_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_cleanses', sa.Integer(), nullable=True),
    sa.Column('avg_cleanses_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('death_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_deaths', sa.Integer(), nullable=True),
    sa.Column('avg_deaths_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dist_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_dist', sa.Integer(), nullable=True),
    sa.Column('avg_dist_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dmg_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_dmg', sa.Integer(), nullable=True),
    sa.Column('avg_dmg_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dmg_taken_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_dmg_taken', sa.Integer(), nullable=True),
    sa.Column('avg_dmg_taken_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fury_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_fury', sa.Integer(), nullable=True),
    sa.Column('avg_fury_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('heal_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_heal', sa.Integer(), nullable=True),
    sa.Column('avg_heal_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('kills_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_kills', sa.Integer(), nullable=True),
    sa.Column('avg_kill_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('might_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_might', sa.Integer(), nullable=True),
    sa.Column('avg_might_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prot_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_prot', sa.Integer(), nullable=True),
    sa.Column('avg_prot_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rip_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_rips', sa.Integer(), nullable=True),
    sa.Column('avg_rips_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stab_stat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_stat_id', sa.Integer(), nullable=True),
    sa.Column('times_top', sa.Integer(), nullable=True),
    sa.Column('total_stab', sa.Integer(), nullable=True),
    sa.Column('avg_stab_s', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['player_stat_id'], ['player_stat.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stab_stat')
    op.drop_table('rip_stat')
    op.drop_table('prot_stat')
    op.drop_table('might_stat')
    op.drop_table('kills_stat')
    op.drop_table('heal_stat')
    op.drop_table('fury_stat')
    op.drop_table('dmg_taken_stat')
    op.drop_table('dmg_stat')
    op.drop_table('dist_stat')
    op.drop_table('death_stat')
    op.drop_table('cleanse_stat')
    op.drop_table('barrier_stat')
    op.drop_table('aegis_stat')
    op.drop_table('player_stat')
    op.drop_table('fight')
    op.drop_table('raid')
    op.drop_table('character')
    op.drop_table('raid_type')
    op.drop_table('profession')
    # ### end Alembic commands ###