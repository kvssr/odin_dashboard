from datetime import date
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from flask_login import login_user, current_user
from flask import session
from werkzeug.security import check_password_hash

from app import app, db
from models import User


def login(redirect):
    login = dbc.Row([
        dcc.Location(id='url_login', refresh=True),
        dbc.Col([
            html.H2('Login Form', style={'text-align': 'center'}),
            dbc.Card([
                dbc.CardImg(src="/assets/logo.png", top=True, style={'width': 200, 'margin': 'auto'}),
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
                    dbc.Button('Login', id='login-button', class_name='btn btn-color px-5 w-100', n_clicks=0),
                    dcc.Store(id='redirect-store', data=redirect)
                ])
            ]),
            html.Div(children='', id='output-state')
        ],
        md={'size': 4, 'offset': 4},
        xs={'size': 8, 'offset': 2})
    ])
    return login

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

# Logout
logout = html.Div([html.Div(html.H2('You have been logged out - Please login')),
                   html.Br(),
                   dcc.Link('Home', href='/')
                   ])


logged_in_menu = dbc.Nav(className='menu', children=[
    dbc.DropdownMenu(
            [dbc.DropdownMenuItem("API Key", href='/api'), 
            dbc.DropdownMenuItem("Profile", href='/details/')],
            label="Account",
            caret=True,
            nav=True,
            id='account-dpn',
        ),
    dbc.NavItem(dbc.NavLink("Home", href='/')),
    dbc.NavItem(dbc.NavLink("Details", href='/details')),
    dbc.NavItem(dbc.NavLink("Groups", href='/groups')),
     dbc.DropdownMenu(
         [
             dbc.DropdownMenuItem("Howto", href='/howto'),
             dbc.DropdownMenuItem("Contact", href='/contact'),
          ],
         label="Help",
         caret=True,
         nav=True,
         id='help',
     ),
    dbc.DropdownMenu([
        dbc.DropdownMenuItem("Overview", href='/upload'), 
        dbc.DropdownMenuItem("Visit log", href='/logs'),
        dbc.DropdownMenuItem("Users", href='/admin/users'),
        ],
        label="Admin",
        caret=True,
        nav=True,
        id='upload-dpn',
    ),
    dbc.NavItem(dbc.NavLink("Logout", href='/logout')),
],
)

login_menu = dbc.Nav(className='menu', children=[
    dbc.DropdownMenu([
        dbc.DropdownMenuItem("API Key", href='/api'), 
        dbc.DropdownMenuItem("Profile", href='/details/')
        ],
        label="Account",
        caret=True,
        nav=True,
        id='account-dpn',
    ),
    dbc.NavItem(dbc.NavLink("Home", href='/')),
    dbc.NavItem(dbc.NavLink("Details", href='/details')),
    dbc.NavItem(dbc.NavLink("Groups", href='/groups')),
    dbc.DropdownMenu([
        dbc.DropdownMenuItem("Howto", href='/howto'),
        dbc.DropdownMenuItem("Contact", href='/contact'),
        ],
        label="Help",
        caret=True,
        nav=True,
        id='help',
    ),
    dbc.NavItem(dbc.NavLink("Admin", id='admin-link', href='/login')),
])


@app.callback(Output('url_login', 'pathname'),
              Output('output-state', 'children'),
              [Input('login-button', 'n_clicks')],
              [State('uname-box', 'value'), State('pwd-box', 'value'), State('redirect-store', 'data')],
              prevent_initial_call=True)
def login_button_click(n_clicks, username, password, redirect):
    if redirect == '':
        redirect = '/'
    if n_clicks > 0:
        user = db.session.query(User).filter_by(username = username).first()
        if user is not None and user.active:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect, ''
            else:
                return '/login', 'Incorrect username or password'
        else:
            return '/login', 'Incorrect username or password'
    return '/login', ''


@app.callback(
    Output('user-status-div', 'children'), 
    Output('login-status', 'data'), 
    Input('login-row', 'loading_state'),
    State('url', 'pathname'),
    )
def login_status(state, url):
    ''' callback to display login/logout link in the header '''
    print(f'STATE: {state}')

    if hasattr(current_user, 'last_checked') and current_user.last_checked != date.today():
        check_user = db.session.query(User).filter(User.id == current_user.id).first()
        if check_user and check_user.active:
            current_user.last_checked = date.today()
            db.session.add(current_user)
            db.session.commit()
        else:
            return login_menu, 'loggedout'
        
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated \
            and url != '/logout':  # If the URL is /logout, then the user is about to be logged out anyways
        return logged_in_menu, current_user.get_id()
    else:
        return login_menu, 'loggedout'


@app.callback(
    Output('admin-link', 'href'),
    Input('url', 'pathname')
)
def admin_link_redirect_update(pathname):
    return f'/login{pathname}'
