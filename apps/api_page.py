from email.quoprimime import quote
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
from dash.exceptions import PreventUpdate
import urllib

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
                    'type': 'text',
                    'presentation': 'markdown'
                } for i in ['Name', 'Profession', '# Raids']],
                editable=False,
                cell_selectable=False,
                style_as_list_view=True,
                markdown_options={
                    'link_target':'_self'
                },
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
    if session and 'CHARACTERS' in session:       
        info = {}
        info['# Raids'] = []
        info['Name'] = []
        info['Profession'] = session['PROFESSION']
        for name in session['CHARACTERS']:
            char_id = db.session.query(Character.id).filter_by(name = name).first()
            print(char_id)
            if(char_id):
                count = db.session.query(func.count(distinct(PlayerStat.raid_id))).filter_by(character_id = char_id[0]).scalar()
                print(count)
                info['# Raids'].append(count)
                info['Name'].append(f'[{name}](/details/{urllib.parse.quote(name)})')
            else:
                info['# Raids'].append(0)
                info['Name'].append(name)
        print(f'info:{info}')
        df = pd.DataFrame(info).to_dict('records')
        return df


@app.callback(
    Output('api-table', 'data'),
    Input('api-msg', 'children')
)
def show_api_info(msg):
    info = {}
    if session and 'ACCOUNT' in session:
        info['Account'] = session['ACCOUNT']
        info['Key'] = session['API-KEY']
        info['Characters'] = len(session['CHARACTERS'])
        print(f'info:{info}')
        return [info]


@app.callback(
    Output('account-dpn', 'label'),
    Input('url', 'pathname')
)
def show_account_name(url):
    if session and 'ACCOUNT' in session:
        return session['ACCOUNT']
    raise PreventUpdate


@app.callback(
    Output('api-msg', 'children'),
    Output('api-input', 'value'),
    Input('api-btn', 'n_clicks'),
    State('api-input', 'value')
)
def save_api_key(n, key):
    if n:
        print(f'save: {n} - {key}')
        professions = []
        characters = []
        try:
            headers = {'Authorization': f'Bearer {key}'}
            request = requests.get('https://api.guildwars2.com/v2/characters/', headers=headers)
            if request.status_code == 200:
                characters = request.json()
            else:
                raise Exception
            
            for name in characters:
                request = requests.get(f'https://api.guildwars2.com/v2/characters/{name}', headers=headers)
                if request.status_code == 200 or request.status_code == 206:
                    prof = request.json()['profession']
                    icon = requests.get(f'https://api.guildwars2.com/v2/professions/{prof}').json()['icon_big']
                    professions.append(f"![{prof}]({icon}){prof}")
                else:
                    raise Exception

            request = requests.get('https://api.guildwars2.com/v2/account', headers=headers)
            if request.status_code == 200:
                session['ACCOUNT'] = request.json()['name']
            else:
                raise Exception

            session['API-KEY'] = key
            session['CHARACTERS'] = characters
            session['PROFESSION'] = professions
            session.permanent = True
            session.modified = True
            print('Saving API Key')
            return f'API-Key Saved', ''
        except Exception as e:
            print(e)
            return f'Invalid API-KEY', 'Invalid Key'
    return f'Invalid API-KEY', None


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
