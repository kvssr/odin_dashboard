import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State, MATCH, dash_table
from numpy import int64
from app import app, db
from models import Account, Character, CharacterFightStat, CleanseStat, DeathStat, DistStat, DmgStat, Fight, HealStat, PlayerStat, Profession, Raid, RipStat, StabStat
import pandas as pd

_stats_order = {
    'Damage':'',
    'Healing':'',
    'Stability':'2f',
    'Cleansing':'',
    'Strips':'',
    'Distance':'',
    'Protection':'2f',
    'Aegis':'2f',
    'Might':'2f',
    'Fury':'2f',
    'Barrier':'',
    'Damage In':'',
    'Deaths':'',
}


def layout():
    options = [{'label': f'{s.raid_date} | {s.fightsummary[0].start_time} - {s.fightsummary[0].end_time} | {s.raid_type.name} | {s.name}',
                'value': s.id} for s in db.session.query(Raid).order_by(Raid.raid_date.desc()).all()]
    layout = html.Div(children=[
                dbc.Container(id='details-output-data-upload',fluid=True, children=[
                    dbc.Row(id='input-row-top',class_name='input-row', children=[
                        dbc.Col([
                            html.Div("Select Raid", style={'text-align': 'center'}),
                            dcc.Dropdown(id='raids-dropdown',
                                        placeholder='Select raid type',
                                        options=options,
                                        value=options[0]['value']
                                        )
                            ],width={'size': 4, 'offset': 4}),
                    ]),
                    dbc.Row([
                        html.H6("Fight #"),
                        dbc.Col(dbc.Pagination(id='fight-page', size='sm', first_last=True, previous_next=True, min_value=1, max_value=5, active_page=1))
                    ], class_name='input-row', style={'text-align': 'center'}),
                    dbc.Row([
                        dbc.Col(id='fight-group-summary')
                    ], class_name='input-row'),
                    dbc.Row([
                        dbc.Col(id='groups-content')
                    ], id='groups-container')
                ])
            ])
    return layout


@app.callback(
    Output('fight-page', 'max_value'),
    Output('fight-page', 'active_page'),
    Input('raids-dropdown', 'value')
)
def get_number_of_fights(raid):
    num_fights = db.session.query(Fight.id).filter_by(raid_id = raid).count()
    return num_fights, 1


@app.callback(
    Output('fight-group-summary', 'children'),
    Input('raids-dropdown', 'value'),
    Input('fight-page', 'active_page'),
)
def show_fight_summary(raid, fight):
    fight -= 1
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
    else:
        fight -= 1
    print(raid)

    all_players = db.session.query(
        Fight.number,
        CharacterFightStat.group,
        Account.name,
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
        ).join(CharacterFightStat.fight).filter_by(raid_id = raid).filter_by(number = fight).join(CharacterFightStat.character).join(Character.profession).join(Character.account).all()
    #print(all_players)
    df_groups = pd.DataFrame(all_players, columns=[
        'Fight',
        'Party',
        'Account', 
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
 

    top_dmg = {name[0]:['damage'] for name in db.session.query(Character.name).join(Character.playerstats).filter_by(raid_id=raid).join(PlayerStat.dmg_stat).order_by(-DmgStat.total).limit(5).all()}
    top_heals = {name[0]:['heals'] for name in db.session.query(Character.name).join(Character.playerstats).filter_by(raid_id=raid).join(PlayerStat.heal_stat).order_by(-HealStat.total).limit(3).all()}
    top_distance = {name[0]:['distance'] for name in db.session.query(Character.name).join(Character.playerstats).filter_by(raid_id=raid).join(PlayerStat.dist_stat).order_by(-DistStat.percentage_top).limit(5).all()}
    top_strips = {name[0]:['strips'] for name in db.session.query(Character.name).join(Character.playerstats).filter_by(raid_id=raid).join(PlayerStat.rip_stat).order_by(-RipStat.total).limit(3).all()}
    top_cleanses = {name[0]:['cleanses'] for name in db.session.query(Character.name).join(Character.playerstats).filter_by(raid_id=raid).join(PlayerStat.cleanse_stat).order_by(-CleanseStat.total).limit(3).all()}
    top_stab = {name[0]:['stab'] for name in db.session.query(Character.name).join(Character.playerstats).filter_by(raid_id=raid).join(PlayerStat.stab_stat).order_by(-StabStat.total).limit(3).all()}

    top_stats = merge_dicts(top_dmg, top_heals)
    top_stats = merge_dicts(top_stats, top_distance)
    top_stats = merge_dicts(top_stats, top_strips)
    top_stats = merge_dicts(top_stats, top_cleanses)
    top_stats = merge_dicts(top_stats, top_stab)

    #top_stats = { **top_dmg , **top_heals , **top_distance , **top_strips , **top_cleanses , **top_stab}

    table_header = [html.Thead(html.Tr([html.Th('Professions')]+[html.Th(stat) for stat in _stats_order]))]

    table_rows = []
    for party in df_groups['Party'].unique():
        sum_row = html.Tr(
            [html.Td([html.Div(id={'type': 'collapse-cross', 'index': str(party)}, children='+', className='collapse-cross')]+
                [html.Img(src=f'assets/profession_icons/{player}.png', width='30px', className='groups-prof-icon') for player in df_groups[df_groups['Party'] == party]['Profession']], className='groups-prof-icon-col')]+
            [html.Td(f"{df_groups[df_groups['Party'] == party]['Damage'].sum():,} ({df_groups[df_groups['Party'] == party]['Damage'].sum()/df_groups['Damage'].sum()*100:.2f}%)")]+
            [html.Td(format_stat(df_groups[df_groups['Party'] == party][stat].sum())) for stat in _stats_order if stat != 'Damage']
        , className='groups-row', id={'type': 'groups-row', 'index': str(party)})
        table_rows.append(html.Tbody(sum_row))

        player_rows = []
        for player in df_groups.loc[df_groups['Party'] == party, 'Character']:
            hover_text = f'{df_groups.loc[df_groups["Character"] == player, "Account"].values[0]} '
            if player in top_stats:
                top_text = ''.join([f'| Top {p} ' for p in top_stats[player]])
                hover_text += top_text
            player_row = html.Tr(
                [html.Td([
                    html.Img(src=f"assets/profession_icons/{df_groups[df_groups['Character'] == player]['Profession'].values[0]}.png", width='20px'),
                    player,
                    html.Img(src='assets/logo.png', width='20px') if player in top_stats else '',
                    dbc.Tooltip(
                        hover_text, target=f'td-{player}', placement='right'
                    )
                ], id=f'td-{player}')]+
                [html.Td(format_stat(df_groups[df_groups['Character'] == player][stat].values[0])) for stat in _stats_order]
            )
            # table_rows.append(player_row)
            player_rows.append(player_row)
        player_body = html.Tbody(player_rows, hidden=True, className='groups-row-collapse-container', id={'type': 'groups-rows-toggle', 'index': str(party)})
        table_rows.append(player_body)
    # table_body = html.Tbody(table_rows)

    table = dbc.Table(
        table_header + table_rows,
        responsive=False,
        bordered=False,
        dark=True,
        hover=True,
        striped=True,
    )

    rows= [dbc.Row([
        dbc.Col('Professions', width={'size': 2}),]+
        [dbc.Col(stat) for stat in _stats_order]
    , class_name='groups-row-header')]
    for party in df_groups['Party'].unique():
        row = html.Div(dbc.Row([
            dbc.Col([html.Div(id={'type': 'collapse-cross', 'index': str(party)}, children='+', className='collapse-cross')]+
                [html.Img(src=f'assets/profession_icons/{player}.png', width='30px', className='groups-prof-icon') for player in df_groups[df_groups['Party'] == party]['Profession']], width={'size': 2}
                , class_name='groups-prof-icon-col'),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Damage'].sum():,} ({df_groups[df_groups['Party'] == party]['Damage'].sum()/df_groups['Damage'].sum()*100:.2f}%)"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Healing'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Stability'].sum():,.2f}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Cleansing'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Strips'].sum():,}"),
            dbc.Col(f"{df_groups[df_groups['Party'] == party]['Distance'].sum():,}"),
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
                    dbc.Col(id=f'col-{player}', children=[
                        html.Img(src=f"assets/profession_icons/{df_groups[df_groups['Character'] == player]['Profession'].values[0]}.png", width='20px'),
                        player,
                        html.Img(src='assets/logo.png', width='20px') if player in top_stats else '',
                        dbc.Tooltip(f'Top {top_stats[player]}', target=f'col-{player}', placement='left') if player in top_stats else ''
                        ], width={'size': 2}),]+
                    [dbc.Col(format_stat(df_groups[df_groups['Character'] == player][stat].values[0])) for stat in _stats_order]
                    , class_name='groups-row-collapse') for player in df_groups.loc[df_groups['Party'] == party, 'Character']],
            hidden=True)

        #for player in df_groups[df_groups['Party'] == party]['Character']:
            #rows.append(dbc.Row(dbc.Col(player), class_name='groups-row-collapse', id={'type': 'groups-rows-toggle', 'index': str(party)}))
        rows.append(hidden_rows)
        #print(row)
    return table


def format_stat(stat):
    if stat == 0:
        return '-'
    elif isinstance(stat, int64):
        return f'{stat:,}'
    elif isinstance(stat, float):
        return f'{stat:,.2f}'
    else:
        print(type(stat))
        print(stat)
        return ''


def merge_dicts(dict_1, dict_2):
    dict_3 = {**dict_2, **dict_1}
    for key, value in dict_3.items():
        if key in dict_1 and key in dict_2:
                dict_3[key].append(dict_2[key][0])
    return dict_3


@app.callback(
    Output({'type': 'groups-rows-toggle', 'index': MATCH}, 'hidden'),
    Output({'type': 'collapse-cross', 'index': MATCH}, 'children'),
    Input({'type': 'groups-row', 'index': MATCH}, 'n_clicks'),
    State({'type': 'groups-rows-toggle', 'index': MATCH}, 'hidden'),
    State({'type': 'collapse-cross', 'index': MATCH}, 'children'),
    prevent_initial_call=True
)
def toggle_group_rows(n, style, icon):
    new_icon = '+'
    if icon == '+':
        new_icon = '-'
    return not style, new_icon
