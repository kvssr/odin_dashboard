from datetime import datetime
import pytz
from models import Account, AegisStat, AlacStat, BarrierStat, Character, CleanseStat, DeathStat, DistStat, DmgStat, DmgTakenStat, Fight, FightSummary, FuryStat, HealStat, MightStat, PlayerStat, Profession, ProtStat, QuickStat, Raid, RaidType, RipStat, StabStat, SupSpeedStat
from app import db
from helpers import graphs


stats = {
    'dmg': DmgStat,
    'aegis': AegisStat,
    'barrier': BarrierStat,
    'cleanses': CleanseStat,
    'deaths': DeathStat,
    'dist': DistStat,
    'dmg_taken': DmgTakenStat,
    'fury': FuryStat,
    'heal': HealStat,
    'might': MightStat,
    'prot': ProtStat,
    'rips': RipStat,
    'stab': StabStat,
    'quick': QuickStat,
    'alac': AlacStat,
    'speed': SupSpeedStat,
}


def write_xls_to_db(json_file, name = '' , t = 1):
    json_fights = json_file['fights']

    # start_time_utc = datetime.strptime(json_file['overall_raid_stats']['start_time'], '%H:%M:%S %z')
    # start_time_cet = start_time_utc.astimezone(pytz.timezone("CET"))

    # end_time_utc = datetime.strptime(json_file['overall_raid_stats']['end_time'], '%H:%M:%S %z')
    # end_time_cet = end_time_utc.astimezone(pytz.timezone("CET"))

    # #json_fight_date = date_time_cet.date()
    # json_raid_start_time = str(start_time_cet.timetz())
    # json_raid_end_time = str(end_time_cet.timetz())

    # print(f'start time: {json_raid_start_time}')
    # print(f'end time: {json_raid_end_time}')

    json_fight_date = json_file['overall_raid_stats']['date']
    json_raid_start_time = json_file['overall_raid_stats']['start_time']
    json_raid_end_time = json_file['overall_raid_stats']['end_time']

    try:
        raids = db.session.query(Raid.id).filter_by(raid_date=json_fight_date)
        print(f'raids: {raids}')
        raid_exists = db.session.query(FightSummary).filter(FightSummary.raid_id.in_(raids)).filter_by(start_time=json_raid_start_time).first()
        print(raid_exists)
        if raid_exists:
            print('Raid is already in the database')
            return "Raid is already in the database"
    except Exception as e:
        print('Cant check date')
        print(e)
    try:
        write_professions_to_db(graphs.profession_shorts, graphs.profession_colours)
        write_character_to_db(json_file['players'])
        write_raid_type_to_db(graphs.raid_types)

        raid_id = write_raid_to_db(json_fight_date, name, t)
        write_player_stat_to_db(json_file['players'], raid_id)
        write_fights_to_db(json_fights, raid_id)
        write_fight_summary_to_db(json_file, raid_id, json_raid_start_time, json_raid_end_time)

        # player stats
        for player in json_file['players']:
            professionId = db.session.query(Profession.id).filter_by(name=player['profession']).first()[0]
            char_id = db.session.query(Character.id).filter_by(name=player['name'], profession_id=professionId).first()[0]
            player_id = db.session.query(PlayerStat.id).filter_by(character_id = char_id, raid_id=raid_id).first()[0]
            for stat in stats:
                write_stats_to_db(player, player_id, stats[stat], stat)
        print('Updated database succesfully')
        return "Updated database successfully"
    except Exception as e:
        print(e)
        return "There was an error updating the database"


def write_raid_type_to_db(types):
    counter = 0
    for t in types:
        try:
            if db.session.query(RaidType).filter_by(name=t).first() is not None:
                print(f'Raid type {t} is already in the database')
                continue            
            raid_type = RaidType()
            raid_type.name = t
            db.session.add(raid_type)
            db.session.commit()
            counter += 1
        except Exception as e:
            db.session.rollback()
            print('Couldnt add raid_types to database')
            print(e)
        finally:
            db.session.close()
    print(f'Added {counter} new raid_types to the db')


def write_raid_to_db(raid_date, name='', raid_type=1):
    counter = 0
    try:
        raid = Raid()
        raid.name = name
        raid.raid_date = raid_date
        #raid.raid_type_id = db.session.query(RaidType.id).filter_by(name=raid_type).first()[0]
        raid.raid_type_id = raid_type
        db.session.add(raid)
        db.session.commit()
        print(f'raid_id: {raid.id}')
        counter += 1
    except Exception as e:
        db.session.rollback()
        print('Couldnt add raid to database')
        print(e)
    finally:
        db.session.close()
    print(f'Added {counter} new raids to the db')
    return raid.id


def write_professions_to_db(profs, colors):
    counter = 0
    for prof, abr in profs.items():
        try:
            if db.session.query(Profession).filter_by(name=prof).first() is not None:
                print(f'Character {prof} is already in the database')
                continue            
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
        finally:
            db.session.close()
    print(f'Added {counter} new professions to the db')


def write_character_to_db(players):
    counter = 0
    for player in players:
        try:
            char = db.session.query(Character).filter_by(name=player['name']).join(Profession).filter_by(name = player['profession']).first()
            account = db.session.query(Account).filter_by(name=player['account']).first()

            if account is None:
                account = write_account_to_db(player['account'])

            if char is not None:
                print(f'Character {player["name"]} - {player["profession"]} is already in the database')
                if char.account == None:
                    char.account = account
                    db.session.commit()
                    print(f'{char.name} has been linked to {account.name}')
                continue
            character = Character()
            character.name = player['name']
            character.profession_id = db.session.query(Profession.id).filter_by(name=player['profession']).first()[0]
            character.account = account
            db.session.add(character)
            db.session.commit()
            print(f'Added {character.name} to the database')
            counter += 1
        except Exception as e:
            db.session.rollback()
            print('Couldnt add characters to database')
            print(e)
        finally:
            db.session.close()
    print(f'Added {counter} new characters to the db')


def write_account_to_db(name):
    try:
        account = Account()
        account.name = name
        db.session.add(account)
        db.session.commit()
        return account
    except Exception as e:
        print(e)


def write_player_stat_to_db(players, raid_id):
    counter = 0
    for player in players:
        try:
            player_stat = PlayerStat()
            player_stat.raid_id = raid_id
            professionId = db.session.query(Profession.id).filter_by(name=player['profession']).first()[0]
            player_stat.character_id = db.session.query(Character.id).filter_by(name=player['name'], profession_id=professionId).first()[0]
            player_stat.attendance_count = player['num_fights_present']
            player_stat.attendance_duration = player['duration_fights_present']
            db.session.add(player_stat)
            db.session.commit()
            counter += 1
        except Exception as e:
            db.session.rollback()
            print('Couldnt add player_stat to database')
            print(e)
        finally:
            db.session.close()
    print(f'Added {counter} new player_stats to the db')


def write_fights_to_db(fights, raid_id):
    counter = 0
    date_time_end_cet = None
    for fight_row in fights:
        try:
            date_time_utc = datetime.strptime(fight_row['start_time'], '%Y-%m-%d %H:%M:%S %z')
            date_time_cet = date_time_utc.astimezone(pytz.timezone("CET"))

            json_fight_date = date_time_cet.date()
            json_fight_start_time = str(date_time_cet.timetz())

            date_time_utc = datetime.strptime(fight_row['end_time'], '%Y-%m-%d %H:%M:%S %z')
            date_time_end_cet = date_time_utc.astimezone(pytz.timezone("CET"))
            json_fight_end_time = str(date_time_end_cet.timetz())

            fight = Fight()
            fight.raid_id = raid_id
            fight.number = counter
            fight.fight_date = json_fight_date
            fight.start_time = json_fight_start_time
            fight.end_time = json_fight_end_time
            fight.skipped = fight_row['skipped']
            fight.num_allies = fight_row['allies']
            fight.num_enemies = fight_row['enemies']
            fight.damage = fight_row['total_stats']['dmg']
            fight.boonrips = fight_row['total_stats']['rips']
            fight.cleanses = fight_row['total_stats']['cleanses']
            fight.distance_to_tag = fight_row['total_stats']['dist']
            fight.stability = fight_row['total_stats']['stab']
            fight.protection = fight_row['total_stats']['prot']
            fight.aegis = fight_row['total_stats']['aegis']
            fight.might = fight_row['total_stats']['might']
            fight.fury = fight_row['total_stats']['fury']
            fight.barrier = fight_row['total_stats']['barrier']
            fight.dmg_taken = fight_row['total_stats']['dmg_taken']
            fight.healing = fight_row['total_stats']['heal']
            fight.deaths = fight_row['total_stats']['deaths']
            fight.kills = fight_row['kills']
            db.session.add(fight)
            db.session.commit()
            counter += 1
        except Exception as e:
            db.session.rollback()
            print('Couldnt add fights to database')
            print(e)
        finally:
            db.session.close()
    print(f'Added {counter} new fights to the db')


def write_fight_summary_to_db(raid, raid_id, start_time, end_time):
    try:
        fight = FightSummary()
        fight.raid_id = raid_id
        fight.start_time = start_time
        fight.end_time = end_time
        fight.kills = raid['overall_raid_stats']['total_kills']
        fight.deaths = raid['overall_squad_stats']['deaths']
        fight.duration = raid['overall_raid_stats']['used_fights_duration']
        fight.skipped = raid['overall_raid_stats']['num_skipped_fights']
        fight.avg_allies = raid['overall_raid_stats']['mean_allies']
        fight.avg_enemies = raid['overall_raid_stats']['mean_enemies']
        fight.damage = raid['overall_squad_stats']['dmg']
        fight.boonrips = raid['overall_squad_stats']['rips']
        fight.cleanses = raid['overall_squad_stats']['cleanses']
        fight.stability = raid['overall_squad_stats']['stab']
        fight.healing = raid['overall_squad_stats']['heal']
        fight.distance_to_tag = raid['overall_squad_stats']['dist']
        fight.protection = raid['overall_squad_stats']['prot']
        fight.aegis = raid['overall_squad_stats']['aegis']
        fight.might = raid['overall_squad_stats']['might']
        fight.fury = raid['overall_squad_stats']['fury']
        fight.barrier = raid['overall_squad_stats']['barrier']
        fight.dmg_taken = raid['overall_squad_stats']['dmg_taken']
        db.session.add(fight)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Couldnt add fight_summary to database')
        print(e)
    else:
        print(f'Added fight_summary to the db')
    finally:
            db.session.close()


def write_stats_to_db(json_file, player_id, stat_model, json_stat):
    try:
        stat = stat_model()
        # total_stat = setattr(stat, f'total_{json_stat}', json_file['total_stats'][json_stat])
        stat.total = json_file['total_stats'][json_stat]
        if json_stat != 'deaths':
            # setattr(stat, f'avg_{json_stat}_s', json_file['average_stats'][json_stat])
            stat.avg_s = json_file['average_stats'][json_stat]
        else:
            setattr(stat, f'avg_{json_stat}_m', json_file['average_stats'][json_stat])
        stat.player_stat_id = player_id
        stat.times_top = json_file['consistency_stats'][json_stat]
        stat.percentage_top = json_file['portion_top_stats'][json_stat] * 100

        db.session.add(stat)
        db.session.commit()
    except Exception as e:
        print(f'Couldnt add {stat} for {player_id}')
        print(e)
    finally:
        db.session.close()


def delete_raid(raid):
    try:
        db.session.query(Raid).filter_by(id = raid).delete()
        db.session.commit()
        print(f'Raid: {raid} deleted')
    except Exception as e:
        print('Couldnt delete raid')
        print(e)


def check_if_raid_exists(date, time):
    raid = db.session.query(Raid).filter_by(raid_date = date).join(FightSummary, aliased=True).filter_by(start_time=time).first()
    if raid:
        return raid
    return False


def get_raid_by_summary(date, kills, deaths):
    raid = db.session.query(Raid).filter_by(raid_date = date).join(FightSummary, aliased=True).filter_by(kills=kills, deaths=deaths).first()
    if raid:
        return raid
    return False
