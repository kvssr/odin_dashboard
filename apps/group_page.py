from tokenize import group
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State, MATCH
from app import app, db
from models import Character, CleanseStat, DeathStat, DmgStat, HealStat, PlayerStat, Profession, RipStat, StabStat
import pandas as pd

layout = html.Div(children=[
            html.Div(id='details-output-data-upload', children=[
                dbc.Row(id='input-row-top',class_name='input-row', children=[
                    dbc.Col([
                        html.Div("Select Raid", style={'text-align': 'center'}),
                        dcc.Dropdown(id='raids-dropdown',
                                    placeholder='Select raid type',
                                    options=[],
                                    )
                        ],width={'size': 4, 'offset': 4}),
                ]),
                dbc.Row([
                    dbc.Col(id='groups-content')
                ])
            ])
        ])


@app.callback(
    Output('groups-content', 'children'),
    Input('raids-dropdown', 'value')
)
def show_groups_content(raid):
    print(raid)
    all_players = db.session.query(
        PlayerStat.party, 
        Character.name, 
        Profession.name, 
        DmgStat.total_dmg, 
        HealStat.total_heal, 
        CleanseStat.total_cleanses, 
        RipStat.total_rips,
        StabStat.total_stab,
        DeathStat.total_deaths)\
            .filter_by(raid_id = raid)\
                .join(PlayerStat.character)\
                .join(Character.profession)\
                .join(PlayerStat.dmg_stat)\
                .join(PlayerStat.heal_stat)\
                .join(PlayerStat.cleanse_stat)\
                .join(PlayerStat.rip_stat)\
                .join(PlayerStat.stab_stat)\
                .join(PlayerStat.death_stat).all()
    #print(all_players)
    df_groups = pd.DataFrame(all_players, columns=['Party', 'Character', 'Profession', 'Damage', 'Healing', 'Cleansing', 'Strips', 'Stability', 'Deaths']).sort_values(['Party', 'Profession'])
    print(df_groups)

    rows= [dbc.Row([
        dbc.Col('Professions', width={'size': 3}),
        dbc.Col('Damage'),
        dbc.Col('Healing'),
        dbc.Col('Cleansing'),
        dbc.Col('Strips'),
        dbc.Col('Stability'),
        dbc.Col('Deaths'),
    ], class_name='groups-row-header')]
    for party in df_groups['Party'].unique():
        row = html.Div(dbc.Row([
            dbc.Col([html.Div(id={'type': 'collapse-cross', 'index': str(party)}, children='+', className='collapse-cross')]+
                [html.Img(src=f'assets/profession_icons/{player}.png', width='30px', className='groups-prof-icon') for player in df_groups[df_groups['Party'] == party]['Profession']], width={'size': 3}
                , class_name='groups-prof-icon-col'),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Damage'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Healing'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Cleansing'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Strips'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Stability'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Deaths'].sum():,}"),
        ], class_name='groups-row'),  id={'type': 'groups-row', 'index': str(party)})
        rows.append(row)

        hidden_rows = html.Div(
            id={'type': 'groups-rows-toggle', 'index': str(party)},
            className='groups-row-collapse-container',
            children=[
                dbc.Row([
                    dbc.Col([html.Img(src=f"assets/profession_icons/{df_groups[df_groups['Character'] == player]['Profession'].values[0]}.png", width='20px'),player], width={'size': 3}),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Damage'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Healing'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Cleansing'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Strips'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Stability'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Deaths'].values[0]:,}"),
                    ], class_name='groups-row-collapse') for player in df_groups.loc[df_groups['Party'] == party, 'Character']],
            hidden=True)

        #for player in df_groups[df_groups['Party'] == party]['Character']:
            #rows.append(dbc.Row(dbc.Col(player), class_name='groups-row-collapse', id={'type': 'groups-rows-toggle', 'index': str(party)}))
        rows.append(hidden_rows)
        print(row)
    return rows


@app.callback(
    Output({'type': 'groups-rows-toggle', 'index': MATCH}, 'hidden'),
    Output({'type': 'collapse-cross', 'index': MATCH}, 'children'),
    Input({'type': 'groups-row', 'index': MATCH}, 'n_clicks'),
    State({'type': 'groups-rows-toggle', 'index': MATCH}, 'hidden'),
    State({'type': 'collapse-cross', 'index': MATCH}, 'children'),
    prevent_initial_call=True
)
def toggle_group_rows(n, style, icon):
    print('CLICK!')
    print(style)
    print(not style)
    new_icon = '+'
    if icon == '+':
        new_icon = '-'
    return not style, new_icon
