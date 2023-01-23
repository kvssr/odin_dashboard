from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from app import app, db
from models import Role, User


def layout():
    users_dict = [u.to_dict() for u in db.session.query(User).all()]
    users_df = pd.DataFrame(users_dict)


    table_header = [html.Thead(html.Tr([html.Th(col) for col in users_df.columns]+[html.Th('Edit')]))]
    rows = [html.Tr([
        html.Td(row['id']),
        html.Td(row['name']),
        html.Td(row['email']),
        html.Td(row['role']),
        html.Td('✔️' if row['active'] else '❌'),
        html.Td(row['last_checked']),
        html.Td(html.A('Edit', href=f'/admin/users/{row["id"]}')),
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
