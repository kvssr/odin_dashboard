from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
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
        dcc.Store(id='user-id-store', data=user_id),
        dcc.ConfirmDialog(
            id='confirm-user-delete',
            message='Are you sure you want to delete this user?',
        ),
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
        dbc.Col([
            dbc.Input(
                type="password", 
                id="password-row", 
                disabled=True if user else False,
            ),
            dbc.Button('Show', id='show-pw-btn', className='float-end'),
            ],
            width=10, className='d-flex'
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

    active_input = dbc.Row([
        dbc.Label("Active", html_for="active-row", width=2),
        dbc.Col(
            dbc.Select(
                id="active-row",
                options=[{'label':'✔️', 'value': True}, {'label':'❌', 'value': False}],
                value=user.active if user else True
            ),
            width=10,
            ),
        ],
        className="mb-3",
    )

    buttons = dbc.Row(dbc.Col([
            dbc.Button(id='delete-user-btn', children='Delete', className='float-start bg-danger me-3', disabled=False if user else True),
            html.Div(id='delete-msg-box', className='float-start'),
            html.Div(id='save-msg-box', className='float-start'),
            dbc.Button(id='save-user-btn', children='Save', className='float-end ms-3'),
            dbc.Button(id='change-pw-btn', children='Change Password', className='float-end', disabled=False if user else True),
    ]))

    return dbc.Form([username_input, password_input, email_input, role_input, active_input, buttons])


@app.callback(
    Output('save-msg-box', 'children'), 
    Input('save-user-btn', 'n_clicks'),
    State('user-id-store', 'data'),
    State('username-row', 'value'),
    State('password-row', 'value'),
    State('password-row', 'disabled'),
    State('email-row', 'value'),
    State('role-row', 'value'),
    State('active-row', 'value'),
    prevent_initial_call=True
)
def on_submit_click(n, user_id, name, pw, pw_disabled, email, role, active_i):
    active = True if str(active_i).lower() == 'true' else False

    if user_id != None:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not pw_disabled:
            user.password = generate_password_hash(pw)
    else:
        user = User('')
        user.password = generate_password_hash(pw)

    user.username = name
    user.email = email
    user.role_id = role
    user.active = active

    db.session.add(user)
    db.session.commit()

    return f'Saved user {name} - {user.id}'


@app.callback(
    Output('password-row', 'type'), 
    Output('show-pw-btn', 'children'), 
    Input('show-pw-btn', 'n_clicks'),
    State('password-row', 'type'),
    prevent_initial_call=True
)
def show_password(n, state):
    if state == 'password':
        return 'text', 'Hide'
    else:
        return 'password', 'Show'


@app.callback(
    Output('password-row', 'disabled'), 
    Output('change-pw-btn', 'disabled'), 
    Input('change-pw-btn', 'n_clicks'),
    prevent_initial_call=True
)
def enable_password_input(n):
    return False, True


@app.callback(
    Output('confirm-user-delete', 'displayed'), 
    Input("delete-user-btn", "n_clicks"),
    prevent_initial_call=True
)
def on_delete_click(n):
    if n:
        return True


@app.callback(
    Output('delete-msg-box', 'children'),
    Input('confirm-user-delete', 'submit_n_clicks'),
    State('user-id-store', 'data'),
    prevent_initial_call=True
)
def confirm_delete_row(submit_n_clicks, data):
    print(data)
    user = db.session.query(User).filter_by(id=data).first()
    db.session.delete(user)
    db.session.commit()
    return f'User {data} deleted successfully'