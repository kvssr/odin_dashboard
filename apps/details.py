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

from models import AegisStat, BarrierStat, CleanseStat, DeathStat, DistStat, DmgStat, DmgTakenStat, Fight, FightSummary, FuryStat, HealStat, MightStat, PlayerStat, ProtStat, Raid, RipStat, StabStat


tab_style={'padding': '.5rem 0',
            'cursor': 'pointer'}

layout = html.Div(children=[
    html.Div(id='details-output-data-upload', children=[
        html.Div(id='summary-table'),
        dbc.Row(id='input-row', class_name='input-row', children=[
            dbc.Col([
                "Select Raid",
                dcc.Dropdown(id='raids-dropdown',
                            placeholder='Select raid type',
                            options=[],)
                ],md=4),
        ]),
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
            dcc.Loading(html.Div(id="tab-content"), color='grey'),
        ])
    ]),   
    dcc.Store(id='intermediate-value')
])


@app.callback(Output('summary-table', 'children'),
              Input('raids-dropdown', 'value'))
def get_summary_table(raid):
    try:
        query = db.session.query(FightSummary).join(Raid).filter_by(id = raid).first()
        db.session.commit()
        df = pd.DataFrame(query.to_dict(), index=[0])
    except Exception as e:
        db.session.rollback()
        print(e)   
    return graphs.get_summary_table(df)


@app.callback(Output('raids-dropdown', 'options'),
                Input('raids-dropdown', 'value'))
def get_dropdown_raids(value):
    dropdown_options = [{'label':f'{s.id}: {s.raid_date} {s.fightsummary[0].start_time} - {s.fightsummary[0].end_time} - {s.raid_type.name}', 'value':s.id} for s in db.session.query(Raid).order_by(Raid.raid_date.desc()).all()]
    return dropdown_options


@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'active_tab'),
              Input('raids-dropdown', 'value')],
              State('intermediate-value', 'data'))
def switch_tabs(tab, raid, datasets):
    if tab == 'dmg-tab':
        try:
            query = db.session.query(DmgStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
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
                id=f'top-dmg-chart-{raid}',
                figure=fig,
            )
    elif tab == 'rips-tab':
        query = db.session.query(RipStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'rips', "Top Boons Removal", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-rip-chart-{raid}',
            figure=fig
        )
    elif tab == 'might-tab':
        graph = dcc.Graph()
        fig= {}
        query = db.session.query(MightStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        #print(df)
        fig = graphs.get_top_bar_chart(df, 'might', "Top Might Output", True)
        #print(fig)
        fig.update_layout(          
            height=1000,
        )
        return dcc.Graph(
            id=f'top-might-chart-{raid}',
            figure=fig
        )
    elif tab == 'fury-tab':
        query = db.session.query(FuryStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'fury', "Top Fury Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-fury-chart-{raid}',
            figure=fig
        )
    elif tab == 'cleanses-tab':
        query = db.session.query(CleanseStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'cleanses', "Top Conditions Cleansed", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-cleanses-chart-{raid}',
            figure=fig
        )
    elif tab == 'stab-tab':
        query = db.session.query(StabStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'stab', "Top Stability Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-stab-chart-{raid}',
            figure=fig
        )
    elif tab == 'heal-tab':
        query = db.session.query(HealStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'heal', "Top Healing Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-heal-chart-{raid}',
            figure=fig
        )
    elif tab == 'barrier-tab':
        query = db.session.query(BarrierStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'barrier', "Top Barrier Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-barrier-chart-{raid}',
            figure=fig
        )
    elif tab == 'dist-tab':
        query = db.session.query(DistStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_dist_bar_chart(df, True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-dist-chart-{raid}',
            figure=fig
        )
    elif tab == 'prot-tab':
        query = db.session.query(ProtStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'prot', "Top Protection Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-prot-chart-{raid}',
            figure=fig
        )
    elif tab == 'aegis-tab':
        query = db.session.query(AegisStat).join(PlayerStat).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_bar_chart(df, 'aegis', "Top Aegis Output", True)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-aegis-chart-{raid}',
            figure=fig
        )
    elif tab == 'dmg_taken-tab':
        query = db.session.query(DmgTakenStat).join(PlayerStat).join(Raid).filter_by(id=raid).order_by(DmgTakenStat.avg_dmg_taken_s.asc()).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_dmg_taken_chart(df, 'dmg_taken', "Least Damage Taken", False)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-dmg_taken-chart-{raid}',
            figure=fig
        )
    elif tab == 'deaths-tab':
        query = db.session.query(DeathStat).join(PlayerStat).join(Raid).filter_by(id=raid).order_by(DeathStat.times_top.desc(), PlayerStat.attendance_count.desc(), DeathStat.total_deaths.asc()).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        fig = graphs.get_top_survivor_chart(df, 'deaths', "Top Survivor", False)
        fig.update_layout(
            height=1000,
        )
        return dcc.Graph(
            id=f'top-deaths-chart-{raid}',
            figure=fig
        )
    elif tab == 'global-tab':
        #df = pd.read_json(datasets['summary'], orient='split').iloc[-1]
        query = db.session.query(FightSummary).first()
        df = pd.DataFrame(query.to_dict(), index=[0]).iloc[0]
        kd_data = {"values": [df['Kills'],df['Deaths']], "names": ['Kills','Deaths']}
        kd_fig = graphs.get_pie_chart(kd_data,'Kills/Deaths Ratio',['#262527','#87000A'])

        damage_data = {"values": [int(df['Damage'].replace(',', '')),int(df['Damage Taken'].replace(',', ''))], "names": ['Damage Output','Damage Input']}
        damage_fig = graphs.get_pie_chart(damage_data,'Damage Ratio',['#262527','#87000A'])

        pack_data = {"values": [df['⌀ Allies'],df['⌀ Enemies']], "names": ['⌀ Wolves','⌀ Lambs']}
        pack_fig = graphs.get_pie_chart(pack_data,'Wolves/Lambs Ratio',['#262527','#87000A'])

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
        query = db.session.query(Fight).join(Raid).filter_by(id=raid).all()
        df = pd.DataFrame([s.to_dict() for s in query])
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, class_name='tableFixHead')
        return table
