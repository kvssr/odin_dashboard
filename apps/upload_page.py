from ast import Call
import base64
from gc import callbacks
import io
import json
from pydoc import classname
import flask
import time
import datetime
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from sqlalchemy.sql.elements import Null
from helpers import db_writer, graphs

import pandas as pd
from app import app, db
from models import CleanseStat, DistStat, DmgStat, Fight, FightSummary, HealStat, RaidType, RipStat, StabStat

dropdown_options = [{'label':s.name, 'value':s.id} for s in db.session.query(RaidType).all()]

layout = [
    dcc.Store(id='temp-data'),
    dbc.Row([
        dbc.Col(dcc.Upload(id='upload-file', children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ])),md=6),
        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Input(placeholder='Raid title (optionel)'), md=6),
                dbc.Col(html.Div(id='save-msg'), md=6),
            ]),
            dbc.Row([dbc.Col(dcc.Dropdown(id='raid-type-dropdown',
                                    placeholder='Select raid type',
                                    options=dropdown_options)),
                    dbc.Col(dbc.Button("Save", id='save-button'), md=6)
                    ])
        ])
    ]),
    dbc.Row([
        dbc.Col(id='dmg-table'),
        dbc.Col(id='rips-table'),
        dbc.Col(id='cleanse-table'),
        dbc.Col(id='heal-table'),
    ]),
    dbc.Row([
        dbc.Col(id='fights-table')
    ])
]

@app.callback(Output('temp-data', 'data'),
            Input('upload-file', 'contents'))
def get_temp_data(content):
    if content:
        content_type, content_string = content.split(',')
        return content_string


@app.callback(Output('fights-table', 'children'),
            Input('temp-data', 'data'))
def show_fights_table(content):
    if content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview')
        return ["Fights overview",dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True, class_name='tableFixHead')]


@app.callback(Output('dmg-table', 'children'),
            Input('temp-data', 'data'))
def show_dmg_table(content):
    if content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='dmg').head(5)
        return dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True)


@app.callback(Output('rips-table', 'children'),
            Input('temp-data', 'data'))
def show_dmg_table(content):
    if content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='rips').head(5)
        return dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True)


@app.callback(Output('cleanse-table', 'children'),
            Input('temp-data', 'data'))
def show_dmg_table(content):
    if content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='cleanses').head(5)
        return dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True)


@app.callback(Output('heal-table', 'children'),
            Input('temp-data', 'data'))
def show_dmg_table(content):
    if content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='heal').head(5)
        return dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True)


@app.callback(
    Output("save-msg", "children"), 
    [Input("save-button", "n_clicks")],
    State('temp-data', 'data')
)
def on_button_click(n, content):
    if n and content:
        decoded = base64.b64decode(content)
        db_msg = db_writer.write_xls_to_db(decoded)
        return db_msg