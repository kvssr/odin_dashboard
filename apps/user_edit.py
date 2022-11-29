from dash import dash_table
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from app import app, db
from models import Role, User
from werkzeug.security import generate_password_hash


def layout(user_id=None):
    user = None
    if user_id:
        user = db.session.query(User).filter_by(id = user_id).first()

    form = get_form(user)

    layout =  dbc.Container(id='user-editor-container', children=[
        dbc.Row(
            dbc.Col(children=[
                html.H1('User editor', className='text-center'),
            ])
        ),
        dbc.Row(dbc.Col([
            form,
        ], width={'size': 6, 'offset': 3})
        ),
        dcc.Store(id='user-id-store', data=user_id)
    ])   

    return layout


def get_form(user):

    roles = [r.to_dict() for r in db.session.query(Role).order_by(Role.id.desc()).all()]
    dropdown_options = [{'label': r["name"], 'value': r["id"]} for r in roles]
    print(dropdown_options)

    username_input = dbc.Row([
        dbc.Label("Username", html_for="username-row", width=2),
        dbc.Col(
            dbc.Input(
                type="username", 
                id="username-row", 
                placeholder="Enter username",
                value = user.username if user else None
            ),
            width=10,
            ),
        ],
        className="mb-3",
    )

    password_input = dbc.Row([
        dbc.Label("Password", html_for="password-row", width=2),
        dbc.Col(
            dbc.Input(
                type="password", 
                id="password-row", 
                disabled=True if user else False, 
            ),
            width=10,
            ),
        ],
        className="mb-3",
    )

    email_input = dbc.Row([
        dbc.Label("Email", html_for="email-row", width=2),
        dbc.Col(
            dbc.Input(
                type="email", 
                id="email-row",
                value=user.email if user else None ,
            ),
            width=10,
            ),
        ],
        className="mb-3",
    )

    role_input = dbc.Row([
        dbc.Label("Role", html_for="role-row", width=2),
        dbc.Col(
            dbc.Select(
                id="role-row",
                options=dropdown_options,
                value=user.role_id if user else None
            ),
            width=10,
            ),
        ],
        className="mb-3",
    )

    buttons = dbc.Row(dbc.Col([
            html.Div(id='save-msg-box', className='float-start'),
            dbc.Button(id='save-user-btn', children='Save', className='float-end'),
            dbc.Button(id='change-pw-btn', children='Change Password', className='float-end', disabled=False if user else True),
    ]))

    return dbc.Form([username_input, password_input, email_input, role_input, buttons])


@app.callback(
    Output('save-msg-box', 'children'), 
    Input('save-user-btn', 'n_clicks'),
    State('user-id-store', 'data'),
    State('username-row', 'value'),
    State('password-row', 'value'),
    State('email-row', 'value'),
    State('role-row', 'value'),
    prevent_initial_call=True
)
def on_submit_click(n, user_id, name, pw, email, role):
    print(user_id)
    if user_id != None:
        user = db.session.query(User).filter_by(id=user_id).first()
    else:
        user = User('')
        user.password = generate_password_hash(pw)

    user.username = name
    user.email = email
    user.role_id = role

    db.session.add(user)
    db.session.commit()

    return f'Saved user {name} - {user.id}'