import io
from threading import Barrier
from flask_sqlalchemy.model import Model
from numpy import character, e
import pandas as pd
from sqlalchemy.orm import session

from models import AegisStat, BarrierStat, Character, CleanseStat, DeathStat, DistStat, DmgStat, DmgTakenStat, Fight, FightSummary, FuryStat, HealStat, KillsStat, MightStat, PlayerStat, Profession, ProtStat, Raid, RaidType, RipStat, StabStat
from app import db, server
from helpers import graphs


def write_xls_to_db(xls):
    df_fights = pd.read_excel(io.BytesIO(xls), sheet_name='fights overview')
    xls_fight_date = df_fights['Date'][0]
    xls_fight_time = df_fights['Start Time'][0]
    try:
        db_fight_date = str(db.session.query(Fight.fight_date).first()[0])
        db_fight_time = str(db.session.query(Fight.start_time).first()[0])
        print(f'db_date: {db_fight_date} - xls_date: {xls_fight_date}')
        print(f'db_time: {db_fight_time} - xls_time: {xls_fight_time}')
        if((db_fight_date == xls_fight_date) and (db_fight_time == xls_fight_time)):
            print('Database is up to date')
            return "The Database is up-to-date"
    except Exception as e:
        print('Cant check date')
        print(e)

    try:
        recreate_tables()
        write_professions_to_db(graphs.profession_shorts, graphs.profession_colours)
        write_character_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='dmg'))
        
        write_raid_type_to_db(graphs.raid_types)
        raid_id = write_raid_to_db(xls_fight_date)
        write_player_stat_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='dmg'), raid_id)
        write_fights_to_db(df_fights, raid_id)
        write_fight_summary_to_db(df_fights.iloc[-1], raid_id)

        # player stats
        write_dmg_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='dmg'), raid_id)
        write_rips_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='rips'), raid_id)
        write_cleanses_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='cleanses'), raid_id)
        write_heal_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='heal'), raid_id)
        write_dist_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='dist'), raid_id)
        write_stab_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='stab'), raid_id)
        write_prot_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='prot'), raid_id)
        write_aegis_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='aegis'), raid_id)
        write_might_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='might'), raid_id)
        write_fury_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='fury'), raid_id)
        write_barrier_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='barrier'), raid_id)
        write_dmg_taken_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='dmg_taken'), raid_id)
        write_deaths_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='deaths'), raid_id)
        write_kills_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='kills'), raid_id)

        return "Updated database successfully"
    except Exception as e:
        print(e)
        return "There was an error updating the database"


def write_raid_type_to_db(types):
    counter = 0
    try:
        for t in types:
            raid_type = RaidType()
            raid_type.name = t
            db.session.add(raid_type)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add raid_types to database')
        print(e)
    print(f'Added {counter} new raid_types to the db')


def write_raid_to_db(raid_date, raid_type='guild', name=''):
    counter = 0
    try:
        raid = Raid()
        raid.name = name
        raid.raid_date = raid_date
        raid.raid_type_id = db.session.query(RaidType.id).filter_by(name=raid_type).first()[0]
        db.session.add(raid)
        db.session.commit()
        print(f'raid_id: {raid.id}')
        counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add raid to database')
        print(e)
    print(f'Added {counter} new raids to the db')
    return raid.id


def write_professions_to_db(profs, colors):
    counter = 0
    try:
        for prof, abr in profs.items():
            profession = Profession()
            profession.name = prof
            profession.abbreviation = abr
            profession.color = colors[prof]
            db.session.add(profession)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add professions to database')
        print(e)
    print(f'Added {counter} new professions to the db')


def write_character_to_db(df):
    counter = 0
    try:
        for index, row in df.iterrows():
            character = Character()
            character.name = row['Name']
            character.profession_id = db.session.query(Profession.id).filter_by(name=row['Profession']).first()[0]
            db.session.add(character)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add characters to database')
        print(e)
    print(f'Added {counter} new characters to the db')


def write_player_stat_to_db(df, raid_id):
    counter = 0
    try:
        for index, row in df.iterrows():
            player_stat = PlayerStat()
            player_stat.raid_id = raid_id
            player_stat.character_id = db.session.query(Character.id).filter_by(name=row['Name'])
            player_stat.attendance_count = row['Attendance (number of fights)']
            player_stat.attendance_duration = row['Attendance (duration fights)']
            db.session.add(player_stat)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add player_stat to database')
        print(e)
    print(f'Added {counter} new player_stats to the db')


def write_fights_to_db(df, raid_id):
    counter = 0
    try:
        for index, row in df.iterrows():
            #print(f'index:{index} - {len(df)}')
            if index >= len(df) - 1:
                continue
            fight = Fight()
            #print(f'row: {row}')
            fight.raid_id = raid_id
            fight.number = row['#']
            fight.fight_date = row['Date']
            fight.start_time = row['Start Time']
            fight.end_time = row['End Time']
            fight.skipped = False if row['Skipped'] == 'no' else True
            fight.num_allies = row['Num. Allies']
            fight.num_enemies = row['Num. Enemies']
            fight.damage = row['Damage']
            fight.boonrips = row['Boon Strips']
            fight.cleanses = row['Condition Cleanses']
            fight.distance_to_tag = row['Distance to Tag']
            fight.stability = row['Stability Output']
            fight.protection = row['Protection Output']
            fight.aegis = row['Aegis Output']
            fight.might = row['Might Output']
            fight.fury = row['Fury Output']
            fight.barrier = row['Barrier']
            fight.dmg_taken = row['Damage Taken']
            fight.healing = row['Healing']
            fight.deaths = row['Deaths']
            fight.kills = row['Kills']
            db.session.add(fight)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add fights to database')
        print(e)
    print(f'Added {counter} new fights to the db')


def write_fight_summary_to_db(df, raid):
    try:
        fight = FightSummary()
        fight.raid_id = raid
        fight.kills = int(df['Kills'])
        fight.deaths = int(df['Deaths'])
        fight.duration = int(df['Duration in s'])
        fight.skipped = int(df['Skipped'])
        fight.avg_allies = df['Num. Allies'].astype(float)
        fight.avg_enemies = df['Num. Enemies'].astype(float)
        fight.damage = int(df['Damage'])
        fight.boonrips = int(df['Boon Strips'])
        fight.cleanses = int(df['Condition Cleanses'])
        fight.stability = int(df['Stability Output'])
        fight.healing = int(df['Healing'])
        fight.distance_to_tag = int(df['Distance to Tag'])
        fight.protection = int(df['Protection Output'])
        fight.aegis = int(df['Aegis Output'])
        fight.might = int(df['Might Output'])
        fight.fury = int(df['Fury Output'])
        fight.barrier = int(df['Barrier'])
        fight.dmg_taken = int(df['Damage Taken'])
        db.session.add(fight)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Couldnt add fight_summary to database')
        print(e)
    else:
        print(f'Added fight_summary to the db')


def write_dmg_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            dmgstat = DmgStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            dmgstat.player_stat_id = player_id
            dmgstat.times_top = row['Times Top']
            dmgstat.percentage_top = row['Percentage Top']
            dmgstat.total_dmg = row['Total dmg']
            dmgstat.avg_dmg_s = row['Average dmg per s']

            db.session.add(dmgstat)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add dmg_stat to database')
        print(e)
    print(f'Added {counter} new dmg_stats to the db')


def write_rips_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            rips = RipStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            rips.player_stat_id = player_id
            rips.times_top = row['Times Top']
            rips.percentage_top = row['Percentage Top']
            rips.total_rips = row['Total rips']
            rips.avg_rips_s = row['Average rips per s']

            db.session.add(rips)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add rip_stat to database')
        print(e)
    print(f'Added {counter} new rip_stats to the db')


def write_cleanses_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            cleanses = CleanseStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            cleanses.player_stat_id = player_id
            cleanses.times_top = row['Times Top']
            cleanses.percentage_top = row['Percentage Top']
            cleanses.total_cleanses = row['Total cleanses']
            cleanses.avg_cleanses_s = row['Average cleanses per s']

            db.session.add(cleanses)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add cleanse_stat to database')
        print(e)
    print(f'Added {counter} new cleanse_stats to the db')


def write_heal_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            heal = HealStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            heal.player_stat_id = player_id
            heal.times_top = row['Times Top']
            heal.percentage_top = row['Percentage Top']
            heal.total_heal = row['Total heal']
            heal.avg_heal_s = row['Average heal per s']

            db.session.add(heal)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add heal_stat to database')
        print(e)
    print(f'Added {counter} new heal_stats to the db')


def write_dist_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            dist = DistStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            dist.player_stat_id = player_id
            dist.times_top = row['Times Top']
            dist.percentage_top = row['Percentage Top']
            dist.total_dist = row['Total dist']
            dist.avg_dist_s = row['Average dist per s']

            db.session.add(dist)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add dist_stat to database')
        print(e)
    print(f'Added {counter} new dist_stats to the db')


def write_stab_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            stab = StabStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            stab.player_stat_id = player_id
            stab.times_top = row['Times Top']
            stab.percentage_top = row['Percentage Top']
            stab.total_stab = row['Total stab']
            stab.avg_stab_s = row['Average stab per s']

            db.session.add(stab)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add stab_stat to database')
        print(e)
    print(f'Added {counter} new stab_stats to the db')


def write_prot_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            prot = ProtStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            prot.player_stat_id = player_id
            prot.times_top = row['Times Top']
            prot.percentage_top = row['Percentage Top']
            prot.total_prot = row['Total prot']
            prot.avg_prot_s = row['Average prot per s']

            db.session.add(prot)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add prot_stat to database')
        print(e)
    print(f'Added {counter} new prot_stats to the db')

def write_aegis_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            aegis = AegisStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            aegis.player_stat_id = player_id
            aegis.times_top = row['Times Top']
            aegis.percentage_top = row['Percentage Top']
            aegis.total_aegis = row['Total aegis']
            aegis.avg_aegis_s = row['Average aegis per s']

            db.session.add(aegis)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add aegis_stat to database')
        print(e)
    print(f'Added {counter} new aegis_stats to the db')


def write_might_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            might = MightStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            might.player_stat_id = player_id
            might.times_top = row['Times Top']
            might.percentage_top = row['Percentage Top']
            might.total_might = row['Total might']
            might.avg_might_s = row['Average might per s']

            db.session.add(might)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add might_stat to database')
        print(e)
    print(f'Added {counter} new might_stats to the db')


def write_fury_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            fury = FuryStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            fury.player_stat_id = player_id
            fury.times_top = row['Times Top']
            fury.percentage_top = row['Percentage Top']
            fury.total_fury = row['Total fury']
            fury.avg_fury_s = row['Average fury per s']

            db.session.add(fury)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add fury_stat to database')
        print(e)
    print(f'Added {counter} new fury_stats to the db')


def write_barrier_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            barrier = BarrierStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            barrier.player_stat_id = player_id
            barrier.times_top = row['Times Top']
            barrier.percentage_top = row['Percentage Top']
            barrier.total_barrier = row['Total barrier']
            barrier.avg_barrier_s = row['Average barrier per s']

            db.session.add(barrier)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add barrier_stat to database')
        print(e)
    print(f'Added {counter} new barrier_stats to the db')


def write_dmg_taken_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            dmg_taken = DmgTakenStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            dmg_taken.player_stat_id = player_id
            dmg_taken.times_top = row['Times Top']
            dmg_taken.percentage_top = row['Percentage Top']
            dmg_taken.total_dmg_taken = row['Total dmg_taken']
            dmg_taken.avg_dmg_taken_s = row['Average dmg_taken per s']

            db.session.add(dmg_taken)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add dmg_taken_stat to database')
        print(e)
    print(f'Added {counter} new dmg_taken_stats to the db')


def write_deaths_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            deaths = DeathStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            deaths.player_stat_id = player_id
            deaths.times_top = row['Times Top']
            deaths.percentage_top = row['Percentage Top']
            deaths.total_deaths = row['Total deaths']
            deaths.avg_deaths_m = row['Average deaths per min']

            db.session.add(deaths)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add deaths_stat to database')
        print(e)
    print(f'Added {counter} new deaths_stats to the db')


def write_kills_to_db(df, raid):
    counter = 0
    try:
        for index, row in df.iterrows():
            kills = KillsStat()

            char_id = db.session.query(Character.id).filter_by(name=row['Name']).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid).first()[0]

            kills.player_stat_id = player_id
            kills.times_top = row['Times Top']
            kills.percentage_top = row['Percentage Top']
            kills.total_kills = row['Total kills']
            kills.avg_kills_m = row['Average kills per min']

            db.session.add(kills)
            db.session.commit()
            counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add kills_stat to database')
        print(e)
    print(f'Added {counter} new kills_stats to the db')


def recreate_tables():
    try:
        print('#################')
        session.close_all_sessions()
        print('Dropping tables')
        db.metadata.drop_all(db.engine)
        db.session.commit()
        print('Creating tables')
        db.metadata.create_all(db.engine)
        print('#################')
    except Exception as e:
        print(e)
