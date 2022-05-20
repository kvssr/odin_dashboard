import datetime
import json
import dash_bootstrap_components as dbc
import plotly.express as px
from sqlalchemy import func
import pandas as pd
from app import app, db
from dash import html, dcc, Output, Input, State, MATCH, ALL, dash_table
import dash

from dash.exceptions import PreventUpdate
from helpers.graphs import get_logs_line_chart
from models import Account, Log


def layout():
    logs = db.session.query(Log.log_date, func.count(Log.id)).group_by(Log.log_date).order_by(Log.log_date).all()
    df_logs = pd.DataFrame(logs, columns=['Date', 'Number'])
    #print(df_logs)
    fig = get_logs_line_chart(df_logs)

    accounts = db.session.query(Account).order_by(Account.name).all()
    dropdown_options = [{'label':f'{s.name}', 'value':s.id} for s in accounts]

    return html.Div(id='user-logs-container', children=[
        dbc.Row([
            dbc.Col(
                dcc.Graph(id='logs-graph', figure=fig)
            )
        ]),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='log-search-account', options=dropdown_options, value=dropdown_options[0]['value'])),
            dbc.Col(id='account-log-output'),
        ]),
        dbc.Row(class_name='logs-row', children=[
            dbc.Col(id='logs-col-top'),
            dbc.Col(id='logs-col-bot'),
        ])
    ])


@app.callback(
    Output('logs-col-top', 'children'),
    Output('logs-col-bot', 'children'),
    Input('logs-graph','relayoutData')
)
def show_graph_selection_in_table(data):
    if not data:
        raise PreventUpdate
    #print(data)
    grouped_logs_week = ''
    if 'xaxis.range[0]' in data:
        print(data['xaxis.range[0]'].split(' ')[0])
        print(data['xaxis.range[1]'].split(' ')[0])
        start_date = data['xaxis.range[0]'].split(' ')[0]
        end_date = data['xaxis.range[1]'].split(' ')[0]
        grouped_logs_week = db.session.query(Account.name, func.count(Log.account_id).label('Number'))\
        .join(Log.account).filter(Log.log_date >= start_date, Log.log_date <= end_date)\
            .group_by(Account.name)
    else:
        grouped_logs_week = db.session.query(Account.name, func.count(Log.account_id).label('Number'))\
        .join(Log.account).group_by(Account.name)

    top_logs_week = grouped_logs_week.order_by(-func.count(Log.account_id)).limit(10).all()
    bot_logs_week = grouped_logs_week.order_by(func.count(Log.account_id)).limit(10).all()

    df_top_logs_week = pd.DataFrame(top_logs_week, columns=['Account', 'Number'])
    df_bot_logs_week = pd.DataFrame(bot_logs_week, columns=['Account', 'Number'])

    #print(df_top_logs_week)
    #return get_data_table(df_top_logs_week, 'Top # Visits'), get_data_table(df_bot_logs_week, 'Bottom # Visits')
    return get_table(df_top_logs_week, 'Top # Visits'), get_table(df_bot_logs_week, 'Bottom # Visits')
    

@app.callback(
    Output('account-log-output', 'children'),
    Input('logs-graph','relayoutData'),
    Input('log-search-account', 'value'),
)
def show_account_table(graph_data, account):
    if not account or not graph_data:
        raise PreventUpdate

    name = db.session.query(Account.name).filter_by(id = account).first()[0]
    total_visits = db.session.query(func.count(Log.id)).filter_by(account_id=account).scalar()
    last_visit = db.session.query(Log.log_date).filter_by(account_id=account).order_by(Log.log_date.desc()).limit(1).scalar()
    first_visit = db.session.query(Log.log_date).filter_by(account_id=account).order_by(Log.log_date).limit(1).scalar()
    total_selection = 0

    if 'xaxis.range[0]' in graph_data:
        #print(datetime.datetime.strptime(graph_data['xaxis.range[0]'], '%Y-%m-%d'))
        start_date = graph_data['xaxis.range[0]'].split(' ')[0]
        end_date = graph_data['xaxis.range[1]'].split(' ')[0]
        total_selection = db.session.query(func.count(Log.account_id)).filter_by(account_id = account).filter(Log.log_date >= start_date, Log.log_date <= end_date).scalar()
    else:
        total_selection = db.session.query(func.count(Log.account_id)).filter_by(account_id = account).scalar()

    print(f'account: {account} - name: {name}')
    table = html.Div(id='account-logs-table', children=[
        dbc.Row([
            dbc.Col('Name:', class_name='left-table-header'),
            dbc.Col(name),
        ]),
        dbc.Row([
            dbc.Col('First visit:', class_name='left-table-header'),
            dbc.Col(first_visit),
        ]),
        dbc.Row([
            dbc.Col('Last visit:', class_name='left-table-header'),
            dbc.Col(last_visit),
        ]),
        dbc.Row([
            dbc.Col('Total visits:', class_name='left-table-header'),
            dbc.Col(total_visits),
        ]),
        dbc.Row([
            dbc.Col('Total selection visits:', class_name='left-table-header'),
            dbc.Col(total_selection),
        ]),
    ])
    
    return table


def get_table(df, name):
    table = html.Div(id=f'logs-table-{name}', children=[
        dbc.Row(
            dbc.Col(name),
            class_name='table-title'
        ),
        dbc.Row([
            dbc.Col("Account"),
            dbc.Col("Number"),
        ],
        class_name='table-header')]+
        [html.Div(id={'type': 'log-row', 'index': account['Account']},children=dbc.Row(children=[
            dbc.Col(account['Account']),
            dbc.Col(account['Number']),
        ],
        class_name='table-row')) for i, account in df.iterrows()]
    )
    
    return table


@app.callback(
    Output('log-search-account', 'value'),
    Input({'type': 'log-row', 'index': ALL}, 'n_clicks'),
    State({'type': 'log-row', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def click_table_row(n, value):
    ctx = dash.callback_context
    if not ctx.triggered:
        name = 'No clicks yet'
    elif len(ctx.triggered) == 1:
        name = ctx.triggered[0]['prop_id'].split('"')[3]
        account_id = db.session.query(Account.id).filter_by(name = name).first()[0]
        return account_id
    raise PreventUpdate
