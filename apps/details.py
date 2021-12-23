import base64
import datetime
import io
import json

from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app
import pandas as pd
from helpers import graphs

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

layout = html.Div(children=[
    html.Div(id='details-output-data-upload', children=[
        html.Div(id='summary'),
        html.Div([
            dbc.Tabs([
                dbc.Tab(label='Damage', tab_id='dmg-tab'),
                dbc.Tab(label='Rips', tab_id='rips-tab'),
                dbc.Tab(label='Cleanses', tab_id='cleanses-tab'),
                dbc.Tab(label='Stability', tab_id='stab-tab'),
                dbc.Tab(label='Healing', tab_id='heal-tab'),
                dbc.Tab(label='Distance', tab_id='dist-tab'),
                dbc.Tab(label='Summary', tab_id='summary-tab'),
            ],
                id='tabs',
                #active_tab='dmg-tab'
                ),
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

            df_dist = pd.read_excel(io.BytesIO(decoded), sheet_name='dist')

            summary = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview')
            summary = summary.iloc[:,1:]

            dataset = {
                'df_dmg': df_dmg.to_json(orient='split'),
                'df_rips': df_rips.to_json(orient='split'),
                'df_stab': df_stab.to_json(orient='split'),
                'df_cleanses': df_cleanses.to_json(orient='split'),
                'df_heals': df_heals.to_json(orient='split'),
                'df_dist': df_dist.to_json(orient='split'),
                'summary': summary.to_json(orient='split')
            }

            # for index, row in df.iterrows():
            # df.at[index, 'Name'] = "{:<25}".format(row['Name']) + get_short_profession(row['Profession']) + " "

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return dataset


@app.callback(Output('intermediate-value', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_data(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        data = parse_contents(list_of_contents, list_of_names, list_of_dates)
        return data
    return None


@app.callback(Output('summary', 'children'),
              Input('intermediate-value', 'data'))
def update_summary(datasets):
    if datasets is not None:
        print('...summary...')
        df = pd.read_json(datasets['summary'], orient='split')

        df_s = df[['Kills', 'Deaths', 'Duration in s', 'Num. Allies', 'Num. Enemies', 'Damage', 'Boonrips', 'Cleanses', 'Stability Output', 'Healing']].tail(1)
        df_s = df_s.rename(columns={'Num. Allies': 'Avg Num. Allies', 'Num. Enemies': 'Avg Num. Enemies'})
        df_s.insert(0, "Date", df['Date'].iloc[0].strftime("%Y-%d-%m"), True)

        # Adds thousand seperator for summary
        for x, value in enumerate(df_s.iloc[0,6:11]):
            df_s.iloc[0,6+x] = f'{int(value):,}'  

        table = dbc.Table.from_dataframe(df_s, striped=True, bordered=True, hover=True, size='sm')
        return [table, html.Hr()]
    return None


@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'active_tab')],
              State('intermediate-value', 'data'))
def switch_tabs(tab, datasets):
    if datasets is not None:
        if tab == 'dmg-tab':
            df = pd.read_json(datasets['df_dmg'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'dmg', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                    id='top-dmg-chart',
                    figure=fig,
                )
        elif tab == 'rips-tab':
            df = pd.read_json(datasets['df_rips'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'rips', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-rip-chart',
                figure=fig
            )
        elif tab == 'cleanses-tab':
            df = pd.read_json(datasets['df_cleanses'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'cleanses', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-cleanses-chart',
                figure=fig
            )
        elif tab == 'stab-tab':
            df = pd.read_json(datasets['df_stab'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'stab', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-stab-chart',
                figure=fig
            )
        elif tab == 'heal-tab':
            df = pd.read_json(datasets['df_heals'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'heal', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-heal-chart',
                figure=fig
            )
        elif tab == 'dist-tab':
            df = pd.read_json(datasets['df_dist'], orient='split')
            fig = graphs.get_top_dist_bar_chart(df, True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-dist-chart',
                figure=fig
            )
        elif tab == 'summary-tab':
            df = pd.read_json(datasets['summary'], orient='split')
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
            return table
    return ""
