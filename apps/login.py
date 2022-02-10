from click import style
from dash import html, dcc, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask import request, session
import requests
from requests.auth import HTTPBasicAuth

# Login screen
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from models import User


login = dbc.Row([
    dcc.Location(id='url_login', refresh=True),
    dbc.Col([
        html.H2('Login Form', style={'text-align': 'center'}),
        dbc.Card([
            dbc.CardImg(src="assets/logo.png", top=True, style={'width': 200, 'margin': 'auto'}),
            dbc.CardBody([
                html.Div(
                    className='mb-3',
                    children=[
                        dbc.Input(type='text', id='uname-box', placeholder='Enter your username')
                    ]
                ),
                html.Div(
                    className='mb-3',
                    children=[
                        dbc.Input(type='password', id='pwd-box', placeholder='Enter your password')
                    ]
                ),
                dbc.Button('Login', id='login-button', class_name='btn btn-color px-5 w-100', n_clicks=0)
            ])
        ]),
        html.Div(children='', id='output-state')
    ],
    width={'size': 4, 'offset': 4})
])


# Successful login
success = html.Div([html.Div([html.H2('Login successful.'),
                              html.Br(),
                              dcc.Link('Home', href='/')])
                    ])

# Failed Login
failed = html.Div([html.Div([html.H2('Log in Failed. Please try again.'),
                             html.Br(),
                             html.Div([login]),
                             dcc.Link('Home', href='/')
                             ])
                   ])


# logout
logout = html.Div([html.Div(html.H2('You have been logged out - Please login')),
                   html.Br(),
                   dcc.Link('Home', href='/')
                   ])


api_input = html.Div(id='api-container', children=[
    dbc.Row(id='api-row', children=[
        dbc.Col(id='api-col', children=[
            dbc.Input(id='api-input'),
            dbc.Button("Save", id='api-btn'),
            html.Div(id='api-msg', style={'display': 'none'})
        ])
    ])
])


logged_in_menu = dbc.Nav(className='menu', children=[
    dbc.NavItem(dbc.NavLink("API Key", id='api-link')),
    dbc.NavItem(dbc.NavLink("Home", href='/')),
    dbc.NavItem(dbc.NavLink("Details", href='/details')),
    dbc.NavItem(dbc.NavLink("Upload", href='/upload')),
    dbc.NavItem(dbc.NavLink("Logout", href='/logout')),
],
), api_input

loggin_menu = dbc.Nav(className='menu', children=[
    dbc.NavItem(dbc.NavLink("API Key", id='api-link')),
    dbc.NavItem(dbc.NavLink("Home", href='/')),
    dbc.NavItem(dbc.NavLink("Details", href='/details')),
    dbc.NavItem(dbc.NavLink("Admin", href='/login')),
]), api_input


@app.callback(Output('url_login', 'pathname'),
              Output('output-state', 'children'),
              [Input('login-button', 'n_clicks')],
              [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks, username, password):
    if n_clicks > 0:
        user = db.session.query(User).filter_by(username = username).first()
        if user is not None:
            if check_password_hash(user.password, password):
                login_user(user)
                return '/success', ''
            else:
                return '/login', 'Incorrect username or password'
        else:
            return '/login', 'Incorrect username or password'
    return '/login', ''


@app.callback(Output('user-status-div', 'children'), Output('login-status', 'data'), [Input('url', 'pathname')])
def login_status(url):
    ''' callback to display login/logout link in the header '''
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated \
            and url != '/logout':  # If the URL is /logout, then the user is about to be logged out anyways
        return logged_in_menu ,current_user.get_id()
    else:
        return loggin_menu, 'loggedout'


@app.callback(
    Output('api-container', 'style'),
    Output('api-input', 'value'),
    Input('api-link', 'n_clicks'),
    State('api-container', 'style')
)
def toggle_api_input(n, s):
    if n:
        key = session['API-KEY'] if 'API-KEY' in session else ''
        print(f'key: {key}')
        if s['display'] == 'none':
            return {'display': 'inherit'}, key
        else:
            return {'display': 'none'}, key
    return {'display': 'none'}, ''


@app.callback(
    Output('api-msg', 'children'),
    Output('api-link', 'children'),
    Input('api-btn', 'n_clicks'),
    State('api-input', 'value')
)
def save_api_key(n, key):
    if n:
        print(f'save: {n} - {key}')
        session['API-KEY'] = key

        headers = {'Authorization': f'Bearer {key}'}
        request = requests.get('https://api.guildwars2.com/v2/characters/', headers=headers)
        if request.status_code == 200:
            print(request.json())
            session['CHARACTERS'] = request.json()

        request = requests.get('https://api.guildwars2.com/v2/account', headers=headers)
        if request.status_code == 200:
            print(request.json())
            session['ACCOUNT'] = request.json()['name']
        session.permanent = True
        session.modified = True
    print('saving............')
    return 'API key saved', f'API Key({session["ACCOUNT"]})' if "ACCOUNT" in session else 'API Key'