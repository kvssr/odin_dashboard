from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from app import db, app
from models import AegisStat, BarrierStat, Character, CleanseStat, DistStat, DmgTakenStat, FuryStat, HealStat, KillsStat, MightStat, ProtStat, RipStat, StabStat
from dash.dependencies import Input, Output, State
import pandas as pd
from helpers import graphs
import plotly.express as px
from dash import dash_table
from sqlalchemy import func 

from models import DeathStat, DmgStat, FightSummary, PlayerStat, Raid



tab_style={'padding': '.5rem 0',
            'cursor': 'pointer'}


def layout(name):
    name = name.split('(')[0].rstrip()
    character_id = db.session.query(Character.id).filter_by(name = name).first()
    print(character_id[0])
    characters = db.session.query(Character).all()
    dropdown_options = [{'label':f'{s.name} - {s.profession.name}', 'value':s.id} for s in characters]
    layout = [
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Most Damage"),
                    dbc.CardBody(id='most_dmg')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Most Kills"),
                    dbc.CardBody(id='most_kills')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Least Deaths"),
                    dbc.CardBody(id='least_deaths')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Total Raids"),
                    dbc.CardBody(id='total_raids')
                ])
            ]),
        ]),
        dbc.Row([
            dbc.Col(name, width={'size': 4, 'offset': 4})
        ]),
        dbc.Row(class_name='input-row', children=[
            dbc.Col(dcc.Dropdown(
                id='name-dropdown',
                options=dropdown_options,
                value=character_id[0]
            ), width={'size': 4 , 'offset': 4})
        ]),
        html.Div(id='test-col'),
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
                    'selectable': True
                } for i in raids_df.columns if '_id' not in i],
                data=raids_dict,
                editable=False,
                row_selectable='multi',
                column_selectable='single',
                cell_selectable=False,
                style_as_list_view=True,
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
    Output('most_dmg', 'children'),
    Output('most_kills', 'children'),
    Output('least_deaths', 'children'),
    Output('total_raids', 'children'),
    Input('name-dropdown', 'value')
)
def update_highest_stats(character):
    most_dmg = f'{db.session.query(func.max(DmgStat.total_dmg)).join(PlayerStat).filter_by(character_id=character).first()[0]:,}'
    most_kills = db.session.query(func.max(KillsStat.total_kills)).join(PlayerStat).filter_by(character_id=character).first()[0]
    least_deaths = db.session.query(func.min(DeathStat.total_deaths)).join(PlayerStat).filter_by(character_id=character).first()[0]
    total_raids = db.session.query(func.count(Raid.id)).join(PlayerStat).filter_by(character_id=character).first()[0]
    return (most_dmg, most_kills, least_deaths, total_raids)


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
    'Damage Taken': [DmgTakenStat, 'total_dmg_taken'],
    'Deaths': [DeathStat, 'total_deaths']
}

@app.callback(
    Output('test-col', 'children'),
    Input('raids-table', 'selected_columns'),
    Input('raids-table', 'selected_rows'),
    State('raids-table', 'data'),
    State('name-dropdown', 'placeholder')
)
def show_selected_column(col, rows, data, name):
    print(f'col: {col}'),
    print(f'vcol: {rows}')
    print(f'data: {data}')
    if col is not None and col[0] in colum_models:
        model = colum_models[col[0]][0]
        model_attr = getattr(colum_models[col[0]][0], colum_models[col[0]][1])
        df_p = pd.DataFrame(data)
        df_top = pd.DataFrame(
            db.session.query(func.max(model_attr), Raid.raid_date, FightSummary.start_time)
                .join(PlayerStat, model.player_stat_id == PlayerStat.id)
                .join(Raid, Raid.id == PlayerStat.raid_id)
                .join(FightSummary, FightSummary.raid_id == Raid.id)
                .group_by(Raid.raid_date, FightSummary.start_time)
                .order_by(Raid.raid_date.desc(), FightSummary.start_time.desc()).all(),
            columns=[col[0], 'Date', 'Time']
            )
        df_top['Name'] = 'Top'
        for i, row in df_p.iterrows():
            df_p = df_p.append(df_top.loc[df_top['Date'].astype(str) == row['Date']])
        fig = graphs.get_personal_chart(df_p, col[0])
        return dcc.Graph(figure=fig, style={'height': 300})
