import base64
import io
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
from models import FightSummary, Raid, RaidType

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
            dbc.Row(id='input-row', class_name='input-row', children=[
                dbc.Col(dcc.Loading(html.Div(id='save-msg'))),
                dbc.Col(dbc.Input(id='raid-name-input',placeholder='Raid title (optionel)', value='')),
                dbc.Col(dcc.Dropdown(id='raid-type-dropdown',
                                    placeholder='Select raid type',
                                    options=dropdown_options,
                                    value=dropdown_options[1]['value'])),
                dbc.Col(dbc.Button("Save", id='save-button')),
            ]),
        ])
    ]),
    dbc.Row([
        dbc.Col(id='raids-update-output'),
        dbc.Col(dbc.Button("Delete Raid(s)", id='delete-raid-btn'), width={}, style={'text-align':'end'})
    ], justify='end'),
    dbc.Row([
        dcc.Loading(html.Div(
            dash_table.DataTable(
                id='raids-table',
                columns=[{
                    'name': i,
                    'id': i,
                } for i in raids_df.columns],
                data=raids_dict,
                editable=False,
                row_selectable='multi',
                cell_selectable=False,
                style_as_list_view=True,
                style_cell={
                    'border': '1px solid #444',
                    'padding': '0.5rem',
                    'textAlign': 'center',
                    'font-family': 'var(--bs-body-font-family)',
                    'line-height': 'var(--bs-body-line-height)'
                },
                style_data={
                    'backgroundColor': '#424242',
                },
                style_header={
                    'backgroundColor': '#212121',
                    'textAlign': 'center',
                    'fontWeight': 'bold',
                    'border-top': '0px',
                    'border-bottom': '1px solid white'
                },
            ),
        ))
    ]),
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
    Input('raids-update-output', 'children'),
    Input('save-msg', 'children'),
    Input("temp-raid", "data")
)
def update_raids_table(msg, save_msg, data):
    raids_dict = [s.to_dict() for s in db.session.query(FightSummary).join(Raid).order_by(Raid.raid_date.desc(), FightSummary.start_time.desc()).all()]
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


@app.callback(Output('raid-summary', 'children'),
            Input('temp-data', 'data'))
def show_fights_summary_table(content):
    if content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview').tail(1).iloc[:,1:]
        return ["File Summary",dbc.Table.from_dataframe(df_fights, striped=True, bordered=True, hover=True, class_name='tableFixHead table table-striped table-bordered table-hover')]


@app.callback(
    [Output("temp-raid", "data"),
    Output('confirm-raid-exists', 'displayed')], 
    [Input("save-button", "n_clicks")],
    [State('temp-data', 'data'),
    State('raid-name-input', 'value'),
    State('raid-type-dropdown', 'value'),
    ]
)
def on_save_click(n, content, name, t):
    db_msg = ''
    if n and content:
        decoded = base64.b64decode(content)
        df_fights = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview').tail(1).iloc[:,1:]
        raid = db_writer.check_if_raid_exists(df_fights['Date'].values[0], df_fights['Start Time'].values[0])
        if raid:
            return raid.id, True
        db_msg = db_writer.write_xls_to_db(decoded, name, t)
        return db_msg, False
    return content, False


@app.callback(Output('save-msg', 'children'),
              Input('confirm-raid-exists', 'submit_n_clicks'),
              State('temp-raid', 'data'),
              State('temp-data', 'data'),
              State('raid-name-input', 'value'),
              State('raid-type-dropdown', 'value'),)
def update_output(submit_n_clicks, raid, xls, name, t):
    if submit_n_clicks:
        db_writer.delete_raid(raid)
        decoded = base64.b64decode(xls)
        db_writer.write_xls_to_db(decoded, name, t)
        return f'Overwriting raid {raid}'
