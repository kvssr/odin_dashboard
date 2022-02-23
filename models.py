from datetime import datetime
from flask import session
from sqlalchemy.orm import relationship
from app import db
from flask_login import UserMixin, current_user


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

    def to_dict(self):
        return{
            'name': self.name,
            'abbreviation': self.abbreviation,
            'color': self.color
        }


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

    def to_dict(self):
        return {
            'raid_id': self.raid_id,
            'Date': self.raid.raid_date,
            'Start Time': self.raid.fightsummary[0].start_time,
            'character_id': self.character_id,
            'Name': self.character.name,
            'Damage': self.dmg_stat.avg_dmg_s,
            'Rips': self.rip_stat.avg_rips_s,
            'Cleanses': self.cleanse_stat.avg_cleanses_s,
            'Stab': self.stab_stat.avg_stab_s,
            'Healing': self.heal_stat.avg_heal_s,
            'Sticky': f'{self.dist_stat.percentage_top}%' if self.dist_stat else 0,
            'Prot': self.prot_stat.avg_prot_s,
            'Aegis': self.aegis_stat.avg_aegis_s,
            'Might': self.might_stat.avg_might_s,
            'Fury': self.fury_stat.avg_fury_s,
            'Barrier': self.barrier_stat.avg_barrier_s,
            'Damage Taken': self.dmg_taken_stat.times_top if self.dmg_taken_stat else None,
            'Deaths': self.death_stat.times_top,
        }


class Raid(db.Model):

    __tablename__ = 'raid'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_date = db.Column(db.Date())
    name = db.Column(db.String())
    raid_type_id = db.Column(db.Integer(), db.ForeignKey('raid_type.id', ondelete="CASCADE"))

    raid_type = relationship("RaidType", back_populates="raids")
    playerstats = relationship("PlayerStat", back_populates="raid")
    fights = relationship("Fight", back_populates="raid")
    fightsummary = relationship("FightSummary", back_populates="raid")


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
    distance_to_tag = db.Column(db.Integer())
    deaths = db.Column(db.Integer())
    kills = db.Column(db.Integer())
    protection = db.Column(db.Integer())
    aegis = db.Column(db.Integer())
    might = db.Column(db.Integer())
    fury = db.Column(db.Integer())
    barrier = db.Column(db.Integer())
    dmg_taken = db.Column(db.Integer())

    raid = relationship("Raid", back_populates="fights")

    def to_dict(self):
        return {
            'number': self.number,
            'start time': self.start_time,
            'end time': self.end_time,
            'skipped': 'yes' if self.skipped else 'no',
            '# Allies': self.num_allies,
            '# Enemies': self.num_enemies,
            'kills': self.kills,
            'deaths': self.deaths,
            'damage': f'{self.damage:,}',
            'boonrips': f'{self.boonrips:,}',
            'cleanses': f'{self.cleanses:,}',
            'healing': f'{self.healing:,}'
        }


class DmgStat(db.Model):

    __tablename__ = 'dmg_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_dmg = db.Column(db.Integer())
    avg_dmg_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="dmg_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total dmg': self.total_dmg,
            'Average dmg per s': self.avg_dmg_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
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

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total rips': self.total_rips,
            'Average rips per s': self.avg_rips_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }



class CleanseStat(db.Model):

    __tablename__ = 'cleanse_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_cleanses = db.Column(db.Integer())
    avg_cleanses_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="cleanse_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total cleanses': self.total_cleanses,
            'Average cleanses per s': self.avg_cleanses_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class StabStat(db.Model):

    __tablename__ = 'stab_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_stab = db.Column(db.Integer())
    avg_stab_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="stab_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total stab': self.total_stab,
            'Average stab per s': self.avg_stab_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class HealStat(db.Model):

    __tablename__ = 'heal_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_heal = db.Column(db.Integer())
    avg_heal_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="heal_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total heal': self.total_heal,
            'Average heal per s': self.avg_heal_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }



class DistStat(db.Model):

    __tablename__ = 'dist_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_dist = db.Column(db.Integer())
    avg_dist_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="dist_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total dist': self.total_dist,
            'Percentage Top': self.percentage_top,
            'Average dist per s': self.avg_dist_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
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

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total prot': self.total_prot,
            'Average prot per s': self.avg_prot_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class AegisStat(db.Model):

    __tablename__ = 'aegis_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_aegis = db.Column(db.Integer())
    avg_aegis_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="aegis_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total aegis': self.total_aegis,
            'Average aegis per s': self.avg_aegis_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class MightStat(db.Model):

    __tablename__ = 'might_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_might = db.Column(db.Integer())
    avg_might_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="might_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total might': self.total_might,
            'Average might per s': self.avg_might_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class FuryStat(db.Model):

    __tablename__ = 'fury_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_fury = db.Column(db.Integer())
    avg_fury_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="fury_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total fury': self.total_fury,
            'Average fury per s': self.avg_fury_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }

class BarrierStat(db.Model):

    __tablename__ = 'barrier_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_barrier = db.Column(db.Integer())
    avg_barrier_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="barrier_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total barrier': self.total_barrier,
            'Average barrier per s': self.avg_barrier_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class DmgTakenStat(db.Model):

    __tablename__ = 'dmg_taken_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_dmg_taken = db.Column(db.Integer())
    avg_dmg_taken_s = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="dmg_taken_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total dmg_taken': self.total_dmg_taken,
            'Average dmg_taken per s': self.avg_dmg_taken_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color,
            'Total deaths': self.player_stat.death_stat.total_deaths
        }

class DeathStat(db.Model):

    __tablename__ = 'death_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_deaths = db.Column(db.Integer())
    avg_deaths_m = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="death_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total deaths': self.total_deaths,
            'Average deaths per min': self.avg_deaths_m,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class KillsStat(db.Model):

    __tablename__ = 'kills_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total_kills = db.Column(db.Integer())
    avg_kills_m = db.Column(db.Float())

    player_stat = relationship("PlayerStat", back_populates="kills_stat")

    def to_dict(self, masked=False):
        if masked:
            if self.player_stat.character.name in session['CHARACTERS'] or current_user.is_authenticated:
                name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
            else:
                name = f'{self.player_stat.character.id:03d} | Anon ({self.player_stat.character.profession.abbreviation})'
        else:
            name = f'{self.player_stat.character.name} ({self.player_stat.character.profession.abbreviation})'
        return {
            'Name': name,
            'Times Top': self.times_top,
            'Total kills': self.total_kills,
            'Average kills per min': self.avg_kills_m,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class FightSummary(db.Model):
    __tablename__ = 'fight_summary'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    raid_id = db.Column(db.Integer(), db.ForeignKey('raid.id', ondelete="CASCADE"))
    start_time = db.Column(db.String())
    end_time = db.Column(db.String())
    duration = db.Column(db.Integer())
    skipped = db.Column(db.Integer())
    avg_allies = db.Column(db.Float())
    avg_enemies = db.Column(db.Float())
    damage = db.Column(db.Integer())
    boonrips = db.Column(db.Integer())
    cleanses = db.Column(db.Integer())
    stability = db.Column(db.Integer())
    healing = db.Column(db.Integer())
    deaths = db.Column(db.Integer())
    kills = db.Column(db.Integer())
    distance_to_tag = db.Column(db.Integer())
    protection = db.Column(db.Integer())
    aegis = db.Column(db.Integer())
    might = db.Column(db.Integer())
    fury = db.Column(db.Integer())
    barrier = db.Column(db.Integer())
    dmg_taken = db.Column(db.Integer())

    raid = relationship("Raid", back_populates="fightsummary")

    def to_dict(self):
        return {
            'Date': self.raid.raid_date,
            'Title': self.raid.name,
            'Type': self.raid.raid_type.name,
            'Kills': self.kills,
            'Deaths': self.deaths,
            '⌀ Allies': self.avg_allies,
            '⌀ Enemies': self.avg_enemies,
            'Damage': f'{self.damage:,}',
            'Boonrips': f'{self.boonrips:,}',
            'Cleanses': f'{self.cleanses:,}',
            'Stability Output': f'{self.stability:,}',
            'Healing': f'{self.healing:,}',
            'Damage Taken': f'{self.dmg_taken:,}',
        }


class User(UserMixin, db.Model):
    __tablename__ = 'odin_user'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    username = db.Column(db.String(), unique= True)
    password = db.Column(db.String())
    email = db.Column(db.String())

    def __init__(self, username):
        self.username = username