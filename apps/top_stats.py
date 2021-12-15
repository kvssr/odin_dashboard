import base64
import io
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
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), sheet_name='dmg')
            df_dmg = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='rips')
            df_rips = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='stab')
            df_stab = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='cleanses')
            df_cleanses = df.head(5)

            fig_dmg = graphs.get_top_bar_chart(df_dmg, 'dmg')
            fig_rips = graphs.get_top_bar_chart(df_rips, 'rips')
            fig_stab = graphs.get_top_bar_chart(df_stab, 'stab')
            fig_cleanses = graphs.get_top_bar_chart(df_cleanses, 'cleanses')

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-dmg-chart',
                    figure=fig_dmg
                ), md=6, className='bar-chart'),
            dbc.Col(
                dcc.Graph(
                    id='top-rips-chart',
                    figure=fig_rips
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
        ])
    ])


@app.server.route('/')
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    print("Getting content..")
    if list_of_contents is not None:
        data = parse_contents(list_of_contents, list_of_names, list_of_dates)
        return data
