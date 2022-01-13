import base64
import datetime
import io
import json
from threading import Barrier

from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from sqlalchemy.log import echo_property
from app import app, db
import pandas as pd
from helpers import db_writer, graphs
from sqlalchemy.orm.session import close_all_sessions

from models import AegisStat, BarrierStat, CleanseStat, DeathStat, DistStat, DmgStat, DmgTakenStat, Fight, FightSummary, FuryStat, HealStat, MightStat, PlayerStat, ProtStat, RipStat, StabStat


def get_summary_table():
    df = []
    try:
        query = db.session.query(FightSummary).first()
        db.session.commit()
        df = pd.DataFrame(query.to_dict(), index=[0])
    except Exception as e:
        db.session.rollback()
        print(e)
    
    return graphs.get_summary_table(df)


tab_style={'padding': '.5rem 0'}

layout = html.Div(children=[
    html.Div(id='details-output-data-upload', children=[
        dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                # Allow multiple files to be uploaded
                multiple=False
            ),
        html.Div(id='upload-msg'),
        html.Div(get_summary_table()),
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
                #dbc.Tab(label='Global', tab_id='global-tab', label_style=tab_style),
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




def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    db_msg = ''
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file           
            db_msg = db_writer.write_xls_to_db(decoded)

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return db_msg


@app.callback(Output('upload-msg', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_data(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        data = parse_contents(list_of_contents, list_of_names, list_of_dates)
        return data
    return None


@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'active_tab')],
              State('intermediate-value', 'data'))
def switch_tabs(tab, datasets):
    if tab == 'dmg-tab':
        try:
            query = db.session.query(DmgStat).all()
            db.session.commit()
            df = pd.DataFrame([s.to_dict() for s in query])
        except Exception as e:
            db.session.rollback()
            print(e)
        fig = graphs.get_top_bar_chart(df, 'dmg', "Top Damage", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
                id='top-dmg-chart',
                figure=fig,
            )
    elif tab == 'rips-tab':
        query = db.session.query(RipStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'rips', "Top Boons Removal", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-rip-chart',
            figure=fig
        )
    elif tab == 'might-tab':
        query = db.session.query(MightStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'might', "Top Might Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-might-chart',
            figure=fig
        )
    elif tab == 'fury-tab':
        query = db.session.query(FuryStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'fury', "Top Fury Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-fury-chart',
            figure=fig
        )
    elif tab == 'cleanses-tab':
        query = db.session.query(CleanseStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'cleanses', "Top Conditions Cleansed", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-cleanses-chart',
            figure=fig
        )
    elif tab == 'stab-tab':
        query = db.session.query(StabStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'stab', "Top Stability Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-stab-chart',
            figure=fig
        )
    elif tab == 'heal-tab':
        query = db.session.query(HealStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'heal', "Top Healing Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-heal-chart',
            figure=fig
        )
    elif tab == 'barrier-tab':
        query = db.session.query(BarrierStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'barrier', "Top Barrier Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-barrier-chart',
            figure=fig
        )
    elif tab == 'dist-tab':
        query = db.session.query(DistStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_dist_bar_chart(df, True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-dist-chart',
            figure=fig
        )
    elif tab == 'prot-tab':
        query = db.session.query(ProtStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'prot', "Top Protection Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-prot-chart',
            figure=fig
        )
    elif tab == 'aegis-tab':
        query = db.session.query(AegisStat).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'aegis', "Top Aegis Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-aegis-chart',
            figure=fig
        )
    elif tab == 'dmg_taken-tab':
        query = db.session.query(DmgTakenStat).order_by(DmgTakenStat.avg_dmg_taken_s.asc()).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_dmg_taken_chart(df, 'dmg_taken', "Least Damage Taken", False)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-dmg_taken-chart',
            figure=fig
        )
    elif tab == 'deaths-tab':
        query = db.session.query(DeathStat).join(PlayerStat).order_by(DeathStat.times_top.desc(), PlayerStat.attendance_count.desc(), DeathStat.total_deaths.asc()).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_survivor_chart(df, 'deaths', "Top Survivor", False)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id='top-deaths-chart',
            figure=fig
        )
    elif tab == 'global-tab':
        #df = pd.read_json(datasets['summary'], orient='split').iloc[-1]
        query = db.session.query(FightSummary).first()
        df = pd.DataFrame(query.to_dict(), index=[0]).iloc[0]
        kd_data = {"values": [df['Kills'],df['Deaths']], "names": ['Kills','Deaths']}
        kd_fig = graphs.get_pie_chart(kd_data,'Kills/Deaths Ratio',['#0AABD1','#D02500'])

        damage_data = {"values": [int(df['Damage'].replace(',', '')),10000000], "names": ['Damage Output','Damage Input']}
        damage_fig = graphs.get_pie_chart(damage_data,'Damage Ratio',['#FFD814','#D13617'])

        pack_data = {"values": [df['⌀ Allies'],df['⌀ Enemies']], "names": ['Wolves','Lambs']}
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
        query = db.session.query(Fight).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
        return table
