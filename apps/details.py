from dash.dependencies import Input, Output, State
from dash import dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask_login import current_user
from app import app, db, layout_config
import pandas as pd
from helpers import graphs

from models import AegisStat, BarrierStat, CleanseStat, DeathStat, DistStat, DmgStat, DmgTakenStat, Fight, FightSummary, FuryStat, HealStat, MightStat, PlayerStat, ProtStat, Raid, RipStat, StabStat


tab_style = {'padding': '.5rem 0',
             'cursor': 'pointer'}

subtab_style = {'padding': '.5rem 0',
                'cursor': 'pointer',
                'backgroundColor': '#222'}

tab_style_admin = {'padding': '.5rem 0',
                   'cursor': 'pointer',
                   'display': 'block' if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else 'none'}


def layout():
    options = [{'label': f'{s.raid_date} | {s.fightsummary[0].start_time} - {s.fightsummary[0].end_time} | {s.raid_type.name} | {s.name}',
                'value': s.id} for s in db.session.query(Raid).order_by(Raid.raid_date.desc()).all()]
    tab_list = layout_config['details_tabs']
    print(list(tab_list[0].keys())[0])
    print(list(tab_list[2].values())[0])
    print(list(tab_list[0].values())[0][0]['model'])
    layout = html.Div(children=[
        html.Div(id='details-output-data-upload', children=[
            dbc.Row(id='input-row-top', class_name='input-row', children=[
                dbc.Col([
                    html.Div("Select Raid", style={'text-align': 'center'}),
                    dcc.Dropdown(id='raids-dropdown',
                                 placeholder='Select raid type',
                                 options=options,
                                 value=options[0]['value'],
                                 )
                ], width={'size': 4, 'offset': 4}),
            ]),
            html.Div(id='summary-table'),
            html.Div(children=[
                dbc.Tabs(id='tabs', children=[
                    dbc.Tab(
                        label=list(tab.keys())[0],
                        tab_id=f'details-tab-{n}',
                        label_style=tab_style,
                    ) for n, tab in enumerate(tab_list)
                ], class_name='nav-justified flex-nowrap'
                ),
                dbc.Tabs(id='subtabs', class_name='nav-justified flex-nowrap'),
                dcc.Loading(html.Div(id="tab-content"), color='grey'),
            ]),
            dbc.Row(
                dbc.Col(
                    html.P(children=(['*The healing and barrier stat will only show people that run ', html.A("the healing addon",
                                                                                                              href="https://github.com/Krappa322/arcdps_healing_stats/releases", target='_blank')]), id='footnote-heal-barrier', className='text-center sm'),
                )
            )
        ]),
        dcc.Store(id='intermediate-value')
    ])
    return layout


@app.callback(
    Output('deaths-tab-id', 'tab_style'),
    #    Output('dmg-in-tab-id', 'tab_style'),
    Output('summary-tab-id', 'tab_style'),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def hide_tabs(url):
    print(url)
    if url == '/details':
        style = dict(
            display='none'
        )
        print(style)
        if current_user.is_authenticated:
            print('LOGGED IN')
            style = dict(
                display='block'
            )
        return style, style
    else:
        raise PreventUpdate


@app.callback(Output('summary-table', 'children'),
              Input('raids-dropdown', 'value'),)
def get_summary_table(raid):
    try:
        query = db.session.query(FightSummary).join(
            Raid).filter_by(id=raid).first()
        db.session.commit()
        df = pd.DataFrame(query.to_dict(), index=[0])
    except Exception as e:
        db.session.rollback()
        print(e)
    return graphs.get_summary_table(df)


@app.callback(Output('raids-dropdown', 'options'),
              Input('raids-dropdown', 'value'),
              prevent_initial_call=True)
def get_dropdown_raids(value):
    dropdown_options = [{'label': f'{s.raid_date} | {s.fightsummary[0].start_time} - {s.fightsummary[0].end_time} | {s.raid_type.name} | {s.name}',
                         'value': s.id} for s in db.session.query(Raid).order_by(Raid.raid_date.desc()).all()]
    return dropdown_options


@app.callback(Output('subtabs', 'children'),
              Output('subtabs', 'active_tab'),
              Input('tabs', 'active_tab'),
            )
def switch_tabs(tab):
    tab = int(tab.split('-')[-1])
    tab_list = layout_config['details_tabs']
    active_tab = tab_list[tab]
    print(tab)
    tabs = [
        dbc.Tab(
            label=subtab['name'],
            tab_id=f"{subtab['model']}-{x}",
            label_style=subtab_style,
            active_label_style={'backgroundColor': '#1c1c1c', 'border-bottom': '1px solid white'}
        ) for x, subtab in enumerate(list(active_tab.values())[0])
    ]
    return tabs, f"{list(active_tab.values())[0][0]['model']}-{0}"


@app.callback(Output('tab-content', 'children'),
              [Input('subtabs', 'active_tab'),
              Input('tabs', 'active_tab'),
              Input('raids-dropdown', 'value')],
              )
def switch_subtabs(tab, tabs, raid):
    tab = int(tab.split('-')[-1])
    tabs = int(tabs.split('-')[-1])
    model_dict = list(layout_config['details_tabs'][tabs].values())[0][tab]

    content = ''
    if model_dict['name'] == 'Summary':
        content = get_summary_table(raid)
    else:
        model = layout_config['model_list'][model_dict['model']]
        content = get_top_stat_graph(model, raid, model_dict['name'])
    return content


def get_top_stat_graph(model, raid, name):
    masked = False
    MAX_PLAYERS = 30
    if current_user.is_authenticated:
        masked = False
    print(f'Model for fig: {model}')
    max_attendance = db.session.query(PlayerStat.attendance_count).join(Raid).filter_by(id = raid).first()[0]
    min_attend = int(max_attendance * 0.3)
    print(f'Max Attendance: {max_attendance}')
    if isinstance(model(), DistStat):
        query = db.session.query(DistStat).join(PlayerStat).filter_by(
        raid_id=raid).filter(PlayerStat.attendance_count > min_attend).order_by(-DistStat.percentage_top).all()
        df = pd.DataFrame([s.to_dict() if i < 5 else s.to_dict(masked)
                            for i, s in enumerate(query)])                       
        fig = graphs.get_top_dist_bar_chart(df, True)
    elif isinstance(model(), DmgTakenStat):
        query = db.session.query(DmgTakenStat).join(PlayerStat).filter_by(
        raid_id=raid).filter(PlayerStat.attendance_count > min_attend).order_by(DmgTakenStat.avg_s.asc()).all()
        df = pd.DataFrame([s.to_dict() if i < 5 else s.to_dict(masked)
                          for i, s in enumerate(query)])
        fig = graphs.get_top_dmg_taken_chart(
            df, 'dmg_taken', "Least Damage Taken", False)
    elif isinstance(model(), DeathStat):
        query = db.session.query(DeathStat).join(PlayerStat).filter_by(raid_id=raid).order_by(DeathStat.times_top.desc(), PlayerStat.attendance_count.desc(), DeathStat.total.asc()).limit(MAX_PLAYERS).all()
        df = pd.DataFrame([s.to_dict() if i < 5 else s.to_dict(masked) for i, s in enumerate(query)])
        fig = graphs.get_top_survivor_chart(df, 'deaths', "Top Survivor", False)
    else:
        query = db.session.query(model).join(PlayerStat).filter_by(
        raid_id=raid).order_by(-model.total).limit(MAX_PLAYERS).all()
        df = pd.DataFrame([s.to_dict() if i < 5 else s.to_dict(masked)
                            for i, s in enumerate(query)])
        fig = graphs.get_top_bar_chart(df, model, f'Top {name}', True, True)

    fig.update_layout(
        height=30*len(df.index),
    )
    graph = dcc.Graph(
        id=f'top-{name}-chart-{raid}',
        figure=fig,
    )
    return graph


def get_summary_table(raid):
    query = db.session.query(Fight).join(Raid).filter_by(id=raid).order_by(Fight.start_time).all()
    df = pd.DataFrame([s.to_dict() for s in query])
    table = dbc.Table.from_dataframe(
        df, striped=True, bordered=True, hover=True, responsive=True, class_name='tableFixHead')
    return table
