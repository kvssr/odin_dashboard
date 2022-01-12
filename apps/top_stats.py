import base64
import io
import json
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
from models import CleanseStat, DistStat, DmgStat, Fight, FightSummary, HealStat, RipStat, StabStat


def get_fig_with_model(model, t, title, limit):
    try:
        dmg_list = db.session.query(model).limit(limit).all()

        if dmg_list:
            df = pd.DataFrame([s.to_dict() for s in dmg_list])
            fig = graphs.get_top_bar_chart(df, t, title)
            return fig
    except Exception as e:
        print(e)        
    

def get_fig_dist():
    try:
        dist_list = db.session.query(DistStat).limit(5).all()

        if dist_list:
            df = pd.DataFrame([s.to_dict() for s in dist_list])
            fig = graphs.get_top_dist_bar_chart(df)
            return fig
    except Exception as e:
        print(e)

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

layout = html.Div(children=[
    html.Div(id='output-data-upload'),
    html.Div(children=[
        html.Div([
        html.Div(get_summary_table()),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-dmg-chart',
                    figure=get_fig_with_model(DmgStat, 'dmg', 'Top Damage', 5)
                ), md=12, lg=6, className='bar-chart'),     
            dbc.Col(
                dcc.Graph(
                    id='top-dist-chart',
                    figure=get_fig_dist()
                ), md=12,lg=6, className='bar-chart')
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-stab-chart',
                    figure=get_fig_with_model(StabStat, 'stab', 'Top Stability Output', 3)
                ), md=12, lg=6, className='bar-chart'),     
            dbc.Col(
                dcc.Graph(
                    id='top-cleanses-chart',
                    figure=get_fig_with_model(CleanseStat, 'cleanses', 'Top Condition Cleanse', 3)
                ), md=12, lg=6, className='bar-chart')
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-heal-chart',
                    figure=get_fig_with_model(HealStat, 'heal', 'Top Healing Output', 3)
                ), md=12, lg=6, className='bar-chart'),     
            dbc.Col(
                dcc.Graph(
                    id='top-rips-chart',
                    figure=get_fig_with_model(RipStat, 'rips', 'Top Boon Removal', 3)
                ), md=12, lg=6, className='bar-chart')
        ]),
        ])
    ])
])