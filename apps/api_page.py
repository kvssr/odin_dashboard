import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from flask import session
from numpy import character, place
from dash.dependencies import Input, Output, State
import pandas as pd
import requests
from dash import dash_table
from sqlalchemy import distinct, func

from app import app, db
from models import Character, PlayerStat


layout = dbc.Row([
    dbc.Row(id='api-explain-row', children=[
        dbc.Col([
            html.H1('Add your API Key'),
            html.P([f'You can create and API Key at https://account.arena.net/applications.',
                html.Br(),
                'Make sure you select the characters permission.']
                ),
        ])
    ]),
    dbc.Row(id='api-add-row', class_name='input-row',children=[
        dcc.Loading(dbc.Col(id='api-add-col', children=[
            dbc.Input(id='api-input', placeholder='Put your API Key here'),
            dbc.Button("Add", id='api-btn'),
            html.Div(id='api-msg', style={'display': 'none'})
        ], width={'size': 4, 'offset': 4}), color='grey')
    ]),
    dbc.Row(id='api-overview-row', children=[
        dbc.Col(id='api-overview-col', children=(
            dcc.Loading(dash_table.DataTable(
                id='api-table',
                columns=[{
                    'name': i,
                    'id': i,
                } for i in ['Account', 'Key', 'Characters']],
                editable=False,
                row_deletable=True,
                cell_selectable=False,
                style_as_list_view=True,
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
                    'border-bottom': '1px solid white'
                },
            ), color='grey')
        ), width={'size': 10, 'offset': 1}),
        html.Div(id='api-delete-msg', style={'display': 'none'})
    ]),
    dbc.Row(id='api-characters-row', children=[
        html.H1('Characters'),
        dbc.Col(id='api-characters-col', children=(
            dcc.Loading(dash_table.DataTable(
                id='character-table',
                columns=[{
                    'name': i,
                    'id': i,
                } for i in ['Name', 'Profession', '# Raids']],
                editable=False,
                cell_selectable=False,
                style_as_list_view=True,
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
                    'border-bottom': '1px solid white'
                },
            ), color='grey')
        ), width={'size': 8, 'offset': 2})
    ]),
])


@app.callback(
    Output('character-table', 'data'),
    Input('api-msg', 'children'),
    Input('api-delete-msg', 'children')
)
def show_character_info(msg, del_msg):
    info = {}
    info['# Raids'] = []
    if session and session['CHARACTERS']:       
        info['Name'] = session['CHARACTERS']
        info['Profession'] = session['PROFESSION']
        for name in info['Name']:
            char_id = db.session.query(Character.id).filter_by(name = name).first()
            print(char_id)
            if(char_id):
                count = db.session.query(func.count(distinct(PlayerStat.raid_id))).filter_by(character_id = char_id[0]).scalar()
                print(count)
                info['# Raids'].append(count)
            else:
                info['# Raids'].append(0)
        print(f'info:{info}')
        df = pd.DataFrame(info).to_dict('records')
        return df


@app.callback(
    Output('api-table', 'data'),
    Input('api-msg', 'children')
)
def show_api_info(msg):
    info = {}
    if session and session['ACCOUNT']:
        info['Account'] = session['ACCOUNT']
        info['Key'] = session['API-KEY']
        info['Characters'] = len(session['CHARACTERS'])
        print(f'info:{info}')
        return [info]


@app.callback(
    Output('api-msg', 'children'),
    Output('account-dpn', 'label'),
    Input('api-btn', 'n_clicks'),
    State('api-input', 'value')
)
def save_api_key(n, key):
    if n:
        print(f'save: {n} - {key}')
        session['API-KEY'] = key
        session['PROFESSION'] = []
        headers = {'Authorization': f'Bearer {key}'}
        request = requests.get('https://api.guildwars2.com/v2/characters/', headers=headers)
        if request.status_code == 200:
            print(request.json())
            session['CHARACTERS'] = request.json()
        
        for name in session['CHARACTERS']:
            headers = {'Authorization': f'Bearer {key}'}
            request = requests.get(f'https://api.guildwars2.com/v2/characters/{name}', headers=headers)
            if request.status_code == 200:
                print(request.json()['profession'])
                session['PROFESSION'].append(request.json()['profession'])

        request = requests.get('https://api.guildwars2.com/v2/account', headers=headers)
        if request.status_code == 200:
            print(request.json())
            session['ACCOUNT'] = request.json()['name']
        session.permanent = True
        session.modified = True
    print('saving............')
    return f'API key saved {n}', f'{session["ACCOUNT"]}' if "ACCOUNT" in session else 'Account',


@app.callback(
    Output('api-delete-msg', 'children'),
    Input('api-table', 'data'),
    State('api-table', 'data_previous')
)
def delete_api_key(data, prev):
    if prev and len(data) == 0:
        print('session cleared')
        session.clear()
        return 'Session Cleared'

