from datetime import datetime
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State, MATCH, dash_table
from flask_login import current_user
from numpy import int64
from app import app, db
from models import Account, BuildType, Character, CharacterFightRating, CharacterFightStat, CleanseStat, DeathStat, DistStat, DmgStat, Fight, HealStat, PlayerStat, Profession, RipStat, StabStat, Raid
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

_build_options = [
    {'label': 'Unknown', 'value': '1'},
    {'label': 'Dps', 'value': '2'},
    {'label': 'Sup', 'value': '3'},
]


def layout():
    options = [{'label': f'{s.raid_date} | {s.fightsummary[0].start_time} - {s.fightsummary[0].end_time} | {s.raid_type.name} | {s.name}',
                'value': s.id} for s in db.session.query(Raid).order_by(Raid.raid_date.desc()).all()]
    layout = html.Div(children=[
                dbc.Container(id='details-output-data-upload',fluid=True, children=[
                    dbc.Row(id='input-row-top',class_name='input-row', children=[
                        dbc.Col([
                            html.Div("Select Raid", style={'text-align': 'center'}),
                            dcc.Dropdown(id='raids-dropdown-groups',
                                        placeholder='Select raid type',
                                        options=options,
                                        value=options[0]['value']
                                        )
                            ],width={'size': 4, 'offset': 4}),
                    ]),
                    dbc.Row([
                        html.H6("Fight #"),
                        dbc.Col(dbc.Pagination(id='fight-page', size='sm', first_last=True, previous_next=True, min_value=1, max_value=5, active_page=1))
                        ], class_name='input-row', style={'text-align': 'center'}
                    ),
                    dbc.Row([
                        dbc.Col(id='fight-group-summary')
                    ], class_name='input-row'
                    ),
                    dbc.Row([
                        dbc.Col(
                            dbc.Switch(
                                id="rating-switch",
                                label="Show Rating",
                                value=False,
                                style={
                                    'display': 'block' if current_user.is_authenticated and current_user.role.power == 100 else 'none'
                                }
                            ),
                        ) 
                    ]),
                    dbc.Row([
                        dbc.Col(id='groups-content')
                    ], id='groups-container')
                ])
            ])
    return layout


@app.callback(
    Output('fight-page', 'max_value'),
    Output('fight-page', 'active_page'),
    Input('raids-dropdown-groups', 'value')
)
def get_number_of_fights(raid):
    num_fights = db.session.query(Fight.id).filter_by(raid_id = raid).count()
    return num_fights, 1


@app.callback(
    Output('fight-group-summary', 'children'),
    Input('raids-dropdown-groups', 'value'),
    Input('fight-page', 'active_page'),
)
def show_fight_summary(raid, fight):
    fight -= 1
    fight_sum = [db.session.query(Fight).filter_by(raid_id = raid, number = fight).first().to_dict()]
    #print(fight_sum)
    fight_df = pd.DataFrame.from_dict(fight_sum)
    #print(fight_df)
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
    Input('raids-dropdown-groups', 'value'),
    Input('fight-page', 'active_page'),
    Input('rating-switch', 'value'),
)
def show_groups_content(raid, fight, rating):
    if not fight:
        fight = 0
    else:
        fight -= 1
    #print(raid)
    model = CharacterFightStat
    df_groups_prev = None
    if rating:
        model = CharacterFightRating
        if fight > 0:
            df_groups_prev = get_groups_df(raid, fight-1, model)
 
    df_groups = get_groups_df(raid, fight, model)
    if df_groups_prev is not None:
        df_groups_prev.set_index('Character')
        df_groups.set_index('Character')
        df_groups = df_groups.merge(df_groups_prev, how='left', on=['Character'], suffixes=("", "_y"))
        for stat in _stats_order:
            df_groups[f'{stat}_d'] = df_groups[stat] - df_groups[f'{stat}_y']
    else:
        for stat in _stats_order:
            df_groups[f'{stat}_d'] = 0

    #print(df_groups.head())   
    # return 

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

    start_time = datetime.strptime(db.session.query(Fight.start_time).filter_by(raid_id=raid, number=fight).scalar(), '%H:%M:%S')
    end_time = datetime.strptime(db.session.query(Fight.end_time).filter_by(raid_id=raid, number=fight).scalar(), '%H:%M:%S')
    #print(f'{start_time=}')
    duration = (end_time - start_time).total_seconds()

    #top_stats = { **top_dmg , **top_heals , **top_distance , **top_strips , **top_cleanses , **top_stab}

    table_header = [html.Thead(html.Tr([html.Th('Professions'), html.Th('Build') if current_user.is_authenticated and current_user.role.power == 100 else '']+[html.Th(stat) for stat in _stats_order]))]

    table_rows = []
    for party in df_groups['Party'].unique():
        sum_row = html.Tr(
            [html.Td([html.Div(id={'type': 'collapse-cross', 'index': str(party)}, children='-', className='collapse-cross')]+
                [html.Img(src=f'assets/profession_icons/{player}.png', className='groups-prof-icon') for player in df_groups[df_groups['Party'] == party]['Profession']], className='groups-prof-icon-col')]+
            [html.Td('') if current_user.is_authenticated and current_user.role.power == 100 else '']+
            [html.Td(f"{df_groups[df_groups['Party'] == party]['Damage'].sum():,.0f} ({df_groups[df_groups['Party'] == party]['Damage'].sum()/df_groups['Damage'].sum()*100:.0f}%)")]+
            [html.Td(format_stat(df_groups[df_groups['Party'] == party][stat].sum())) for stat in _stats_order if stat != 'Damage']
        , className='groups-row', id={'type': 'groups-row', 'index': str(party)})
        table_rows.append(html.Tbody(sum_row))

        player_rows = []
        rows = df_groups.loc[df_groups['Party'] == party]
        for i, player in df_groups.loc[df_groups['Party'] == party].iterrows():
            hover_text = f'{player["Account"]}'
            fight_id = player['FightId']
            build_type = player['BuildType']
            if player['Character'] in top_stats:
                top_text = ''.join([f'| Top {p} ' for p in top_stats[player["Character"]]])
                hover_text += top_text
            player_row = html.Tr(
                [html.Td([
                    html.Img(src=f"assets/profession_icons/{player['Profession']}.png", width='20px'),
                    html.A(player["Character"], href=f'/details/{player["Character"]}'),
                    html.Img(src='assets/logo.png', width='20px') if player["Character"] in top_stats else '',
                    dbc.Tooltip(
                        hover_text, target=f'td-{player["Character"]}', placement='right'
                    )
                ], id=f'td-{player["Character"]}')]+
                [html.Td(dbc.Select(id={'type': 'build-type-select', 'index': str(fight_id)}, options=_build_options, value=build_type, size='sm', disabled=not current_user.is_authenticated)) if current_user.is_authenticated and current_user.role.power == 100 else '']+
                [html.Td([
                    format_stat(player[stat], rating),
                    html.P(f" ({format_stat(player[f'{stat}_d'], rating)})", style={'color': get_rating_dif_col(player[f'{stat}_d']), 'display': 'inline'}) if rating else ''
                ]) for stat in _stats_order if stat != 'BuildType']
            )
            # table_rows.append(player_row)
            player_rows.append(player_row)
        player_body = html.Tbody(player_rows, hidden=False, className='groups-row-collapse-container', id={'type': 'groups-rows-toggle', 'index': str(party)})
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

    return table


def get_groups_df(raid:int, fight:int, model:db.Model) -> pd.DataFrame:
    all_players = db.session.query(
        model.id,
        Fight.number,
        model.group,
        Account.name,
        Character.name,
        Profession.name,
        model.build_type_id,
        model.damage,
        model.boonrips,
        model.cleanses,
        model.stability,
        model.healing,
        model.distance_to_tag,
        model.deaths,
        model.protection,
        model.aegis,
        model.might,
        model.fury,
        model.barrier,
        model.dmg_taken,
        ).join(model.fight).filter_by(raid_id = raid).filter_by(number = fight).join(model.character).join(Character.profession).join(Character.account).all()

    df_groups = pd.DataFrame(all_players, columns=[
        'FightId',
        'Fight',
        'Party',
        'Account', 
        'Character', 
        'Profession',
        'BuildType', 
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
    return df_groups
    

def format_stat(stat, rating=False):
    if rating:
        if pd.isna(stat):
            return '-'
        if isinstance(stat, float):
            return f'{stat:.0f}'
        else:
            return '-'
    if stat == 0 or stat == None:
        return '-'
    elif isinstance(stat, int64):
        return f'{stat:,}'
    elif isinstance(stat, float):
        return f'{stat:,.2f}'
    else:
        return f'{stat}'


def get_rating_dif_col(dif):
    col = 'grey'
    if dif > 0:
        col = 'green'
    elif dif < 0:
        col = 'red'
    return col


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


@app.callback(
    Output({'type': 'build-type-select', 'index': MATCH}, 'valid'),
    Input({'type': 'build-type-select', 'index': MATCH}, 'value'),
    State({'type': 'build-type-select', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def build_type_change(value, fight_id):
    print(f'Selected: {value}, for char_fight: {fight_id["index"]}')
    try:
        char_fight = db.session.query(CharacterFightStat).filter_by(id=fight_id['index']).first()
        print(f'{char_fight=}')
        char_fight.build_type_id = int(value)
        db.session.add(char_fight)
        db.session.commit()
        return True
    except Exception as e:
        print(f'Couldnt save build type for fight: {fight_id["index"]}')
        print(e)
        return False
