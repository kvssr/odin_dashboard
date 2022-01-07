from app import db


class Character(db.Model):

    __tablename__ = 'character'
    __table_args__ = (
        db.UniqueConstraint('name', 'profession_id', name='name_profession_idx'),
    )

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    profession_id = db.Column(db.Integer(), db.ForeignKey('profession.id', ondelete="CASCADE"))


class Profession(db.Model):

    __tablename__ = 'profession'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    abbreviation = db.Column(db.String())


class PlayerStat(db.Model):

    __tablename__ = 'player_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_id = db.Column(db.Integer(), db.ForeignKey('raid.id', ondelete="CASCADE"))
    character_id = db.Column(db.Integer(), db.ForeignKey('character.id', ondelete="CASCADE"))
    attendance_count = db.Column(db.Integer())
    attendance_duration = db.Column(db.Integer())


class Raid(db.Model):

    __tablename__ = 'raid'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_date = db.Column(db.Date())
    name = db.Column(db.String())
    raid_type = db.Column(db.Integer(), db.ForeignKey('raid_type.id', ondelete="CASCADE"))


class RaidType(db.Model):

    __tablename__ = 'raid_type'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())


class Fight(db.Model):

    __tablename__ = 'fight'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_id = db.Column(db.Integer(), db.ForeignKey('raid.id', ondelete="CASCADE"))
    number = db.Column(db.Integer())
    fight_date = db.Column(db.Date())
    start_time = db.Column(db.TIMESTAMP())
    end_time = db.Column(db.TIMESTAMP())
    skipped = db.Column(db.Boolean())
    num_allies = db.Column(db.Integer())
    num_enemies = db.Column(db.Integer())
    damage = db.Column(db.Integer())
    boonrips = db.Column(db.Integer())
    cleanses = db.Column(db.Integer())
    stability = db.Column(db.Integer())
    healing = db.Column(db.Integer())
    deaths = db.Column(db.Integer())
    kills = db.Column(db.Integer())


class DmgStat(db.Model):

    __tablename__ = 'dmg_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_dmg = db.Column(db.Integer())
    avg_dmg_s = db.Column(db.Float())


class RipStat(db.Model):

    __tablename__ = 'rip_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_rips = db.Column(db.Integer())
    avg_rips_s = db.Column(db.Float())


class CleanseStat(db.Model):

    __tablename__ = 'cleanse_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_cleanses = db.Column(db.Integer())
    avg_cleanses_s = db.Column(db.Float())


class StabStat(db.Model):

    __tablename__ = 'stab_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_stab = db.Column(db.Integer())
    avg_stab_s = db.Column(db.Float())


class HealStat(db.Model):

    __tablename__ = 'heal_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_heal = db.Column(db.Integer())
    avg_heal_s = db.Column(db.Float())


class DistStat(db.Model):

    __tablename__ = 'dist_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_dist = db.Column(db.Integer())
    avg_dist_s = db.Column(db.Float())


class ProtStat(db.Model):

    __tablename__ = 'prot_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_prot = db.Column(db.Integer())
    avg_prot_s = db.Column(db.Float())


class AegisStat(db.Model):

    __tablename__ = 'aegis_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_aegis = db.Column(db.Integer())
    avg_aegis_s = db.Column(db.Float())


class MightStat(db.Model):

    __tablename__ = 'might_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_might = db.Column(db.Integer())
    avg_might_s = db.Column(db.Float())


class FuryStat(db.Model):

    __tablename__ = 'fury_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_fury = db.Column(db.Integer())
    avg_fury_s = db.Column(db.Float())


class BarrierStat(db.Model):

    __tablename__ = 'barrier_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_barrier = db.Column(db.Integer())
    avg_barrier_s = db.Column(db.Float())


class DmgTakenStat(db.Model):

    __tablename__ = 'dmg_taken_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_dmg_taken = db.Column(db.Integer())
    avg_dmg_taken_s = db.Column(db.Float())


class DeathStat(db.Model):

    __tablename__ = 'death_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_deaths = db.Column(db.Integer())
    avg_deaths_s = db.Column(db.Float())


class KillsStat(db.Model):

    __tablename__ = 'kills_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"))
    times_top = db.Column(db.Integer())
    total_kills = db.Column(db.Integer())
    avg_kill_s = db.Column(db.Float())
