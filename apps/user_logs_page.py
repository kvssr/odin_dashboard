from datetime import date
import dash_bootstrap_components as dbc
import requests
from sqlalchemy import func
import pandas as pd
from app import app, db
from dash import html, dcc, Output, Input, State, ALL
import dash

from dash.exceptions import PreventUpdate
from helpers import graphs
from helpers.graphs import get_logs_line_chart
from models import Account, Guild, Log


def layout():
    update_guild_members()
    logs = db.session.query(Log.log_date, func.count(Log.id)).group_by(Log.log_date).order_by(Log.log_date).all()
    df_logs = pd.DataFrame(logs, columns=['Date', 'Number'])
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
            dbc.Col(id='logs-col-graph'),
        ]),
    ])


@app.callback(
    Output('logs-col-graph', 'children'),
    Input('logs-graph','relayoutData')
)
def show_graph_selection_in_table(data):
    if not data:
        raise PreventUpdate
    #print(data)
    grouped_logs_week = ''
    start_date = ''
    guild_id = db.session.query(Guild.id).filter_by(id=1).scalar()
    if 'xaxis.range[0]' in data:
        print(data['xaxis.range[0]'].split(' ')[0])
        print(data['xaxis.range[1]'].split(' ')[0])
        start_date = data['xaxis.range[0]'].split(' ')[0]
        end_date = data['xaxis.range[1]'].split(' ')[0]
        grouped_logs_week = db.session.query(Account.name, func.count(Log.account_id).label('Number')).filter_by(guild_id=guild_id)\
        .join(Log.account).filter(Log.log_date >= start_date, Log.log_date <= end_date)\
            .group_by(Account.name)
    else:
        grouped_logs_week = db.session.query(Account.name, func.count(Log.account_id).label('Number')).filter_by(guild_id=guild_id)\
        .join(Log.account).group_by(Account.name)

    no_visits = db.session.query(Account.name).filter_by(guild_id=guild_id).filter_by(logs = None)
    print(f'{no_visits}')

    df_no_visits = pd.DataFrame(no_visits, columns=['Account'])
    df_no_visits['Number'] = 0
    print(df_no_visits)

    all_logs = grouped_logs_week.order_by(func.count(Log.account_id))
    df_all_logs = pd.DataFrame(all_logs, columns=['Account', 'Number'])
    df_all_logs = df_all_logs.append(df_no_visits).sort_values(by=['Number'])

    title = f'Total visits from {start_date} to {end_date}' if start_date != '' else 'Total visits'
    fig = graphs.get_horizontal_bar_chart(df_all_logs, x='Number', y='Account', title=title)
    visits_graph = dcc.Graph(id='visits-graph', figure=fig)

    return visits_graph
    

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


def update_guild_members():
    last_checked = db.session.query(Guild.members_updated_last).filter_by(id=1).scalar()
    print(f'{date.today()} - {last_checked}')
    if last_checked != date.today():
        guild = db.session.query(Guild).filter_by(id=1).first()
        #print(guild.leader_key)
        headers = {'Authorization': f'Bearer {guild.leader_key}'}
        request = requests.get(f'https://api.guildwars2.com/v2/guild/{guild.api_id}/members', headers=headers)
        if request.status_code == 200 or request.status_code == 206:
            members = request.json()
            #print(members)
            for member in members:
                account = db.session.query(Account).filter_by(name = member['name']).first()
                if account is None:
                    print(f'{member["name"]} doesnt exist yet')
                    continue
                    # account = Account()
                    # account.name = member['name']
                account.guild = guild
                try:
                    db.session.add(account)
                    db.session.commit()
                except Exception as e:
                    print(f'Couldnt update account: {account.name}')
                    print(e)
                print(f'Updated account: {account.name}')
        guild.members_updated_last = date.today()
        db.session.add(guild)
        db.session.commit()
        print('Members updated')
    print('members already up to date')
