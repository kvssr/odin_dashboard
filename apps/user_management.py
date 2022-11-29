from dash import dash_table
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from app import app, db
from models import Role, User


def layout():
    users_dict = [u.to_dict() for u in db.session.query(User).all()]
    roles = [r.to_dict() for r in db.session.query(Role).all()]
    print(roles)
    users_df = pd.DataFrame(users_dict)
    print(users_df)
    roles_df = pd.DataFrame(roles)
    print(roles_df)

    table_header = [html.Thead(html.Tr([html.Th(col) for col in users_df.columns]+[html.Th('Edit', colSpan=2)]))]
    rows = [html.Tr([
        # html.Td(html.A(x, href=f'/admin/users/{row["id"]}')) for x in row.values()
        html.Td(row['id']),
        html.Td(row['name']),
        html.Td(row['email']),
        html.Td(row['role']),
        html.Td(row['active']),
        # html.Td(dbc.Select(
        #     id='user-role-slct',
        #     options=[{'label': 'guest', 'value': '1'},{'label': 'admin', 'value': '2'}],
        #     value='2'
        # )),
        # html(),
        # html.Td(dbc.Switch(
        #     id='user-active-check',
        #     value=row['active'],
        # )),
        html.Td(row['last_checked']),
        html.Td(html.A('Edit', href=f'/admin/users/{row["id"]}')),
        html.Td(html.A('Delete', href=f'/admin/users/{row["id"]}')),
    ]) for row in users_dict]

    user_table = dbc.Table(
        table_header + [html.Tbody(rows)],
        responsive=False,
        bordered=False,
        dark=True,
        hover=True,
        striped=True,
    )

    layout =  dbc.Container(id='user-manager-container', children=[
        dbc.Row(
            dbc.Col(children=[
                html.H1('User Management', className='text-center'),
            ])),
        dbc.Row([
            dbc.Col([
                user_table,
                dbc.Button(children='New User', id='add-row-button', n_clicks=0, href='/admin/users/add'),
            ])
        ])
    ])
    
    return layout


# @app.callback(
#     Output('users-table', 'data'),
#     Input('add-row-button', 'n_clicks'),
#     State('users-table', 'data'),
#     State('users-table', 'columns'))
# def add_row(n_clicks, rows, columns):
#     if n_clicks > 0:
#         rows.append({c['id']: '' for c in columns})
#     return rows