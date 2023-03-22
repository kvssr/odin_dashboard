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
    account_id = db.Column(db.Integer(), db.ForeignKey('account.id', ondelete="CASCADE"))
    
    profession = relationship("Profession", back_populates="characters")
    account = relationship("Account", back_populates='characters')
    playerstats = relationship("PlayerStat", back_populates="character")
    character_fight_stats = relationship('CharacterFightStat', back_populates='character')
    character_fight_ratings = relationship('CharacterFightRating', back_populates='character')


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
    quick_stat = relationship("QuickStat", back_populates="player_stat", uselist=False, lazy='select')
    alac_stat = relationship("AlacStat", back_populates="player_stat", uselist=False, lazy='select')
    sup_speed_stat = relationship("SupSpeedStat", back_populates="player_stat", uselist=False, lazy='select')
    stripped_stat = relationship("StrippedStat", back_populates="player_stat", uselist=False, lazy='select')

    def to_dict(self):
        return {
            'raid_id': self.raid_id,
            'Date': self.raid.raid_date,
            'Start Time': self.raid.fightsummary[0].start_time,
            'character_id': self.character_id,
            'Name': self.character.name,
            'Damage': self.dmg_stat.avg_s,
            'Rips': self.rip_stat.avg_s,
            'Cleanses': self.cleanse_stat.avg_s,
            'Stab': self.stab_stat.avg_s,
            'Heals': self.heal_stat.avg_s,
            'Sticky': f'{self.dist_stat.percentage_top}%' if self.dist_stat else '0%',
            'Prot': self.prot_stat.avg_s,
            'Aegis': self.aegis_stat.avg_s,
            'Might': self.might_stat.avg_s,
            'Fury': self.fury_stat.avg_s,
            'Barrier': self.barrier_stat.avg_s,
            'Quick': self.quick_stat.avg_s,
            'Alac': self.alac_stat.avg_s,
            'SSpeed': self.sup_speed_stat.avg_s,
            'Dmg In': self.dmg_taken_stat.times_top if self.dmg_taken_stat else None,
            'Deaths': self.death_stat.times_top,
            'Rips In': self.stripped_stat.avg_s if self.stripped_stat else None,
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
    kills = db.Column(db.Integer())
    
    raid = relationship("Raid", back_populates="fights")
    character_fight_stats = relationship('CharacterFightStat', back_populates='fight')
    character_fight_ratings = relationship('CharacterFightRating', back_populates='fight')

    def to_dict(self):
        return {
            'number': self.number + 1,
            'start time': self.start_time,
            'end time': self.end_time,
            'skipped': 'yes' if self.skipped else 'no',
            '# Allies': self.num_allies,
            '# Enemies': self.num_enemies,
            'kills': self.kills,
            'deaths': sum(stats.deaths for stats in self.character_fight_stats),
            'damage': f'{sum(stats.damage for stats in self.character_fight_stats):,}',
            'boonrips': f'{sum(stats.boonrips for stats in self.character_fight_stats):,}',
            'cleanses': f'{sum(stats.cleanses for stats in self.character_fight_stats):,}',
            'healing': f'{sum(stats.healing for stats in self.character_fight_stats):,}'
        }


class CharacterFightStat(db.Model):

    __tablename__ = 'character_fight_stat'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    fight_id = db.Column(db.Integer(), db.ForeignKey('fight.id', ondelete='CASCADE'))
    character_id = db.Column(db.Integer(), db.ForeignKey('character.id', ondelete='CASCADE'))
    build_type_id = db.Column(db.Integer(), db.ForeignKey('build_type.id', ondelete='CASCADE'))
    damage = db.Column(db.Integer())
    boonrips = db.Column(db.Integer())
    cleanses = db.Column(db.Integer())
    stability = db.Column(db.Float())
    healing = db.Column(db.Integer())
    distance_to_tag = db.Column(db.Integer())
    deaths = db.Column(db.Integer())
    protection = db.Column(db.Float())
    aegis = db.Column(db.Float())
    might = db.Column(db.Float())
    fury = db.Column(db.Float())
    barrier = db.Column(db.Integer())
    dmg_taken = db.Column(db.Integer())
    stripped = db.Column(db.Integer())
    group = db.Column(db.Integer())

    fight = relationship('Fight', back_populates='character_fight_stats')
    character = relationship('Character', back_populates='character_fight_stats')
    build_type = relationship("BuildType", back_populates='character_fight_stats')



class BaseStat(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    times_top = db.Column(db.Integer())
    percentage_top = db.Column(db.Integer())
    total = db.Column(db.Integer())
    avg_s = db.Column(db.Float())

    
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
            'Total': self.total,
            'Average per s': self.avg_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Percentage Top': self.percentage_top,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class DmgStat(BaseStat):

    __tablename__ = 'dmg_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="dmg_stat")


class RipStat(BaseStat):

    __tablename__ = 'rip_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="rip_stat")

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="rip_stat")

class CleanseStat(BaseStat):

    __tablename__ = 'cleanse_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="cleanse_stat")


class StabStat(BaseStat):

    __tablename__ = 'stab_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="stab_stat")

class HealStat(BaseStat):

    __tablename__ = 'heal_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="heal_stat")


class DistStat(BaseStat):

    __tablename__ = 'dist_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="dist_stat")


class ProtStat(BaseStat):

    __tablename__ = 'prot_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="prot_stat")


class AegisStat(BaseStat):

    __tablename__ = 'aegis_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="aegis_stat")


class MightStat(BaseStat):

    __tablename__ = 'might_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="might_stat")


class FuryStat(BaseStat):

    __tablename__ = 'fury_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="fury_stat")


class BarrierStat(BaseStat):

    __tablename__ = 'barrier_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="barrier_stat")


class DmgTakenStat(BaseStat):

    __tablename__ = 'dmg_taken_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
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
            'Total': self.total,
            'Total Deaths': self.player_stat.death_stat.total,
            'Average per s': self.avg_s,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Percentage Top': self.percentage_top,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class QuickStat(BaseStat):

    __tablename__ = 'quick_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="quick_stat")


class AlacStat(BaseStat):

    __tablename__ = 'alac_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="alac_stat")


class SupSpeedStat(BaseStat):

    __tablename__ = 'sup_speed_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="sup_speed_stat")


class DeathStat(BaseStat):

    __tablename__ = 'death_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
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
            'Total': self.total,
            'Average per m': self.avg_deaths_m,
            'Attendance (number of fights)': self.player_stat.attendance_count,
            'Profession': self.player_stat.character.profession.name,
            'Profession_color': self.player_stat.character.profession.color
        }


class KillsStat(BaseStat):

    __tablename__ = 'kills_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
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


    
class StrippedStat(BaseStat):

    __tablename__ = 'stripped_stat'

    player_stat_id = db.Column(db.Integer(), db.ForeignKey('player_stat.id', ondelete="CASCADE"), unique= True)
    player_stat = relationship("PlayerStat", back_populates="stripped_stat")



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
    healing = db.Column(db.Integer())
    deaths = db.Column(db.Integer())
    kills = db.Column(db.Integer())
    distance_to_tag = db.Column(db.Integer())
    dmg_taken = db.Column(db.Integer())
    barrier = db.Column(db.Integer())
    # Boons
    stability = db.Column(db.Float())
    protection = db.Column(db.Float())
    aegis = db.Column(db.Float())
    might = db.Column(db.Float())
    fury = db.Column(db.Float())
    quickness = db.Column(db.Float())
    alacrity = db.Column(db.Float())
    superspeed = db.Column(db.Float())
    stripped = db.Column(db.Float())    

    raid = relationship("Raid", back_populates="fightsummary")

    def to_dict(self, short = True):
        d = {
            'Date': self.raid.raid_date,
            'Start': self.start_time,
            'End': self.end_time,
            'Title': self.raid.name,
            'Type': self.raid.raid_type.name,
            'Kills': self.kills,
            'Deaths': self.deaths,
            '⌀ Allies': self.avg_allies,
            '⌀ Enemies': self.avg_enemies,
            'Damage': f'{self.damage:,}',
            'Boonrips': f'{self.boonrips:,}',
            'Cleanses': f'{self.cleanses:,}',
            'Stability Output': f'{self.stability:,.2f}',
            'Healing': f'{self.healing:,}',
        }
        if not short:
            d.update({
                'Damage Taken': f'{self.dmg_taken:,}',
                'Protections': f'{self.protection:,.2f}',
                'Aegis': f'{self.aegis:,.2f}',
                'Might': f'{self.might:,.2f}',
                'Fury': f'{self.fury:,.2f}',
                'Quickness': f'{self.quickness:,.2f}',
                'Alacrity': f'{self.alacrity:,.2f}',
#                'Superspeed': f'{self.superspeed:,.2f}'
                'Superspeed': f'{self.superspeed:,.2f}',
                'Rips Taken': f'{self.stripped:,}'
            })
        return d


class User(UserMixin, db.Model):
    __tablename__ = 'odin_user'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String())
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete="CASCADE"))
    last_checked = db.Column(db.Date())
    active = db.Column(db.Boolean(), default=True)

    role = relationship("Role", back_populates="users")

    def __init__(self, username):
        self.username = username

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.username,
            'email': self.email,
            'role': self.role.name,
            'active': self.active,
            'last_checked': self.last_checked
        }

    def to_json(self):        
        return {"name": self.username,
                "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):   
        return self.active           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id)


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String(), unique= True)
    power = db.Column(db.Integer())

    users = relationship("User", back_populates="role")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String(), unique= True)
    guild_id = db.Column(db.Integer(), db.ForeignKey("guild.id", ondelete="SET NULL"))

    characters = relationship("Character", back_populates="account")
    logs = relationship("Log", back_populates="account")
    guild = relationship('Guild', back_populates='members')


class Log(db.Model):

    __tablename__ = 'log'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    log_date = db.Column(db.Date())
    account_id = db.Column(db.Integer(), db.ForeignKey("account.id", ondelete="SET NULL"))

    account = relationship("Account", back_populates="logs")


class Guild(db.Model):

    __tablename__ = 'guild'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    api_id = db.Column(db.String())
    leader_key = db.Column(db.String())
    members_updated_last = db.Column(db.Date())

    members = relationship('Account', back_populates='guild')
    
class BuildType(db.Model):

    __tablename__ = 'build_type'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())

    character_fight_stats = relationship("CharacterFightStat", back_populates="build_type")
    character_fight_ratings = relationship("CharacterFightRating", back_populates="build_type")


class CharacterFightRating(db.Model):

    __tablename__ = 'character_fight_rating'
    
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    fight_id = db.Column(db.Integer(), db.ForeignKey('fight.id', ondelete='CASCADE'))
    character_id = db.Column(db.Integer(), db.ForeignKey('character.id', ondelete='CASCADE'))
    build_type_id = db.Column(db.Integer(), db.ForeignKey('build_type.id', ondelete='CASCADE'))
    damage = db.Column(db.Float())
    boonrips = db.Column(db.Float())
    cleanses = db.Column(db.Float())
    stability = db.Column(db.Float())
    healing = db.Column(db.Float())
    distance_to_tag = db.Column(db.Float())
    deaths = db.Column(db.Float())
    protection = db.Column(db.Float())
    aegis = db.Column(db.Float())
    might = db.Column(db.Float())
    fury = db.Column(db.Float())
    barrier = db.Column(db.Float())
    dmg_taken = db.Column(db.Float())
    stripped = db.Column(db.Float())
    group = db.Column(db.Integer())

    fight = relationship("Fight", back_populates="character_fight_ratings")
    character = relationship("Character", back_populates="character_fight_ratings")
    build_type = relationship("BuildType", back_populates="character_fight_ratings")
