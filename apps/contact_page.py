import dash_bootstrap_components as dbc
from dash import html
from numpy import size

def layout():
    layout = dbc.Container(id='contact-page-container', children=[
        dbc.Row(id='contect-title', class_name='input-row', children=[
            dbc.Col(class_name='text-center',children=[html.H1('Contact')])
        ]),
        dbc.Row(class_name='mb-3', children=[
            dbc.Col(children=[
                dbc.Row(class_name='table-header', children=[
                    dbc.Col('Name'),
                    dbc.Col('Ingame'),
                    dbc.Col('Discord'),
                ]),
                dbc.Row(class_name='table-row', children=[
                    dbc.Col('Congenial'),
                    dbc.Col('Congenial.2693'),
                    dbc.Col('Congenial#6593'),
                ]),
                dbc.Row(class_name='table-row', children=[
                    dbc.Col('Freya'),
                    dbc.Col('Freya.7140'),
                    dbc.Col('Freya#7797'),
                ]),
                dbc.Row(class_name='table-row', children=[
                    dbc.Col('Mustang Meringue'),
                    dbc.Col('Shunsui Jiraiya.9103'),
                    dbc.Col('Mustang.Meringue#4655'),
                ]),
                dbc.Row(class_name='table-row', children=[
                    dbc.Col('Tinman'),
                    dbc.Col('TinMan.2765'),
                    dbc.Col('TinMan#0455'),
                ]),
            ], width={'size':'6', 'offset': '3'})
        ]),
    ])

    return layout