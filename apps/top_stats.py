import base64
import io
import json
import flask
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from helpers import graphs

import pandas as pd
from app import app


layout = html.Div(children=[
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'json' in filename:
            print("json file uploaded")
            raw_json = json.loads(decoded.decode('utf-8'))
            json_players = raw_json['players']
            print(raw_json['overall_squad_stats'])
            print(raw_json['players'][0]['total_stats']['dmg'])
            #df_players = pd.read_json(raw_json["players"])
            #print(df_players)
            return html.Div()
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), sheet_name='dmg')
            df_dmg = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='rips')
            df_rips = df.head(3)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='stab')
            df_stab = df.head(3)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='cleanses')
            df_cleanses = df.head(3)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='heal')
            df_heal = df.head(3)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='dist')
            df_dist = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview')
            df_summary = df[['Kills', 'Deaths', 'Duration in s', 'Num. Allies', 'Num. Enemies', 'Damage', 'Boonrips', 'Cleanses', 'Stability Output', 'Healing']].tail(1)
            df_summary = df_summary.rename(columns={'Num. Allies': '⌀ Allies', 'Num. Enemies': '⌀ Enemies'})
            df_summary.insert(0, "Date", df['Date'].iloc[0], True)
            print(df_summary.iloc[0,6:10])

            # Adds thousand seperator for summary
            for x, value in enumerate(df_summary.iloc[0,6:11]):
                df_summary.iloc[0,6+x] = f'{int(value):,}'          

            fig_dmg = graphs.get_top_bar_chart(df_dmg, 'dmg')
            fig_rips = graphs.get_top_bar_chart(df_rips, 'rips')
            fig_stab = graphs.get_top_bar_chart(df_stab, 'stab')
            fig_cleanses = graphs.get_top_bar_chart(df_cleanses, 'cleanses')
            fig_heal = graphs.get_top_bar_chart(df_heal, 'heal')
            fig_dist = graphs.get_top_dist_bar_chart(df_dist)

            graph_list = [fig_dmg,
                            fig_rips,
                            fig_stab,
                            fig_cleanses,
                            fig_heal,
                            fig_dist]



    except Exception as e:
        print("Exception: " + str(e))
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        dbc.Table.from_dataframe(df_summary, striped=True, bordered=True, hover=True, size='sm', id='summary'),
        html.Hr(),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-dmg-chart',
                    figure=fig_dmg
                ), md=6, className='bar-chart'),     
            dbc.Col(
                dcc.Graph(
                    id='top-dist-chart',
                    figure=fig_dist
                ), md=6, className='bar-chart')
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-stab-chart',
                    figure=fig_stab
                ), md=6, className='bar-chart'),
            dbc.Col(
                dcc.Graph(
                    id='top-cleanses-chart',
                    figure=fig_cleanses
                ), md=6, className='bar-chart')
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-heal-chart',
                    figure=fig_heal
                ), md=6, className='bar-chart'),
            dbc.Col(
                dcc.Graph(
                    id='top-rips-chart',
                    figure=fig_rips
                ), md=6, className='bar-chart')
        ])
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    print("Getting content..")
    if list_of_contents is not None:
        data = parse_contents(list_of_contents, list_of_names, list_of_dates)
        return data
