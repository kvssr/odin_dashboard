import pandas as pd
from app import db
from models import Character, CharacterFightRating, CharacterFightStat, Fight, Profession, Raid


_features = [
    'Damage',
    'Boonrips',
    'Cleanses',
    'Stability',
    'Healing',
    'Protection',
    'Aegis',
    'Might',
    'Fury',
    'Barrier',
]


def calculate_ratings_per_fight(fight_id:int, players_df:pd.DataFrame) -> pd.DataFrame:
    with pd.ExcelWriter('output.xlsx', mode='a') as writer: 
        for feature in _features:
            players_df[f'{feature}_c'] = 0
            players_df['Count'] = 0
            for x, player_a in players_df.iterrows():
                if player_a[feature] == 0:
                    continue
                filter = players_df.xs(x[1], level=1, drop_level=False)
                player_count = filter.loc[players_df['Profession'] == player_a['Profession']]
                player_count = len(player_count)
                if player_a['Count'] >= player_count - 1:
                    # print(f'{player_count=} : CONTINUE - {player_a["Profession"]}')
                    continue
                for y, player_b in players_df.iterrows():
                    if x[0] == y[0]: # if it's the same character
                        continue
                    if player_b[feature] == 0:
                        continue
                    if player_a['Profession'] != player_b['Profession']:
                        continue
                    if x[1] != y[1]: # If build is not the same type
                        continue
                    if player_b['Count'] >= player_count - 1:
                        continue
                    expected_score = player_a[f'{feature.lower()}_r']/player_b[f'{feature.lower()}_r']
                    score = player_a[feature]/player_b[feature]
                    change_a = max(-20, min(20, (score - expected_score)))
                    change_b = max(-20, min(20, (expected_score - score)))
                    #new_rating = player_a['Rating'] + 20 * (score - expected_score)
                    players_df.loc[players_df.index == x, f'{feature}_c'] += change_a
                    players_df.loc[players_df.index == y, f'{feature}_c'] += change_b
                    players_df.loc[players_df.index == x, 'Count'] += 1
                    players_df.loc[players_df.index == y, 'Count'] += 1

                    # print(f'Player_a: {x[0]} \t Player_b: {y[0]}')
                    # print(f'Player_a_rating: {player_a[f"{feature.lower()}_r"]} \t Player_b_rating: {player_b[f"{feature.lower()}_r"]}')
                    # print(f'Player_a_value: {player_a[feature]} \t Player_b_value: {player_b[feature]}')
                    # print(f'Score: {score} \t Expected: {expected_score}')
            #players_df['Rating'] += 15 * players_df['Change']
            #players_df['Change'] = 0
            # print('*'*12)
        #print(players_change_df)
        
        # players_df.to_excel(writer, sheet_name=f'fight_{fight_id}')
        for x, character in players_df.iterrows():
            update_db_rating(x, fight_id, character)
            
    return players_df


def update_db_rating(index, fight_id, char_df:pd.DataFrame):
    prof_id = db.session.query(Profession.id).filter_by(name = char_df['Profession']).first()[0]
    char_id = db.session.query(Character.id).filter_by(name = index[0]).filter_by(profession_id = prof_id).first()[0]
    char_rating = CharacterFightRating(
        fight_id        = fight_id,
        character_id    = char_id,
        build_type_id   = index[1],
        damage          = max(1, char_df['damage_r'] + char_df['Damage_c']),
        boonrips        = max(1, char_df['boonrips_r'] + char_df['Boonrips_c']),
        cleanses        = max(1, char_df['cleanses_r'] + char_df['Cleanses_c']),
        stability       = max(1, char_df['stability_r'] + char_df['Stability_c']),
        healing         = max(1, char_df['healing_r'] + char_df['Healing_c']),
        protection      = max(1, char_df['protection_r'] + char_df['Protection_c']),
        aegis           = max(1, char_df['aegis_r'] + char_df['Aegis_c']),
        might           = max(1, char_df['might_r'] + char_df['Might_c']),
        fury            = max(1, char_df['fury_r'] + char_df['Fury_c']),
        barrier         = max(1, char_df['barrier_r'] + char_df['Barrier_c']),
        group           = char_df['Group']
    )
    try:
        db.session.add(char_rating)
        db.session.commit()
    except Exception as e:
        print(e)
        

def calculate_ratings_per_raid(raid_id:int):
    fights = [fight.id for fight in db.session.query(Fight.id).filter_by(raid_id = raid_id).filter(Fight.skipped == False)]
    ratings_exist = db.session.query(CharacterFightRating.id).filter(CharacterFightRating.fight_id.in_(fights)).first()
    if ratings_exist != None:
        print('This raid already has ratings')
        return
    # excel_df = pd.DataFrame()
    # excel_df.to_excel('output.xlsx')
    players2_df = pd.DataFrame(columns=['Name', 'Build', 'Change']).set_index(['Name', 'Build'])
    for fight in fights:

        players = db.session.query(
            Character.name, 
            Profession.name, 
            CharacterFightStat.build_type_id,
            CharacterFightStat.group,
            CharacterFightStat.damage, 
            CharacterFightStat.boonrips, 
            CharacterFightStat.cleanses,
            CharacterFightStat.stability,
            CharacterFightStat.healing,
            CharacterFightStat.protection, 
            CharacterFightStat.aegis, 
            CharacterFightStat.might, 
            CharacterFightStat.fury, 
            CharacterFightStat.barrier, 
            ).filter(CharacterFightStat.fight_id==fight)\
            .join(CharacterFightStat.character)\
                .join(Character.profession)

        players_df = pd.DataFrame(players, columns=['Name', 'Profession', 'Build', 'Group']+_features)


        players_df['Change'] = 0
        players_df = players_df.set_index(['Name', 'Build'])
        get_players_ratings(players_df)
        print(f'{fight=}')

        players1_df = calculate_ratings_per_fight(fight, players_df)
        players2_df = pd.concat([players2_df, players1_df]).groupby(level=['Name', 'Build']).sum()
        #print(players2_df)
        print('*'*12)

    print(fights)
    #print(players2_df)
    # players2_df.to_csv('file2.csv')
    # with pd.ExcelWriter('output.xlsx', mode='a') as writer: 
    #     players2_df.to_excel(writer, sheet_name='Overview')


def get_players_ratings(players_df:pd.DataFrame) -> pd.DataFrame:
    columns = [c for c in CharacterFightRating.__table__.columns.keys() if c not in ['id', 'fight_id', 'character_id', 'build_type_id', 'group']]
    for column in columns:
        players_df[f'{column}_r'] = 1200
    for x, player in players_df.iterrows():
        char_id = db.session.query(Character.id).filter_by(name = x[0]).first()[0]
        ratings = db.session.query(CharacterFightRating).filter_by(character_id = char_id).filter_by(build_type_id = x[1]).order_by(CharacterFightRating.id.desc()).first()
        if ratings != None:
            # print(f'{type(ratings)=}')
            # print(f'{ratings.id=}')
            for column in columns:
                # print(f'{getattr(ratings, column)}=')
                players_df.loc[players_df.index == x, f'{column}_r'] = getattr(ratings, column)
    print(f'{players_df.head()}')


def main():
    raids = db.session.query(Raid.id).order_by(Raid.raid_date).all()
    print(f'{raids=}')
    for raid in raids:
        print(f'Raids: {raid}')
        calculate_ratings_per_raid(raid[0])


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
if __name__ == "__main__":
    main()