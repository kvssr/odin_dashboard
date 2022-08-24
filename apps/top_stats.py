from dash.dependencies import Input, Output, State, MATCH, ALL
from dash import dcc, html
import dash_bootstrap_components as dbc
from itsdangerous import json
from helpers import graphs
from flask_login import current_user

import pandas as pd
from app import app, db, layout_config
from models import DistStat, FightSummary, PlayerStat, Raid


config = {
    'displayModeBar': False,
    'displaylogo': False,
    'scrollZoom': False,
    'staticPlot': True
}


def get_fig_with_model(model, t, title, limit, raid):
    if model == DistStat:
        return get_fig_dist(raid)
    try:
        dmg_list = db.session.query(model).order_by(-model.total).join(
            PlayerStat).join(Raid).filter_by(id=raid).limit(limit).all()

        if dmg_list:
            df = pd.DataFrame([s.to_dict() for s in dmg_list])
            fig = graphs.get_top_bar_chart(df, model, title)
            return fig
    except Exception as e:
        print(e)


def get_fig_dist(raid):
    try:
        dist_list = db.session.query(DistStat).order_by(-DistStat.percentage_top).join(
            PlayerStat).join(Raid).filter_by(id=raid).limit(5).all()

        if dist_list:
            df = pd.DataFrame([s.to_dict() for s in dist_list])
            fig = graphs.get_top_dist_bar_chart(df)
            return fig
    except Exception as e:
        print(e)


def get_summary_table(raid):
    df = []
    try:
        query = db.session.query(FightSummary).join(
            Raid).filter_by(id=raid).first()
        db.session.commit()
        df = pd.DataFrame(query.to_dict(), index=[0])
    except Exception as e:
        db.session.rollback()
        print(e)

    return graphs.get_summary_table(df)


def layout():
    layout = html.Div(children=[
        dbc.Row(id='input-row-top', class_name='input-row', children=[
                dbc.Col([
                    html.Div("Select Raid", style={'text-align': 'center'}),
                    dcc.Dropdown(id='raids-dropdown',
                                 placeholder='Select raid type',
                                 options=[],
                                 ),
                ], width={'size': 4, 'offset': 4}),
                ]),
        dbc.Row([
            dbc.Switch(
                id="edit-switch",
                label="EditMode",
                value=False,
                style={'display': 'block'} if current_user.is_authenticated else {'display': 'none'}),
            html.Div(id='top-stats-layout', className='row')
        ]),
        dcc.Store(id='order-status')
    ])
    return layout


@app.callback(Output('raids-dropdown', 'option'),
              Output('raids-dropdown', 'value'),
              Input('url', 'pathname'))
def get_drop_down_options(url):
    options = [{'label': f'{s.raid_date} | {s.fightsummary[0].start_time} - {s.fightsummary[0].end_time} | {s.raid_type.name} | {s.name}',
                'value': s.id} for s in db.session.query(Raid).order_by(Raid.raid_date.desc()).all()]
    return options, options[0]['value']


@app.callback(Output('top-stats-layout', 'children'),
              Input('raids-dropdown', 'value'),
              Input('order-status', 'data'),
              State('edit-switch', 'value')
              )
def update_on_page_load(raid, data, editmode):
    stats_shown = layout_config['top_page_stats']
    stats_models = layout_config['model_list']

    cols = [dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div(id={'type': 'edit-row', 'index': x}, hidden=not editmode, children=[
                    dbc.Label('Position',
                              align='center',
                              className='edit-item',
                              ),
                    dbc.Select(
                        id={'type': 'slct-pos', 'index': x},
                        className='edit-item',
                        style={'max-width': '60px'},
                        value=x,
                        options=[
                            {'label': n+1, 'value': n} for n in range(len(stats_shown))
                        ]
                    ),
                    dbc.Label('Limit',
                              className='edit-item'),
                    dbc.Input(
                        id={'type': 'input-limit', 'index': x},
                        type='number',
                        min=1,
                        max=10,
                        value=row['top_limit'],
                        size='sm',
                        className='edit-item',
                        style={'max-width': '60px'}
                    ),
                    dbc.Label('Model',
                              className='edit-item'),
                    dbc.Select(
                        id={'type': 'slct-model', 'index': x},
                        className='edit-item',
                        style={'max-width': '120px'},
                        value=list(stats_models.keys()).index(row['model_name']),
                        options=[
                            {'label': s, 'value': ix} for ix, s in enumerate(stats_models)
                        ]
                    ),
                    dbc.Button(
                        'Delete',
                        id={'type': 'btn-delete', 'index': x},
                        className='btn btn-primary edit-item btn-delete-graph',
                    ),
                ], className='edit-row', style={'display': 'flex'}),
                dcc.Loading(
                    dcc.Graph(
                        id={'type': 'top-graph', 'index': x},
                        figure=get_fig_with_model(
                            stats_models[row['model_name']], 'dmg', f'Top {row["name"]}', row['top_limit'], raid),
                        config=config
                    ), color='grey'
                )
            ])
        ]),
    ],
        md=12,
        lg=6,
        className='bar-chart',
        id=f'graph-{x}'
    ) for x, row in enumerate(stats_shown)]
    return cols


@app.callback(
    Output({'type': 'edit-row', 'index': MATCH}, 'hidden'),
    Input('edit-switch', 'value'),
    prevent_initial_call=True
)
def toggle_editmode(editmode):
    return not editmode


@app.callback(
    Output({'type': 'top-graph', 'index': MATCH}, 'figure'),
    Input({'type': 'input-limit', 'index': MATCH}, 'value'),
    Input({'type': 'slct-model', 'index': MATCH}, 'value'),
    State({'type': 'top-graph', 'index': MATCH}, 'id'),
    State('raids-dropdown', 'value'),
    prevent_initial_call=True
)
def update_graph(limit, model, id, raid):
    stat = {}
    stat['model_name'] = list(layout_config['model_list'].keys())[int(model)]
    stat['name'] = stat['model_name']
    stat['model'] = layout_config['model_list'][stat['name']]
    layout_config['top_page_stats'][id['index']] = stat
    stat['top_limit'] = limit
    figure = get_fig_with_model(
        stat['model'], 'dmg', f'Top {stat["name"]}', stat['top_limit'], raid)
    return figure


@app.callback(
    Output('order-status', 'data'),
    Input({'type': 'slct-pos', 'index': ALL}, 'value'),
    Input({'type': 'slct-pos', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def change_graph_position(values, index):
    stats = layout_config['top_page_stats']
    old_p = 0
    new_p = 0
    for x, i in enumerate(values):
        if x != i:
            old_p = x
            new_p = int(i)
            break
    temp_row = stats.pop(old_p)
    stats.insert(new_p, temp_row)
    return json.dumps(f'{old_p}:{new_p}')
