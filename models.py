from sqlalchemy.orm import relationship
from app import db


class Character(db.Model):

    __tablename__ = 'character'
    __table_args__ = (
        db.UniqueConstraint('name', 'profession_id', name='name_profession_idx'),
    )

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    profession_id = db.Column(db.Integer(), db.ForeignKey('profession.id', ondelete="CASCADE"))
    
    profession = relationship("Profession", back_populates="characters")
    playerstats = relationship("PlayerStat", back_populates="character")


class Profession(db.Model):

    __tablename__ = 'profession'
    __table_args__ = (
        db.UniqueConstraint('name', name='name_idx'),
    )

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    abbreviation = db.Column(db.String(), unique=True)
    color = db.Column(db.String())

    characters = relationship("Character", back_populates="profession")


class PlayerStat(db.Model):

    __tablename__ = 'player_stat'
    __table_args__ = (
        db.UniqueConstraint('raid_id', 'character_id', name='raid_character_idx'),
    )

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_id = db.Column(db.Integer(), db.ForeignKey('raid.id', ondelete="CASCADE"))
    character_id = db.Column(db.Integer(), db.ForeignKey('character.id', ondelete="CASCADE"))
    attendance_count = db.Column(db.Integer())
    attendance_duration = db.Column(db.Integer())

    raid = relationship("Raid", back_populates="playerstats")
    character = relationship("Character", back_populates="playerstats")

    dmg_stat = relationship("DmgStat", back_populates="player_stat", uselist=False, lazy='select')
    rip_stat = relationship("RipStat", back_populates="player_stat", uselist=False, lazy='select')
    cleanse_stat = relationship("CleanseStat", back_populates="player_stat", uselist=False, lazy='select')
    stab_stat = relationship("StabStat", back_populates="player_stat", uselist=False, lazy='select')
    heal_stat = relationship("HealStat", back_populates="player_stat", uselist=False, lazy='select')
    dist_stat = relationship("DistStat", back_populates="player_stat", uselist=False, lazy='select')
    prot_stat = relationship("ProtStat", back_populates="player_stat", uselist=False, lazy='select')
    aegis_stat = relationship("AegisStat", back_populates="player_stat", uselist=False, lazy='select')
    might_stat = relationship("MightStat", back_populates="player_stat", uselist=False, lazy='select')
    fury_stat = relationship("FuryStat", back_populates="player_stat", uselist=False, lazy='select')
    barrier_stat = relationship("BarrierStat", back_populates="player_stat", uselist=False, lazy='select')
    dmg_taken_stat = relationship("DmgTakenStat", back_populates="player_stat", uselist=False, lazy='select')
    death_stat = relationship("DeathStat", back_populates="player_stat", uselist=False, lazy='select')
    kills_stat = relationship("KillsStat", back_populates="player_stat", uselist=False, lazy='select')


class Raid(db.Model):

    __tablename__ = 'raid'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_date = db.Column(db.Date())
    name = db.Column(db.String())
    raid_type_id = db.Column(db.Integer(), db.ForeignKey('raid_type.id', ondelete="CASCADE"))

    raid_type = relationship("RaidType", back_populates="raids")
    playerstats = relationship("PlayerStat", back_populates="raid")
    fights = relationship("Fight", back_populates="raid")


class RaidType(db.Model):

    __tablename__ = 'raid_type'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)

    raids = relationship("Raid", back_populates="raid_type")


class Fight(db.Model):

    __tablename__ = 'fight'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_id = db.Column(db.Integer(), db.ForeignKey('raid.id', ondelete="CASCADE"))
    number = db.Column(db.Integer())
    fight_date = db.Column(db.Date())
    start_time = db.Column(db.String())
    end_time = db.Column(db.String())
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

    raid = relationship("Raid", back_populates="fights")


class DmgStat(db.Model):

    __tablename__ = 'dmg_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_dmg = db.Column(db.Integer())
    avg_dmg_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="dmg_stat")

    def to_dict(self):
        return {
            'Name': self.player_stat.character.name,
            'Times Top': self.times_top,
            'Total dmg': self.total_dmg,
            'Average dmg per s': self.avg_dmg_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name
        }


class RipStat(db.Model):

    __tablename__ = 'rip_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_rips = db.Column(db.Integer())
    avg_rips_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="rip_stat")



class CleanseStat(db.Model):

    __tablename__ = 'cleanse_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_cleanses = db.Column(db.Integer())
    avg_cleanses_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="cleanse_stat")


class StabStat(db.Model):

    __tablename__ = 'stab_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_stab = db.Column(db.Integer())
    avg_stab_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="stab_stat")


class HealStat(db.Model):

    __tablename__ = 'heal_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_heal = db.Column(db.Integer())
    avg_heal_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="heal_stat")



class DistStat(db.Model):

    __tablename__ = 'dist_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_dist = db.Column(db.Integer())
    avg_dist_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="dist_stat")

    def to_dict(self):
        return {
            'Name': self.player_stat.character.name,
            'Times Top': self.times_top,
            'Total dist': self.total_dist,
            'Percentage Top': self.percentage_top,
            'Average dist per s': self.avg_dist_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name
        }

class ProtStat(db.Model):

    __tablename__ = 'prot_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_prot = db.Column(db.Integer())
    avg_prot_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="prot_stat")


class AegisStat(db.Model):

    __tablename__ = 'aegis_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_aegis = db.Column(db.Integer())
    avg_aegis_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="aegis_stat")


class MightStat(db.Model):

    __tablename__ = 'might_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_might = db.Column(db.Integer())
    avg_might_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="might_stat")


class FuryStat(db.Model):

    __tablename__ = 'fury_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_fury = db.Column(db.Integer())
    avg_fury_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="fury_stat")

class BarrierStat(db.Model):

    __tablename__ = 'barrier_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_barrier = db.Column(db.Integer())
    avg_barrier_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="barrier_stat")


class DmgTakenStat(db.Model):

    __tablename__ = 'dmg_taken_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_dmg_taken = db.Column(db.Integer())
    avg_dmg_taken_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="dmg_taken_stat")

class DeathStat(db.Model):

    __tablename__ = 'death_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_deaths = db.Column(db.Integer())
    avg_deaths_m = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="death_stat")


class KillsStat(db.Model):

    __tablename__ = 'kills_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_kills = db.Column(db.Integer())
    avg_kills_m = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="kills_stat")
