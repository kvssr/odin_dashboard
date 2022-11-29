import time
from datetime import date, datetime
from urllib.parse import unquote

import dash_bootstrap_components as dbc
import requests
from dash import dash, dcc, html
from dash.dependencies import Input, Output
from flask import session
from flask_login import current_user, logout_user

from app import app, db
from apps import (api_page, contact_page, details, groups_page, howto_page,
                  json_page, login, personal_details, top_stats, upload_page,
                  user_logs_page)
from models import Account, Log

server = app.server

# General layout of the website
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
    html.Div(id='page-content'),
    dbc.Row(id='footer')
])

# All the routes from the app
@app.callback(Output('page-content', 'children'),
              Output('redirect', 'pathname'),
              Input('url', 'pathname'))
def display_page(pathname):
    view = None
    url = dash.no_update
    
    # if pathname == '/login':
    #     view = login.login()
    if pathname.startswith('/login'):
        redirect = pathname.split('/')[-1]
        view = login.login(redirect)
    elif pathname == '/contact':
        view = contact_page.layout()
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
        # if (check_valid_guild() and ('CHARACTERS' in session and char in session['CHARACTERS'])) or current_user.is_authenticated:
        if check_valid_guild() or current_user.is_authenticated:
            view = personal_details.layout(unquote(name))
        # elif 'CHARACTERS' in session and check_valid_guild():
        #     view = personal_details.layout('')
        else:
            view = 'Redirecting to api...'
            url = '/api'
    elif pathname == '/details':
        if check_valid_guild() or current_user.is_authenticated:
            view = details.layout()
        else:
            view = 'Redirecting to api...'
            url = '/api'
    elif pathname == '/groups':
        if check_valid_guild() or current_user.is_authenticated:
            view = groups_page.layout()
        else:
            view = 'Redirecting to login...'
            url = '/login'
    elif pathname == '/upload':
        if current_user.is_authenticated:
            view = upload_page.layout()
        else:
            view = 'Redirecting to login...'
            url = f'/login{pathname}'
    elif pathname == '/logs':
        if current_user.is_authenticated:
            view = user_logs_page.layout()
        else:
            view = 'Redirecting to login...'
            url = f'/login{pathname}'
    elif pathname == '/howto':
        view = howto_page.layout
    elif pathname == '/':
        if check_valid_guild() or current_user.is_authenticated:
            view = top_stats.layout()
        else:
            view = 'Redirecting to api...'
            url = '/api'
    else:
        view = 'Redirecting to api...'
        url = '/api'
    # You could also return a 404 "URL not found" page here
    return view, url


# Checks if the user is in the guild. In this case Odin.
def check_valid_guild():
    guild = '48B067A2-21A7-4858-8007-4ECA99798EBF' # Odin
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
                if guild in guilds:
                    print('Odin is in guilds. Refreshing api..')
                    session['LAST-CHECKED'] = str(date.today())
                    session.permanent = True
                    name = request.json()['name']
                    account_id = db.session.query(Account.id).filter_by(name = name).first()
                    if account_id is None:
                        account = Account(name=name)
                        db.session.add(account)
                        db.session.commit()
                        account_id = account.id
                    else:
                        account_id = account_id[0]
                    logged_today = db.session.query(Log.id).filter_by(account_id=account_id).filter_by(log_date=date.today()).first()
                    if logged_today:
                        print('Already logged today')
                    else:
                        print('Not logged yet today')
                        log = Log(account_id=account_id, log_date=date.today())
                        print(f'account: {log.account_id} - date: {log.log_date}')
                        db.session.add(log)
                        db.session.commit()                    
                    return True

    today = date.today()
    print(f'Today: {today}')
    print('No account in Odin')
    return False


if __name__ == '__main__':
    app.run_server(debug=app.server.config['DEBUG'])
