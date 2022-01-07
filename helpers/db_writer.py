import io
from numpy import character
import pandas as pd

from models import Character, Fight, Profession
from app import db


def write_xls_to_db(xls):
    write_character_to_db(pd.read_excel(io.BytesIO(xls), sheet_name='dmg'))
    pass


def write_character_to_db(df):
    try:
        for index, row in df.iterrows():
            if index >= len(df) - 1:
                continue
            character = Character()
            character.name = row['Name']
            db.session.add(character)
            db.session.commit()
    except Exception as e:
        print('Couldnt add fights to database')
        print(e)
    pass

def write_fights_to_db(df):
    try:
        for index, row in df.iterrows():
            print(f'index:{index} - {len(df)}')
            if index >= len(df) - 1:
                continue
            fight = Fight()
            print(f'row: {row}')
            fight.fight_date = row['Date']
            fight.start_time = row['Start Time']
            fight.end_time = row['End Time']
            fight.skipped = 0
            fight.num_allies = row['Num. Allies']
            db.session.add(fight)
            db.session.commit()
    except Exception as e:
        print('Couldnt add fights to database')
        print(e)
    pass

def write_dmg_to_db(df):
    pass

def write_rips_to_db(df):
    pass

def write_cleanses_to_db(df):
    pass

def write_heal_to_db(df):
    pass

def write_dist_to_db(df):
    pass

def write_stab_to_db(df):
    pass

def write_prot_to_db(df):
    pass

def write_aegis_to_db(df):
    pass

def write_might_to_db(df):
    pass

def write_fury_to_db(df):
    pass

def write_barrier_to_db(df):
    pass

def write_dmg_taken_to_db(df):
    pass

def write_deaths_to_db(df):
    pass

def write_kills_to_db(df):
    pass
