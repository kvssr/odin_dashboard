import json
from os import stat
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
from dash.exceptions import PreventUpdate
import dash
from dash.dash_table.Format import Format, Scheme, Sign

from models import DeathStat, DmgStat, FightSummary, PlayerStat, Raid


tab_style={'padding': '.5rem 0',
            'cursor': 'pointer'}

config = {
    'displayModeBar': False,
    'displaylogo': False,
    'scrollZoom': False,
}

colum_models = {
    'Damage': [DmgStat, 'total_dmg', 'avg_dmg_s', 'Average dmg per s'],
    'Rips': [RipStat, 'total_rips', 'avg_rips_s', 'Average rips per s'],
    'Cleanses': [CleanseStat, 'total_cleanses', 'avg_cleanses_s', 'Average cleanses per s'],
    'Stab': [StabStat, 'total_stab', 'avg_stab_s', 'Average stab per s'],
    'Healing': [HealStat, 'total_heal', 'avg_heal_s', 'Average heal per s'],
    'Sticky': [DistStat, 'percentage_top', 'percentage_top', 'Percentage Top'],
    'Prot': [ProtStat, 'total_prot', 'avg_prot_s', 'Average prot per s'],
    'Aegis': [AegisStat, 'total_aegis', 'avg_aegis_s', 'Average aegis per s'],
    'Might': [MightStat, 'total_might', 'avg_might_s', 'Average might per s'],
    'Fury': [FuryStat, 'total_fury', 'avg_fury_s', 'Average fury per s'],
    'Barrier': [BarrierStat, 'total_barrier', 'avg_barrier_s', 'Average barrier per s'],
    'Damage Taken': [DmgTakenStat, 'times_top', 'times_top', 'Times Top'],
    'Deaths': [DeathStat, 'times_top', 'times_top', 'Times Top']
}


def layout(name):
    if current_user.is_authenticated:
        characters = db.session.query(Character).filter(Character.id.in_(db.session.query(PlayerStat.character_id).distinct()))\
                                .join(Profession).order_by(Profession.name, Character.name).all()
        dropdown_options = [{'label':f'{s.name} - {s.profession.name}', 'value':s.id} for s in characters]
    else:
        characters = db.session.query(Character).filter(Character.name.in_(session['CHARACTERS'])).filter(Character.id.in_(db.session.query(PlayerStat.character_id).distinct()))\
                                .join(Profession).order_by(Profession.name, Character.name).all()
        dropdown_options = [{'label':f'{s.name} - {s.profession.name}', 'value':s.id} for s in characters]

    character_id = 0
    if name != '':
        name = name.split('(')[0].rstrip()
        character_id = db.session.query(Character.id).filter_by(name = name).first()[0]
    elif 'CHARACTERS' in session:
        character_id = db.session.query(Character.id).filter_by(name = session['CHARACTERS'][0]).first()[0]
    else:
        character_id = dropdown_options[0]['value']
        print(dropdown_options[0]['value'])

    raids_dict = [s.to_dict() for s in db.session.query(PlayerStat).filter_by(character_id=character_id).join(Raid).join(FightSummary).order_by(Raid.raid_date.desc(), FightSummary.start_time.desc()).all()]
    #print(f'raids_dict: {raids_dict}')
    raids_df = pd.DataFrame(raids_dict)
    #print(f'raids_df: {raids_df}')

    enabled_columns = ['Date', 'Start Time', 'Damage', 'Rips', 'Cleanses', 'Stab', 'Healing', 'Sticky', 'Prot', 'Aegis', 'Might', 'Fury', 'Barrier']
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        enabled_columns = [c for c in raids_df.columns if c not in ['Name', 'character_id', 'raid_id']]


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
                value=character_id
            ), width={'size': 4 , 'offset': 4})
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Loading(html.Div(id='raids-graph'), color='grey'),
                width={'size': 8}
            ),
            dbc.Col(
                dcc.Loading(html.Div(id='raids-top10'), color='grey'),
                id='raids-top10-col',
                width={'size': 4}
            )
        ]),
        dbc.Row([
            dbc.Col(id='personal-raids-table', children=[
                dash_table.DataTable(
                id='pers-raids-table',
                columns=[{
                    'name': f'{i}*' if i in ['Healing', 'Barrier'] else i,
                    'id': i,
                    'selectable': True if i not in ['Date', 'Start Time', 'Name'] else False,
                } for i in enabled_columns],
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
            ]),
        ]),
        dbc.Row(
            dbc.Col([
                html.P(children=([f'*The healing and barrier stat will only show values for people that run ', html.A("the healing addon", href="https://github.com/Krappa322/arcdps_healing_stats/releases", target='_blank')]), id='footnote-heal-barrier', className='text-center sm'),
                
            ])
        )
    ]
    return layout


@app.callback(
    Output('pers-raids-table', 'data'),
    Input('name-dropdown', 'value'),
)
def update_raids_table(character):
    raids_dict = [s.to_dict() for s in db.session.query(PlayerStat).filter_by(character_id=character).join(Raid).join(FightSummary).order_by(Raid.raid_date.desc(), FightSummary.start_time.desc()).all()]
    return raids_dict


@app.callback(
    Output('raids-attended', 'children'),
    Output('fights-attended', 'children'),
    Output('fights-missed', 'children'),
    Output('times-top', 'children'),
    Output('times-top-header', 'children'),
    Input('name-dropdown', 'value'),
    Input('pers-raids-table', 'selected_columns'),
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
    Input('pers-raids-table', 'selected_columns'),
    Input('pers-raids-table', 'derived_virtual_selected_rows'),
    Input('pers-raids-table', 'data'),
)
def show_selected_column(col, rows, data):
    print(f'col: {col}'),
    print(f'rows: {rows}')
    print(f'data: {data}')
    if col is not None and col[0] in colum_models:
        selected_raids = [data[s]['raid_id'] for s in rows]

        # Get model and attribute depending on selected column
        model = colum_models[col[0]][0]
        model_attr = getattr(colum_models[col[0]][0], colum_models[col[0]][2])

        df_p = pd.DataFrame(data)
        df_p['mode'] = 'markers+lines'
        df_p['fill'] = 'none'
        profession = db.session.query(Character).filter_by(id = str(df_p['character_id'][0])).join(Profession).first().profession
        df_p['Profession_color'] = profession.color
        df_p['Profession'] = profession.name

        df_p = df_p[df_p['raid_id'].isin(selected_raids)]
        min_max = func.max(model_attr)
   
        for raid in df_p['raid_id']:
            raid_date = df_p.loc[df_p['raid_id']==raid, 'Date'].item()
            raid_time = df_p.loc[df_p['raid_id']==raid, 'Start Time'].item()
            raid_date = f'{raid_date} {raid_time}'
            
            df_p.loc[df_p['raid_id']==raid, 'Date'] = raid_date
            if col[0] == 'Sticky':
                df_p.loc[df_p['raid_id']==raid, col[0]] = int(df_p.loc[df_p['raid_id']==raid, col[0]].item().split('%')[0])

            ### Get Lowest Profession
            bot_prof_value = db.session.query(func.min(model_attr)).join(PlayerStat).filter_by(raid_id=raid).join(Character).join(Profession).filter_by(name=profession.name).group_by(PlayerStat.raid_id).scalar()
            df_bot_prof = pd.DataFrame(
                [[raid, raid_date, 'Last Prof', bot_prof_value, profession.color, profession.name, 'lines', 'none']],
                columns=['raid_id', 'Date', 'Name', col[0], 'Profession_color', 'Profession', 'mode', 'fill']
            )
            df_p = df_p.append(df_bot_prof)

            ### Get Top Profession
            top_prof_value = db.session.query(min_max).join(PlayerStat).filter_by(raid_id=raid).join(Character).join(Profession).filter_by(name=profession.name).group_by(PlayerStat.raid_id).scalar()
            df_top_prof = pd.DataFrame(
                [[raid, raid_date, 'First Prof', top_prof_value, profession.color, profession.name, 'none', 'tonextx']],
                columns=['raid_id', 'Date', 'Name', col[0], 'Profession_color', 'Profession', 'mode', 'fill']
            )
            df_p = df_p.append(df_top_prof)

            ### Get Top Player
            top_value = db.session.query(min_max).join(PlayerStat).filter_by(raid_id=raid).group_by(PlayerStat.raid_id).scalar()
            top_char = db.session.query(Character).join(PlayerStat).filter_by(raid_id=raid).join(model).filter(model_attr==top_value).first()
            profession2 = top_char.profession.name
            profession_color = top_char.profession.color
            df_top_n = pd.DataFrame([[raid, raid_date, '#1 Person', top_value, profession_color, profession2, 'lines', 'none']], 
                columns=['raid_id', 'Date', 'Name', col[0], 'Profession_color', 'Profession', 'mode', 'fill'])
            df_p = df_p.append(df_top_n.head())

        fig = graphs.get_personal_chart(df_p, col[0])
        return dcc.Graph(id='personal-graph',figure=fig, style={'height': 500}, config=config)


@app.callback(
    Output('raids-top10', 'children'),
    Output("pers-raids-table", "style_data_conditional"),
    Input('personal-graph', 'hoverData'),
    State('pers-raids-table', 'selected_columns'),
    State('pers-raids-table', 'selected_rows'),
    State('pers-raids-table', 'data'),)
def display_hover_data(hoverData, col, rows, data):
    if hoverData:        
        masked = True
        if current_user.is_authenticated:
            masked = False

        raid = hoverData['points'][0]['customdata']
        raid_date = hoverData['points'][0]['x']
        selected_raid = [s for s in rows if data[s]['raid_id']==raid]
        model = colum_models[col[0]][0]
        model_attr = getattr(colum_models[col[0]][0], colum_models[col[0]][2])
        stat_list = db.session.query(model).order_by(-model_attr).join(PlayerStat).join(Raid).filter_by(id = raid).limit(10).all()
        df = pd.DataFrame([s.to_dict(masked) if i > 4 else s.to_dict() for i, s in enumerate(stat_list)])
        fig = graphs.get_top_bar_chart_p(df, colum_models[col[0]][3], raid_date)
        highlight = [{"if": {"row_index":selected_raid[0]}, "backgroundColor": "grey"},]

        return dcc.Graph(figure=fig, style=dict(height='500px')), highlight
    raise PreventUpdate


@app.callback(
    Output('pers-raids-table', 'selected_rows'),
    Input('pers-raids-table', 'data'),
)
def select_all_rows(data):
    if data:
        rows = [s for s in range(len(data))]
        print(f'DATA::::{rows}')
        return rows

