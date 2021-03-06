from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from sqlalchemy.sql.elements import Null
from helpers import db_writer, graphs
from flask_login import login_user, current_user

import pandas as pd
from app import app, db
from models import CleanseStat, DistStat, DmgStat, Fight, FightSummary, HealStat, PlayerStat, Raid, RipStat, StabStat


config = {
    'displayModeBar': False,
    'displaylogo': False,
    'scrollZoom': False,
    'staticPlot': True
}


def get_fig_with_model(model, t, title, limit, raid):
    try:
        dmg_list = db.session.query(model).order_by(-getattr(model, f'total_{t}')).join(PlayerStat).join(Raid).filter_by(id = raid).limit(limit).all()

        if dmg_list:
            df = pd.DataFrame([s.to_dict() for s in dmg_list])
            fig = graphs.get_top_bar_chart(df, t, title)
            return fig
    except Exception as e:
        print(e)        
    

def get_fig_dist(raid):
    try:
        dist_list = db.session.query(DistStat).order_by(-DistStat.percentage_top).join(PlayerStat).join(Raid).filter_by(id=raid).limit(5).all()

        if dist_list:
            df = pd.DataFrame([s.to_dict() for s in dist_list])
            fig = graphs.get_top_dist_bar_chart(df)
            return fig
    except Exception as e:
        print(e)

def get_summary_table(raid):
    df = []
    try:
        query = db.session.query(FightSummary).join(Raid).filter_by(id=raid).first()
        db.session.commit()
        df = pd.DataFrame(query.to_dict(), index=[0])
    except Exception as e:
        db.session.rollback()
        print(e)
    
    return graphs.get_summary_table(df)


layout = html.Div(children=[
    dbc.Row(id='input-row-top',class_name='input-row', children=[
            dbc.Col([
                html.Div("Select Raid", style={'text-align': 'center'}),
                dcc.Dropdown(id='raids-dropdown',
                            placeholder='Select raid type',
                            options=[],
                            )
                ],width={'size': 4, 'offset': 4}),
        ]),
    dbc.Row(
        dcc.Loading(html.Div(id='top-stats-layout'), color='grey')
    )       
])


@app.callback(Output('raids-dropdown', 'option'),
        Output('raids-dropdown', 'value'),
        Input('url', 'pathname'))
def get_drop_down_options(url):
    options = [{'label':f'{s.raid_date} | {s.fightsummary[0].start_time} - {s.fightsummary[0].end_time} | {s.raid_type.name} | {s.name}', 'value':s.id} for s in db.session.query(Raid).order_by(Raid.raid_date.desc()).all()]
    return options, options[0]['value']


@app.callback(Output('top-stats-layout', 'children'),
              Input('raids-dropdown', 'value'))
def update_on_page_load(raid):
    return html.Div([
        html.Div(get_summary_table(raid)),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id=f'top-dmg-chart-{raid}',
                    figure=get_fig_with_model(DmgStat, 'dmg', 'Top Damage', 5, raid),
                    config=config
                ), md=12, lg=6, className='bar-chart'),     
            dbc.Col(
                dcc.Graph(
                    id=f'top-dist-chart-{raid}',
                    figure=get_fig_dist(raid),
                    config=config
                ), md=12,lg=6, className='bar-chart')
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id=f'top-stab-chart-{raid}',
                    figure=get_fig_with_model(StabStat, 'stab', 'Top Stability Output', 3, raid),
                    config=config
                ), md=12, lg=6, className='bar-chart'),     
            dbc.Col(
                dcc.Graph(
                    id=f'top-cleanse-chart-{raid}',
                    figure=get_fig_with_model(CleanseStat, 'cleanses', 'Top Condition Cleanse', 3, raid),
                    config=config
                ), md=12, lg=6, className='bar-chart')
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id=f'top-heal-chart-{raid}',
                    figure=get_fig_with_model(HealStat, 'heal', 'Top Healing Output', 3, raid),
                    config=config
                ), md=12, lg=6, className='bar-chart'),     
            dbc.Col(
                dcc.Graph(
                    id=f'top-rips-chart-{raid}',
                    figure=get_fig_with_model(RipStat, 'rips', 'Top Boon Removal', 3, raid),
                    config=config
                ), md=12, lg=6, className='bar-chart')
        ]),
    ])