from datetime import date
import time
from dash import dcc, dash
from dash import html
from dash.dependencies import Input, Output
from flask import request, session
from flask_login import current_user, logout_user
import dash_bootstrap_components as dbc
from urllib.parse import unquote
import requests

from app import app
from apps import api_page, json_page, personal_details, top_stats, details, login, upload_page

server = app.server

app.layout = dbc.Container(id='container', children=[
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='redirect', refresh=True),
    dcc.Store(id='login-status', storage_type='session'),
    dbc.Row(id='login-row', children=dbc.Col(html.Div(id='user-status-div'))),
    dbc.Row(id='header', children=[
        dbc.Col(html.Img(id='logo', src='../assets/logo.png'), sm=1),
        dbc.Col(children=[
            html.H1('Records of Valhalla', 'title'),
            ], sm=10)]),
    html.Hr(id='hr-header'),
    dcc.Store(id='db-update-date'),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Output('redirect', 'pathname'),
              Input('url', 'pathname'))
def display_page(pathname):
    view = None
    url = dash.no_update
    if pathname == '/login':
        view = login.login
    elif pathname == '/api':
        view = api_page.layout
    elif pathname == '/json':
        view = json_page.layout
    elif pathname == '/success':
        if current_user.is_authenticated:
            view = login.success
            url = '/details'
        else:
            view = login.failed
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            time.sleep(1)
            url = '/'
        else:
            view = login
            url = '/login'
    elif pathname.startswith('/details/'):     
        name = pathname.split('/')[-1]
        char = unquote(name.split('(')[0]).rstrip()
        if current_user.is_authenticated or check_valid_guild() and ('CHARACTERS' in session and char in session['CHARACTERS']):
            view = personal_details.layout(unquote(name))
        elif 'CHARACTERS' in session and check_valid_guild():
            view = personal_details.layout('')
        else:
            view = 'Redirecting to api...'
            url = '/api'
    elif pathname == '/details':
        if  current_user.is_authenticated or (check_valid_guild() and 'CHARACTERS' in session):
            view = details.layout
        else:
            view = 'Redirecting to api...'
            url = '/api'
    elif pathname == '/upload':
        if current_user.is_authenticated:
            view = upload_page.layout
        else:
            view = 'Redirecting to login...'
            url = '/login'
    elif pathname == '/':
        if current_user.is_authenticated or check_valid_guild():
            view = top_stats.layout
        else:
            view = 'Redirecting to api...'
            url = '/api'
    else:
        view = top_stats.layout
    # You could also return a 404 "URL not found" page here
    return view, url



def check_valid_guild():
    odin = '48B067A2-21A7-4858-8007-4ECA99798EBF'
    if session:
        if 'LAST-CHECKED' in session:
            print(f'dat compare: {date.today()} - {session["LAST-CHECKED"]}')
            if str(date.today()) == session['LAST-CHECKED']:
                print('API still valid')
                return True
        if 'API-KEY' in session:
            key = session['API-KEY']
            headers = {'Authorization': f'Bearer {key}'}
            request = requests.get('https://api.guildwars2.com/v2/account', headers=headers)
            if request.status_code == 200 or request.status_code == 206:
                guilds = request.json()['guilds']
                if odin in guilds:
                    print('Odin is in guilds. Refreshing api..')
                    session['LAST-CHECKED'] = str(date.today())
                    session.permanent = True
                    return True

    today = date.today()
    print(f'Today: {today}')
    print('No account in Odin')
    return False



if __name__ == '__main__':
    app.run_server(debug=True)
