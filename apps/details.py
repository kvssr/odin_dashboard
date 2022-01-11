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

tab_style={'padding': '.5rem 0'}

layout = html.Div(children=[
    html.Div(id='details-output-data-upload', children=[
        html.Div(id='summary'),
        html.Div([
            dbc.Tabs([
                dbc.Tab(label='Damage', tab_id='dmg-tab', label_style=tab_style),
                dbc.Tab(label='Rips', tab_id='rips-tab', label_style=tab_style),
                dbc.Tab(label='Might', tab_id='might-tab', label_style=tab_style),
                dbc.Tab(label='Fury', tab_id='fury-tab', label_style=tab_style),
                dbc.Tab(label='Healing', tab_id='heal-tab', label_style=tab_style),
                dbc.Tab(label='Barrier', tab_id='barrier-tab', label_style=tab_style),
                dbc.Tab(label='Cleanses', tab_id='cleanses-tab', label_style=tab_style),
                dbc.Tab(label='Stability', tab_id='stab-tab', label_style=tab_style),
                dbc.Tab(label='Protection', tab_id='prot-tab', label_style=tab_style),
                dbc.Tab(label='Aegis', tab_id='aegis-tab', label_style=tab_style),
                dbc.Tab(label='Distance', tab_id='dist-tab', label_style=tab_style),
                dbc.Tab(label='Dmg taken', tab_id='dmg_taken-tab', label_style=tab_style),
                dbc.Tab(label='Deaths', tab_id='deaths-tab', label_style=tab_style),
                dbc.Tab(label='Global', tab_id='global-tab', label_style=tab_style),
                dbc.Tab(label='Summary', tab_id='summary-tab', label_style=tab_style),
            ],
                id='tabs',
                #active_tab='dmg-tab'
                class_name='nav-justified flex-nowrap'
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

            df_might = pd.read_excel(io.BytesIO(decoded), sheet_name='might')

            df_fury = pd.read_excel(io.BytesIO(decoded), sheet_name='fury')

            df_heals = pd.read_excel(io.BytesIO(decoded), sheet_name='heal')

            df_barrier = pd.read_excel(io.BytesIO(decoded), sheet_name='barrier')

            df_cleanses = pd.read_excel(io.BytesIO(decoded), sheet_name='cleanses')

            df_stab = pd.read_excel(io.BytesIO(decoded), sheet_name='stab')

            df_prot = pd.read_excel(io.BytesIO(decoded), sheet_name='prot')

            df_aegis = pd.read_excel(io.BytesIO(decoded), sheet_name='aegis')

            df_dist = pd.read_excel(io.BytesIO(decoded), sheet_name='dist')

            df_dmg_taken = pd.read_excel(io.BytesIO(decoded), sheet_name='dmg_taken')

            df_deaths = pd.read_excel(io.BytesIO(decoded), sheet_name='deaths')

            summary = pd.read_excel(io.BytesIO(decoded), sheet_name='fights overview')
            summary = summary.iloc[:,1:]

            dataset = {
                'df_dmg': df_dmg.to_json(orient='split'),
                'df_rips': df_rips.to_json(orient='split'),
                'df_might': df_might.to_json(orient='split'),
                'df_fury': df_fury.to_json(orient='split'),
                'df_heals': df_heals.to_json(orient='split'),
                'df_barrier': df_barrier.to_json(orient='split'),
                'df_cleanses': df_cleanses.to_json(orient='split'),
                'df_stab': df_stab.to_json(orient='split'),
                'df_prot': df_prot.to_json(orient='split'),
                'df_aegis': df_aegis.to_json(orient='split'),
                'df_dist': df_dist.to_json(orient='split'),
                'df_dmg_taken': df_dmg_taken.to_json(orient='split'),
                'df_deaths': df_deaths.to_json(orient='split'),
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
        df_s = df_s.rename(columns={'Num. Allies': '⌀ Allies', 'Num. Enemies': '⌀ Enemies'})
        df_s.insert(0, "Date", df['Date'].iloc[0].strftime("%Y-%m-%d"), True)

        # Adds thousand seperator for summary
        for x, value in enumerate(df_s.iloc[0,6:11]):
            df_s.iloc[0,6+x] = f'{int(value):,}'  

        table = dbc.Table.from_dataframe(df_s, striped=True, bordered=True, hover=True, size='sm', id='summary')
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
        elif tab == 'might-tab':
            df = pd.read_json(datasets['df_might'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'might', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-might-chart',
                figure=fig
            )
        elif tab == 'fury-tab':
            df = pd.read_json(datasets['df_fury'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'fury', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-fury-chart',
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
        elif tab == 'barrier-tab':
            df = pd.read_json(datasets['df_barrier'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'barrier', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-barrier-chart',
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
        elif tab == 'prot-tab':
            df = pd.read_json(datasets['df_prot'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'prot', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-prot-chart',
                figure=fig
            )
        elif tab == 'aegis-tab':
            df = pd.read_json(datasets['df_aegis'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'aegis', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-aegis-chart',
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
        elif tab == 'dmg_taken-tab':
            df = pd.read_json(datasets['df_dmg_taken'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'dmg_taken', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-dmg_taken-chart',
                figure=fig
            )
        elif tab == 'deaths-tab':
            df = pd.read_json(datasets['df_deaths'], orient='split')
            fig = graphs.get_top_bar_chart(df, 'deaths', True)
            fig.update_layout(
                height=1000,
            )
            return dcc.Graph(
                id='top-deaths-chart',
                figure=fig
            )
        elif tab == 'global-tab':
            df = pd.read_json(datasets['summary'], orient='split').iloc[-1]

            kd_data = {"values": [df['Kills'],df['Deaths']], "names": ['Kills','Deaths']}
            kd_fig = graphs.get_pie_chart(kd_data,'Kills/Deaths Ratio',['#0AABD1','#D02500'])

            damage_data = {"values": [df['Damage'],10000000], "names": ['Damage Output','Damage Input']}
            damage_fig = graphs.get_pie_chart(damage_data,'Damage Ratio',['#FFD814','#D13617'])

            pack_data = {"values": [df['Num. Allies'],df['Num. Enemies']], "names": ['Wolves','Lambs']}
            pack_fig = graphs.get_pie_chart(pack_data,'Wolves/Lambs Ratio',['#7D7A7A','#850000'])

            return html.Div([
                dbc.Row([
                    dbc.Col(
                        dcc.Graph(
                            id='kd-pie-chart',
                            figure=kd_fig
                        ), md=4, className='pie-chart'),     
                    dbc.Col(
                        dcc.Graph(
                            id='damage-pie-chart',
                            figure=damage_fig
                        ), md=4, className='pie-chart'),
                    dbc.Col(
                        dcc.Graph(
                            id='pack-pie-chart',
                            figure=pack_fig
                        ), md=4, className='pie-chart')
                ]),
            ])

        elif tab == 'summary-tab':
            df = pd.read_json(datasets['summary'], orient='split')
            df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
            return table
    return ""
