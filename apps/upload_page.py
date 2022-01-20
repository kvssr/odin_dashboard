from ast import Call
import base64
from gc import callbacks
import io
from turtle import width
import dash
from pydoc import classname
from dash import dash_table
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
raids_dict = [s.to_dict() for s in db.session.query(FightSummary).all()]
raids_df = pd.DataFrame(raids_dict)


layout = [
    dcc.Store(id='temp-data'),
    dcc.Store(id='temp-raid'),
    dcc.ConfirmDialog(
        id='confirm-raid-exists',
        message='This raid already exists. Want to overwrite?',
    ),
    dcc.ConfirmDialog(
        id='confirm-raid-delete',
        message='Are you sure you want to delete this raid?',
    ),
    dbc.Row([dcc.Loading(dbc.Col(id='raid-summary'))]),
    dbc.Row([
        dbc.Col(dcc.Upload(id='upload-file', children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ])),md=12)               
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Row(id='upload-input-row', children=[
                dbc.Col(dcc.Loading(html.Div(id='save-msg'))),
                dbc.Col(dbc.Input(placeholder='Raid title (optionel)')),
                dbc.Col(dcc.Dropdown(id='raid-type-dropdown',
                                    placeholder='Select raid type',
                                    options=dropdown_options)),
                dbc.Col(dbc.Button("Save", id='save-button')),
            ]),
        ])
    ]),
    dbc.Row([
        dbc.Col(id='dmg-table'),
        dbc.Col(id='rips-table'),
        dbc.Col(id='cleanse-table'),
        dbc.Col(id='heal-table'),
    ]),
    dbc.Row([
        html.Div(
             dash_table.DataTable(
                id='raids-table',
                columns=[{
                    'name': i,
                    'id': i,
                } for i in raids_df.columns],
                data=raids_dict,
                editable=True,
                row_selectable='multi'
            ),
        )
    ]),
    dbc.Row([
        dbc.Col(id='raids-update-output'),
        dbc.Col(dbc.Button("Delete Raid(s)", id='delete-raid-btn'), width={'size': 2, 'offset':10})
    ])
]

@app.callback(Output('temp-data', 'data'),
            Input('upload-file', 'contents'))
def get_temp_data(content):
    if content:
        content_type, content_string = content.split(',')
        return content_string


@app.callback(
    Output('confirm-raid-delete', 'displayed'), 
    Input("delete-raid-btn", "n_clicks")
)
def on_delete_click(n):
    if n:
        return True

@app.callback(
    Output('raids-table', 'data'),
    Input('raids-update-output', 'children')
)
def update_raids_table(msg):
    raids_dict = [s.to_dict() for s in db.session.query(FightSummary).all()]
    return raids_dict


@app.callback(Output('raids-update-output', 'children'),
              Input('confirm-raid-delete', 'submit_n_clicks'),
              State('raids-table', 'selected_rows'),
              State('raids-table', 'data'))
def confirm_delete_row(submit_n_clicks, rows, data):
    if submit_n_clicks:
        row_list = []
        for row in rows:
            raid = db_writer.get_raid_by_summary(data[row]['Date'], data[row]['Kills'], data[row]['Deaths'])
            db_writer.delete_raid(raid.id)
            row_list.append(raid)
            data[row] = {}
        data = [s for s in data if s != {}]
        return [f'Just removed {row}:{row.raid_date}' for row in row_list]



""" 
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
        return dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True) """


@app.callback(Output('raid-summary', 'children'),
            Input('temp-data', 'data'))
def show_fights_summary_table(content):
    if content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview').tail(1).iloc[:,1:]
        return ["File Summary",dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True, class_name='tableFixHead')]


@app.callback(
    [Output("temp-raid", "data"),
    Output('confirm-raid-exists', 'displayed')], 
    [Input("save-button", "n_clicks")],
    [State('temp-data', 'data')]
)
def on_button_click(n, content):
    db_msg = ''
    if n and content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview').tail(1).iloc[:,1:]
        raid = db_writer.check_if_raid_exists(df_fights['Date'].values[0], df_fights['Start Time'].values[0])
        if raid:
            return raid.id, True
        db_msg = db_writer.write_xls_to_db(decoded)
        return db_msg, False
    return content, False


@app.callback(Output('save-msg', 'children'),
              Input('confirm-raid-exists', 'submit_n_clicks'),
              State('temp-raid', 'data'))
def update_output(submit_n_clicks, raid):
    if submit_n_clicks:

        return f'Overwriting raid {raid}'
