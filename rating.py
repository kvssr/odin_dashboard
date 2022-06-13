import pandas as pd
from sqlalchemy import desc
from app import db
from models import Character, CharacterFightStat, Fight, Profession, Raid

_k_factor = {
    40,
    20,
    10
}


_prof_stats = {
    '': {},
}

_prof_builds = {

}



def calculate_ratings_per_fight(fight_id:int, players_df:pd.DataFrame) -> pd.DataFrame:
    for x, player_a in players_df.iterrows():
        # build = check_build(player_a)
        # players_df.loc[players_df.index == x, 'Build'] = build
        for y, player_b in players_df.iterrows():
            # print(f'{player_a=}')
            if x == y:
                print(f'{x=} - {y=}')
                continue
            #print(f'{player_a["Name"]} - {player_b["Name"]}')
            expected_score = player_a['Rating']/player_b['Rating']
            score = player_a['Damage']/player_b['Damage']
            #print(f'{score} - {expected_score}')
            new_rating = player_a['Rating'] + 20 * (score - expected_score)
            #print(new_rating)
            players_df.loc[players_df.index == x, 'Change'] += (score - expected_score)
    players_df['Rating'] += 15 * players_df['Change']
    #players_df['Change'] = 0
    print(players_df)
    # print('*'*12)
    return players_df[['Change']]


def calculate_ratings_per_raid(raid_id:int):
    fights = [fight.id for fight in db.session.query(Fight.id).filter_by(raid_id = raid_id).filter(Fight.skipped == False)]

    players2_df = pd.DataFrame(columns=['Name', 'Build', 'Change']).set_index(['Name', 'Build'])
    for fight in fights:
        # players = db.session.query(Character.name, Profession.name, CharacterFightStat.damage).filter(CharacterFightStat.fight_id==fight)\
        # .join(CharacterFightStat.character)\
        #     .join(Character.profession).filter_by(name = 'Herald').order_by(desc(CharacterFightStat.damage))

        players = db.session.query(
            Character.name, Profession.name, 
            CharacterFightStat.damage, 
            CharacterFightStat.healing,
            CharacterFightStat.stability,
            CharacterFightStat.cleanses,
            CharacterFightStat.boonrips,
            ).filter(CharacterFightStat.fight_id==fight)\
            .join(CharacterFightStat.character)\
                .join(Character.profession)

        players_df = pd.DataFrame(players, columns=['Name', 'Profession', 'Damage', 'Healing', 'Stability', 'Cleansing', 'Strips'])
        players_df['Rating'] = 1200
        players_df['Change'] = 0
        for x, player in players_df.iterrows():
            players_df.loc[players_df.index == x, 'Build'] = check_build(player)
        players_df = players_df.set_index(['Name', 'Build'])
        print(players_df)
        print(f'{fight=}')

        #players1_df = calculate_ratings_per_fight(fight, players_df)
        #players2_df = pd.concat([players2_df, players1_df]).groupby(level=['Name', 'Build']).sum()
        #print(players2_df)
        print('*'*12)

    print(fights)
    #print(players2_df)
    pass


def main():
    raids = db.session.query(Raid.id).all()
    print(f'{raids=}')
    calculate_ratings_per_raid(20)
    pass


def check_build(player:pd.Series, duration:int) -> str:
    print(f'{player["Character"]=}')
    if player['Damage'] == 0:
        return 'non'

    build = 'dmg'
    print(duration)
    stats = {
        'heal': player['Healing'] * 0.8 / player['Damage'],
        'cleanse': player['Cleansing'] * 250 / player['Damage'],
        'stab': player['Stability'] * duration * 180 / player['Damage'],
        'barrier': player['Barrier'] / (player['Damage'] * 1.5),
        'prot': player['Protection'] * duration * 100 / player['Damage'],
    }

    max_stat = max(stats, key=stats.get)
    if stats[max_stat] > 1:
        if max_stat == 'prot':
            fury = player['Fury'] * duration * 10 / player['Damage']
            if fury > 1:
                build = f'dmg {fury:.2f} - fury'
            else:
                build = f'sup {stats[max_stat]:.2f} - {max_stat}'
        else:
            build = f'sup {stats[max_stat]:.2f} - {max_stat}'
    elif sum(1 for x in stats if stats[x] > 0.65) > 1:
        build = f'sup 2x'
    else:
        build = f'dmg {stats[max_stat]:.2f} - {max_stat[0]}'
    
    return build


# calculate_ratings_per_fight(417)
#main()