import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State, MATCH, dash_table
from app import app, db
from models import Character, CharacterFightStat, CleanseStat, DeathStat, DmgStat, Fight, HealStat, PlayerStat, Profession, RipStat, StabStat
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
                    html.H6("Fight #"),
                    dbc.Col(dbc.Pagination(id='fight-page', size='sm', first_last=True, previous_next=True, min_value=0, max_value=5, active_page=0))
                ], class_name='input-row', style={'text-align': 'center'}),
                dbc.Row([
                    dbc.Col(id='fight-group-summary')
                ], class_name='input-row'),
                dbc.Row([
                    dbc.Col(id='groups-content')
                ])
            ])
        ])


@app.callback(
    Output('fight-page', 'max_value'),
    Input('raids-dropdown', 'value')
)
def get_number_of_fights(raid):
    num_fights = db.session.query(Fight.id).filter_by(raid_id = raid).count()
    return num_fights - 1


@app.callback(
    Output('fight-group-summary', 'children'),
    Input('raids-dropdown', 'value'),
    Input('fight-page', 'active_page'),
)
def show_fight_summary(raid, fight):
    fight_sum = [db.session.query(Fight).filter_by(raid_id = raid, number = fight).first().to_dict()]
    print(fight_sum)
    fight_df = pd.DataFrame.from_dict(fight_sum)
    print(fight_df)
    return dash_table.DataTable(
        id='groups-table',
        columns=[{
            'name': i,
            'id': i,
        } for i in fight_df.columns],
        data=fight_sum,
        editable=False,
        cell_selectable=False,
        style_as_list_view=True,
        style_cell={
            'border': '1px solid #444',
            'padding': '0.5rem',
            'textAlign': 'center',
            'font-family': 'var(--bs-body-font-family)',
            'line-height': 'var(--bs-body-line-height)'
        },
        style_data={
            'backgroundColor': '#424242',
        },
        style_header={
            'backgroundColor': '#212121',
            'textAlign': 'center',
            'fontWeight': 'bold',
            'border-top': '0px',
            'border-bottom': '1px solid white'
        },
    )


@app.callback(
    Output('groups-content', 'children'),
    Input('raids-dropdown', 'value'),
    Input('fight-page', 'active_page'),
)
def show_groups_content(raid, fight):
    if not fight:
        fight = 0
    print(raid)

    all_players = db.session.query(
        Fight.number,
        CharacterFightStat.group,
        Character.name,
        Profession.name,
        CharacterFightStat.damage,
        CharacterFightStat.boonrips,
        CharacterFightStat.cleanses,
        CharacterFightStat.stability,
        CharacterFightStat.healing,
        CharacterFightStat.distance_to_tag,
        CharacterFightStat.deaths,
        CharacterFightStat.protection,
        CharacterFightStat.aegis,
        CharacterFightStat.might,
        CharacterFightStat.fury,
        CharacterFightStat.barrier,
        CharacterFightStat.dmg_taken,
        ).join(CharacterFightStat.fight).filter_by(raid_id = raid).filter_by(number = fight).join(CharacterFightStat.character).join(Character.profession).all()
    #print(all_players)
    df_groups = pd.DataFrame(all_players, columns=[
        'Fight',
        'Party', 
        'Character', 
        'Profession', 
        'Damage', 
        'Strips',
        'Cleansing', 
        'Stability', 
        'Healing', 
        'Distance', 
        'Deaths',
        'Protection',
        'Aegis',
        'Might',
        'Fury',
        'Barrier',
        'Damage In',
        ]).sort_values(['Party', 'Profession'])
    print(df_groups)

    #top_dmg = db.session.query(Character).all()

    rows= [dbc.Row([
        dbc.Col('Professions', width={'size': 3}),
        dbc.Col('Damage'),
        dbc.Col('Healing'),
        dbc.Col('Stability'),
        dbc.Col('Cleansing'),
        dbc.Col('Strips'),
        dbc.Col('Distance'),
        dbc.Col('Protection'),
        dbc.Col('Aegis'),
        dbc.Col('Might'),
        dbc.Col('Fury'),
        dbc.Col('Barrier'),
        dbc.Col('Damage In'),
        dbc.Col('Deaths'),
    ], class_name='groups-row-header')]
    for party in df_groups['Party'].unique():
        row = html.Div(dbc.Row([
            dbc.Col([html.Div(id={'type': 'collapse-cross', 'index': str(party)}, children='+', className='collapse-cross')]+
                [html.Img(src=f'assets/profession_icons/{player}.png', width='30px', className='groups-prof-icon') for player in df_groups[df_groups['Party'] == party]['Profession']], width={'size': 3}
                , class_name='groups-prof-icon-col'),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Damage'].sum():,} ({df_groups[df_groups['Party'] == party]['Damage'].sum()/df_groups['Damage'].sum()*100:.2f}%)"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Healing'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Stability'].sum():,.2f}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Cleansing'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Strips'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Distance'].sum():,.2f}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Protection'].sum():,.2f}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Aegis'].sum():,.2f}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Might'].sum():,.2f}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Fury'].sum():,.2f}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Barrier'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Damage In'].sum():,}"),
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
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Stability'].values[0]:,.2f}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Cleansing'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Strips'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Distance'].values[0]:,.2f}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Protection'].values[0]:,.2f}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Aegis'].values[0]:,.2f}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Might'].values[0]:,.2f}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Fury'].values[0]:,.2f}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Barrier'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Damage In'].values[0]:,}"),
                    dbc.Col(f"{df_groups[df_groups['Character'] == player]['Deaths'].values[0]:,}"),
                    ], class_name='groups-row-collapse') for player in df_groups.loc[df_groups['Party'] == party, 'Character']],
            hidden=True)

        #for player in df_groups[df_groups['Party'] == party]['Character']:
            #rows.append(dbc.Row(dbc.Col(player), class_name='groups-row-collapse', id={'type': 'groups-rows-toggle', 'index': str(party)}))
        rows.append(hidden_rows)
        #print(row)
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
