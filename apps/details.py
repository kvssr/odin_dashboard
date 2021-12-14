import base64
import io
import json

from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app
import pandas as pd

profession_shorts = {
    'Guardian': 'Gnd',
    'Dragonhunter': 'Dgh',
    'Firebrand': 'Fbd',
    'Revenant': 'Rev',
    'Herald': 'Her',
    'Renegade': 'Ren',
    'Warrior': 'War',
    'Berserker': 'Brs',
    'Spellbreaker': 'Spb',
    'Engineer': 'Eng',
    'Scrapper': 'Scr',
    'Holosmith': 'Hls',
    'Ranger': 'Rgr',
    'Druid': 'Dru',
    'Soulbeast': 'Slb',
    'Thief': 'Thf',
    'Daredevil': 'Dar',
    'Deadeye': 'Ded',
    'Elementalist': 'Ele',
    'Tempest': 'Tmp',
    'Weaver': 'Wea',
    'Mesmer': 'Mes',
    'Chronomancer': 'Chr',
    'Mirage': 'Mir',
    'Necromancer': 'Nec',
    'Reaper': 'Rea',
    'Scourge': 'Scg',
}

layout = dbc.Container(id='container', children=[
    dbc.Row(id='header', children=[
        html.Img(id='logo', className='col-sm-1', src='../assets/logo.png'),
        dbc.Col(children=[
            html.H1('ODIN Carrot Awards', 'title'),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                # Allow multiple files to be uploaded
                multiple=False
            )])]),
    html.Hr(),
    html.Div(id='details-output-data-upload', children=[
        html.Div([
            dbc.Tabs([
                dbc.Tab(label='Damage', tab_id='dmg-tab'),
                dbc.Tab(label='Rips', tab_id='rips-tab'),
                dbc.Tab(label='Cleanses', tab_id='cleanses-tab'),
                dbc.Tab(label='Stability', tab_id='stab-tab'),
                dbc.Tab(label='Healing', tab_id='heal-tab'),
            ],
                id='tabs',
                active_tab='dmg-tab'),
            html.Div(id="tab-content"),
        ])
    ]),
    dcc.Store(id='intermediate-value')
])


def get_short_profession(profession):
    return "(" + profession_shorts[profession] + ")"


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file

            df_dmg = pd.read_excel(io.BytesIO(decoded), sheet_name='dmg')

            df_rips = pd.read_excel(io.BytesIO(decoded), sheet_name='rips')

            df_stab = pd.read_excel(io.BytesIO(decoded), sheet_name='stab')

            df_cleanses = pd.read_excel(io.BytesIO(decoded), sheet_name='cleanses')

            df_heals = pd.read_excel(io.BytesIO(decoded), sheet_name='heal')

            dataset = {
                'df_dmg': df_dmg.to_json(orient='split'),
                'df_rips': df_rips.to_json(orient='split'),
                'df_stab': df_stab.to_json(orient='split'),
                'df_cleanses': df_cleanses.to_json(orient='split'),
                'df_heals': df_heals.to_json(orient='split'),
            }

            # for index, row in df.iterrows():
            # df.at[index, 'Name'] = "{:<25}".format(row['Name']) + get_short_profession(row['Profession']) + " "

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return json.dumps(dataset)


@app.callback(Output('intermediate-value', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        data = parse_contents(list_of_contents, list_of_names, list_of_dates)
        return data
    return ""


@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'active_tab')],
              State('intermediate-value', 'data'))
def switch_tabs(tab, datasets):
    if datasets is not None:
        datasets = json.loads(datasets)
        if tab == 'dmg-tab':
            return html.Div(str(pd.read_json(datasets['df_dmg'], orient='split')))
        elif tab == 'rips-tab':
            return
        elif tab == 'cleanses-tab':
            return
        elif tab == 'stab-tab':
            return
        elif tab == 'heal-tab':
            return
