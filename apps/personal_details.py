from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from flask import session
from flask_login import current_user
from app import db, app
from models import AegisStat, BarrierStat, Character, CleanseStat, DistStat, DmgTakenStat, Fight, FuryStat, HealStat, KillsStat, MightStat, Profession, ProtStat, RipStat, StabStat
from dash.dependencies import Input, Output, State
import pandas as pd
from helpers import graphs
import plotly.express as px
from dash import dash_table
from sqlalchemy import func 

from models import DeathStat, DmgStat, FightSummary, PlayerStat, Raid



tab_style={'padding': '.5rem 0',
            'cursor': 'pointer'}

colum_models = {
    'Damage': [DmgStat, 'total_dmg'],
    'Rips': [RipStat, 'total_rips'],
    'Cleanses': [CleanseStat, 'total_cleanses'],
    'Stab': [StabStat, 'total_stab'],
    'Healing': [HealStat, 'total_heal'],
    'Sticky': [DistStat, 'percentage_top'],
    'Prot': [ProtStat, 'total_prot'],
    'Aegis': [AegisStat, 'total_aegis'],
    'Might': [MightStat, 'total_might'],
    'Fury': [FuryStat, 'total_fury'],
    'Barrier': [BarrierStat, 'total_barrier'],
    'Damage Taken': [DmgTakenStat, 'times_top'],
    'Deaths': [DeathStat, 'times_top']
}


def layout(name):
    name = name.split('(')[0].rstrip()
    character_id = db.session.query(Character.id).filter_by(name = name).first()
    characters = db.session.query(Character).filter(Character.id.in_(db.session.query(PlayerStat.character_id).distinct()))\
                            .join(Profession).order_by(Profession.name, Character.name).all()
    if current_user.is_authenticated:
        dropdown_options = [{'label':f'{s.name} - {s.profession.name}', 'value':s.id} for s in characters]
    else:
        dropdown_options = [{'label':f'{s.name} - {s.profession.name}', 'value':s.id} for s in characters if s.name in session['CHARACTERS']]
    layout = [
        dbc.Row(class_name='input-row', children=[
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Raids Attended"),
                    dbc.CardBody(id='raids-attended')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Fights Attended"),
                    dbc.CardBody(id='fights-attended')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Fights Missed"),
                    dbc.CardBody(id='fights-missed')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Times Top", id='times-top-header'),
                    dbc.CardBody(id='times-top')
                ])
            ]),
        ]),
        dbc.Row(class_name='input-row', children=[
            dbc.Col(dcc.Dropdown(
                id='name-dropdown',
                options=dropdown_options,
                value=character_id[0]
            ), width={'size': 4 , 'offset': 4})
        ]),
        dbc.Row(
            dbc.Col(
                dcc.Loading(html.Div(id='raids-graph'), color='grey'),
            )
        ),
        dbc.Row([
            dbc.Col(id='personal-raids-table'),
        ]),
    ]
    return layout


@app.callback(
    Output('personal-raids-table', 'children'),
    Input('name-dropdown', 'value'),
)
def update_raids_table(character):
    raids_dict = [s.to_dict() for s in db.session.query(PlayerStat).filter_by(character_id=character).join(Raid).join(FightSummary).order_by(Raid.raid_date.desc(), FightSummary.start_time.desc()).all()]
    print(f'raids_dict: {raids_dict}')
    raids_df = pd.DataFrame(raids_dict)
    print(f'raids_df: {raids_df}')
    table = dash_table.DataTable(
                id='raids-table',
                columns=[{
                    'name': i,
                    'id': i,
                    'selectable': True if i not in ['Date', 'Start Time', 'Name'] else False,
                } for i in raids_df.columns if '_id' not in i and i not in ['Name']],
                data=raids_dict,
                editable=False,
                row_selectable='multi',
                column_selectable='single',
                cell_selectable=False,
                style_as_list_view=True,
                selected_columns=['Damage'],
                selected_rows=[s for s in range(len(raids_df))],
                #sort_action='native',
                style_cell={
                    'border': '1px solid #444',
                    'padding': '0.5rem',
                    'textAlign': 'center',
                    'font-family': 'var(--bs-body-font-family)',
                    'line-height': 'var(--bs-body-line-height)'
                },
                style_data={
                    'backgroundColor': '#424242',
                },
                style_header={
                    'backgroundColor': '#212121',
                    'textAlign': 'center',
                    'fontWeight': 'bold',
                    'border-top': '0px',
                    'border-bottom': '1px solid white',
                },
            )
    return table


@app.callback(
    Output('raids-attended', 'children'),
    Output('fights-attended', 'children'),
    Output('fights-missed', 'children'),
    Output('times-top', 'children'),
    Output('times-top-header', 'children'),
    Input('name-dropdown', 'value'),
    Input('raids-table', 'selected_columns'),
)
def update_highest_stats(character, col):
    raids_attended = db.session.query(func.count(PlayerStat.id)).filter_by(character_id=character).first()[0]
    fights_attended = db.session.query(func.sum(PlayerStat.attendance_count)).filter_by(character_id=character).first()[0] 
    fights_attended = 0 if fights_attended is None else fights_attended 

    raids = db.session.query(PlayerStat.raid_id).filter_by(character_id=character).subquery().select()
    total_fights = db.session.query(func.count(Fight.id)).filter(Fight.raid_id.in_(raids)).filter_by(skipped=False).first()[0]
    fights_missed = total_fights - fights_attended

    if col:
        model = colum_models[col[0]][0]
        times_top = db.session.query(func.sum(model.times_top)).join(PlayerStat).filter_by(character_id=character).first()[0]
    return (raids_attended, fights_attended, fights_missed, times_top, f'Times Top: {col[0]}')


@app.callback(
    Output('raids-graph', 'children'),
    Input('raids-table', 'selected_columns'),
    Input('raids-table', 'selected_rows'),
    State('raids-table', 'data'),
)
def show_selected_column(col, rows, data):
    print(f'col: {col}'),
    print(f'rows: {rows}')
    print(f'data: {data}')
    if col is not None and col[0] in colum_models:
        selected_raids = [data[s]['raid_id'] for s in rows]
        #print(f'selected raids: {selected_raids}')
        model = colum_models[col[0]][0]
        model_attr = getattr(colum_models[col[0]][0], colum_models[col[0]][1])

        df_p = pd.DataFrame(data)
        df_p['Profession_color'] = db.session.query(Character).filter_by(id = str(df_p['character_id'][0])).join(Profession).first().profession.color

        df_p = df_p[df_p['raid_id'].isin(selected_raids)]
        min_max = func.max(model_attr)

        df_top = pd.DataFrame(db.session.query(PlayerStat.raid_id, min_max.label('Damage')).join(PlayerStat).filter(PlayerStat.raid_id.in_(df_p['raid_id'])).group_by(PlayerStat.raid_id).all(),
        columns=['raid_id', col[0]])
        for i, s in df_top.iterrows():
            top_char = db.session.query(PlayerStat).filter(PlayerStat.raid_id==str(s[0])).join(model).filter(model_attr==str(s[1])).first()
            df_top.loc[df_top['raid_id'] == s['raid_id'], 'Profession_color'] = top_char.character.profession.color
            df_top.loc[df_top['raid_id'] == s['raid_id'], 'Profession'] = top_char.character.profession.name
            df_top.loc[df_top['raid_id'] == s['raid_id'], 'Date'] = db.session.query(Raid.raid_date).filter(Raid.id == str(s['raid_id'])).first()[0]
            print(f"row: {df_top.loc[df_top['raid_id'] == s['raid_id']]}")
            print(f"Date: {db.session.query(Raid.raid_date).filter(Raid.id == str(s[0])).first()[0]}")
            print(top_char)
        print(df_top)
        df_top['Name'] = '#1 Person'

        for i, row in df_p.iterrows():
            df_p = df_p.append(df_top.loc[df_top['raid_id'] == row['raid_id']])
        print(f'Color df_p: {df_p}')
        fig = graphs.get_personal_chart(df_p, col[0])
        return dcc.Graph(figure=fig, style={'height': 300})