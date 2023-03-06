import json
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from flask import session
from flask_login import current_user
from numpy import character
from app import db, app, layout_config
from models import AegisStat, AlacStat, BarrierStat, Character, CharacterFightRating, CleanseStat, DistStat, DmgTakenStat, Fight, FuryStat, HealStat, KillsStat, MightStat, Profession, ProtStat, QuickStat, RipStat, StabStat, SupSpeedStat
from dash.dependencies import Input, Output, State
import pandas as pd
from helpers import graphs
from dash import dash_table
from sqlalchemy import func
from dash.exceptions import PreventUpdate
import dash

from models import DeathStat, DmgStat, FightSummary, PlayerStat, Raid


config = {
    'displayModeBar': False,
    'displaylogo': False,
    'scrollZoom': False,
}

column_models = {
    'Damage': [DmgStat, 'total', 'avg_s', 'Average per s', 5],
    'Rips': [RipStat, 'total', 'avg_s', 'Average per s', 3],
    'Cleanses': [CleanseStat, 'total', 'avg_s', 'Average per s', 3],
    'Stab': [StabStat, 'total', 'avg_s', 'Average per s', 3],
    'Heals': [HealStat, 'total', 'avg_s', 'Average per s', 3],
    'Sticky': [DistStat, 'percentage_top', 'percentage_top', 'Percentage Top', 5],
    'Prot': [ProtStat, 'total', 'avg_s', 'Average per s', 3],
    'Aegis': [AegisStat, 'total', 'avg_s', 'Average per s', 3],
    'Might': [MightStat, 'total', 'avg_s', 'Average per s', 2],
    'Fury': [FuryStat, 'total', 'avg_s', 'Average per s', 2],
    'Barrier': [BarrierStat, 'total', 'avg_s', 'Average per s', 3],
    'Quick': [QuickStat, 'total', 'avg_s', 'Average per s', 3],
    'Alac': [AlacStat, 'total', 'avg_s', 'Average per s', 3],
    'SSpeed': [SupSpeedStat, 'total', 'avg_s', 'Average per s', 3],
    'Dmg In': [DmgTakenStat, 'times_top', 'times_top', 'Times Top', 5],
    'Deaths': [DeathStat, 'times_top', 'times_top', 'Times Top', 5]
}


def layout(name):
    # if current_user.is_authenticated:
    characters = db.session.query(Character).filter(Character.id.in_(db.session.query(PlayerStat.character_id).distinct()))\
                            .join(Profession).order_by(Profession.name, Character.name).all()
    dropdown_options = [{'label':f'{s.name} - {s.profession.name}', 'value':s.id} for s in characters]
    # else:
    #     characters = db.session.query(Character).filter(Character.name.in_(session['CHARACTERS'])).filter(Character.id.in_(db.session.query(PlayerStat.character_id).distinct()))\
    #                             .join(Profession).order_by(Profession.name, Character.name).all()
    #     dropdown_options = [{'label':f'{s.name} - {s.profession.name}', 'value':s.id} for s in characters]

    character_id = 0
    if name != '':
        fullname = name
        name = name.split('(')[0].rstrip()
        if len(fullname.split('(')) > 1:
            abbr = fullname.split("(")[1][0:-1]
            character_id = db.session.query(Character.id).filter_by(name = name).join(Profession).filter_by(abbreviation=abbr).first()[0]
        else:
            character_id = db.session.query(Character.id).filter_by(name = name).first()[0]
    elif 'CHARACTERS' in session and len(session['CHARACTERS']) > 0:
        character_id = db.session.query(Character.id).filter_by(name = session['CHARACTERS'][0]).first()[0]
    else:
        character_id = dropdown_options[0]['value']
        print(dropdown_options[0]['value'])

    raids_dict = [s.to_dict() for s in db.session.query(PlayerStat).filter_by(character_id=character_id).join(Raid).join(FightSummary).order_by(Raid.raid_date.desc(), FightSummary.start_time.desc()).all()]
    #print(f'raids_dict: {raids_dict}')
    raids_df = pd.DataFrame(raids_dict)
    #print(f'raids_df: {raids_df}')

    # OLD PART. ONLY ADMINS COULD SEE ALL THE STATS
    # enabled_columns = ['Date', 'Start Time', 'Damage', 'Rips', 'Cleanses', 'Stab', 'Healing', 'Sticky', 'Prot', 'Aegis', 'Might', 'Fury', 'Barrier']
    # if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
    enabled_columns = [c for c in raids_df.columns if c not in ['Name', 'character_id', 'raid_id', 'Deaths']]

    tab_style = {'padding': '.5rem 0',
             'cursor': 'pointer'}
    layout = [
        dbc.Row(class_name='input-row', children=[
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Raids Attended"),
                    dbc.CardBody(id='raids-attended', class_name='pers-stat-card-body')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Fights Attended"),
                    dbc.CardBody(id='fights-attended', class_name='pers-stat-card-body')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Fights Missed"),
                    dbc.CardBody(id='fights-missed', class_name='pers-stat-card-body')
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Times Top", id='times-top-header'),
                    dbc.CardBody(id='times-top', class_name='pers-stat-card-body')
                ])
            ]),
        ]),
        dbc.Row(class_name='input-row', children=[
            dbc.Col(dcc.Dropdown(
                id='name-dropdown-pers',
                options=dropdown_options,
                value=character_id
                ), width={'size': 4 , 'offset': 4}
            ),
            dbc.Col(dbc.Switch(
                            id="rating-switch-pers",
                            label="Show Rating",
                            value=False,
                            style={
                                'display': 'block' if current_user.is_authenticated and current_user.role.power >= 50 else 'none'
                            }
                    ), width={'size': 1}
            ),
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Loading(html.Div(id='raids-graph'), color='grey'),
                width={}
            ),
            dbc.Col(
                dcc.Loading(html.Div(id='raids-top10'), color='grey'),
                id='raids-top10-col',
                width={'size': 4}
            )
        ]),
        dbc.Row([
            dbc.Tabs(id='tabs-buildtype-pers', children=[
                    dbc.Tab(
                        label='Damage',
                        tab_id='dps-tab-pers-2',
                        label_style=tab_style,
                    ),
                    dbc.Tab(
                        label='Support',
                        tab_id='sup-tab-pers-3',
                        label_style=tab_style,
                    ),
                ], class_name='nav-justified flex-nowrap',
                active_tab = 'dps-tab-pers-2'
                ),
        ]),
        dbc.Row([
            dbc.Col(id='personal-raids-table', children=[
                dash_table.DataTable(
                id='pers-raids-table',
                columns=[{
                    'name': f'{i}*' if i in ['Healing', 'Barrier'] else i,
                    'id': i,
                    'selectable': True if i not in ['Date', 'Start Time', 'Name'] else False,
                } for i in enabled_columns],
                data=raids_dict,
                editable=False,
                row_selectable='multi',
                column_selectable='single',
                cell_selectable=False,
                style_as_list_view=True,
                selected_columns=['Damage'],
                selected_rows=[s for s in range(len(raids_df))],
                #sort_action='native',
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
                    'border-bottom': '1px solid white',
                },
            )
            ]),
        ]),
        dbc.Row(
            dbc.Col([
                html.P(children=([f'*The healing and barrier stat will only show values for people that run ', html.A("the healing addon", href="https://github.com/Krappa322/arcdps_healing_stats/releases", target='_blank')]), id='footnote-heal-barrier', className='text-center sm'),        
            ])
        ),
        dcc.Store(id='hover-store')
    ]
    return layout


@app.callback(
    Output('pers-raids-table', 'column_selectable'),
    Input('rating-switch-pers', 'value'),
)
def switch_table_col_selection(switch):
    selectable = 'single'
    if switch:
        selectable = 'multi'
    return selectable


@app.callback(
    Output('pers-raids-table', 'data'),
    Input('name-dropdown-pers', 'value'),
    Input('rating-switch-pers', 'value'),
    Input('tabs-buildtype-pers', 'active_tab')
)
def update_raids_table(character, rating_switch, active_tab):
    build_type = int(active_tab[-1])
    print(f'{build_type=}')
    if not rating_switch:
        raids_dict = [s.to_dict() for s in db.session.query(PlayerStat).filter_by(character_id=character).join(Raid).join(FightSummary).order_by(Raid.raid_date.desc(), FightSummary.start_time.desc()).all()]
    else:
        all_raids = [s for (s,) in db.session.query(Raid.id)\
                     .join(Fight).join(CharacterFightRating)\
                        .filter_by(character_id=character, build_type_id=build_type)\
                            .order_by(Raid.raid_date.desc())\
                                .distinct()]
        print(f'{all_raids=}')
        if not all_raids:
            raise PreventUpdate
        raids_dict = get_rating_per_character_for_raids(character, all_raids, build_type).round(0).to_dict('records')
    return raids_dict


def get_rating_per_character_for_raids(character_id:int, raids:list, build_type:int) -> pd.DataFrame:
    print('get_rating_per_character_for_raids')
    print(raids)
    df = pd.DataFrame
    for raid in raids:
        raid_date = db.session.query(Raid.raid_date).filter_by(id=raid).first()[0]
        print(f'{raid_date=}')
        raid_stats = db.session.query(CharacterFightRating).filter_by(character_id=str(character_id), build_type_id=build_type).join(CharacterFightRating.fight).filter_by(raid_id=raid)\
            .order_by(CharacterFightRating.id.desc()).first()
        if raid_stats is None:
            continue
        raid_stats = raid_stats.to_dict()
        raid_stats['raid_date'] = raid_date
        raid_stats['raid_id'] = raid
        print(f'{raid_stats=}')
        if df.empty:
            df = pd.DataFrame(raid_stats, columns = raid_stats.keys(), index=['id'])
        else:
            df = df.append(raid_stats, ignore_index=True)

    return df


@app.callback(
    Output('raids-attended', 'children'),
    Output('fights-attended', 'children'),
    Output('fights-missed', 'children'),
    Output('times-top', 'children'),
    Output('times-top-header', 'children'),
    Input('name-dropdown-pers', 'value'),
    Input('pers-raids-table', 'selected_columns'),
)
def update_highest_stats(character, col):
    raids_attended = db.session.query(func.count(PlayerStat.id)).filter_by(character_id=character).first()[0]
    fights_attended = db.session.query(func.sum(PlayerStat.attendance_count)).filter_by(character_id=character).first()[0] 
    fights_attended = 0 if fights_attended is None else fights_attended 

    raids = db.session.query(PlayerStat.raid_id).filter_by(character_id=character).subquery().select()
    total_fights = db.session.query(func.count(Fight.id)).filter(Fight.raid_id.in_(raids)).filter_by(skipped=False).first()[0]
    fights_missed = total_fights - fights_attended

    if col:
        model = column_models[col[0]][0]
        times_top = db.session.query(func.sum(model.times_top)).join(PlayerStat).filter_by(character_id=character).first()[0]
    return (raids_attended, fights_attended, fights_missed, times_top, f'Times Top: {col[0]}')


@app.callback(
    Output('raids-graph', 'children'),
    Input('pers-raids-table', 'selected_columns'),
    Input('pers-raids-table', 'derived_virtual_selected_rows'),
    Input('pers-raids-table', 'data'),
    Input('rating-switch-pers', 'value'),
    prevent_initial_call=True
)
def show_selected_column(col, rows, data, switch):
    print(f'col: {col}'),
    print(f'rows: {rows}')
    # print(f'data: {data}')
    if data and rows and col is not None and col[0] in column_models:
        selected_raids = [data[s]['raid_id'] for s in rows]

        if not switch:
            df_p = pd.DataFrame(data)
            print(df_p.head())
            fig = get_value_graph(col, df_p, selected_raids)
        elif switch:
            selected_data = [data[s] for s in rows]
            df_s = pd.DataFrame(selected_data)
            print(df_s.head())
            fig = get_rating_graph(col, df_s)
        else:
            return None
        return dcc.Graph(id='personal-graph',figure=fig, style={'height': 500}, config=config)
    raise PreventUpdate


def get_rating_graph(cols, df_p):
    df_p.sort_values(by=['raid_date'], inplace=True)
    #print(df)
    # selected_cols = [column_models[col][1] for col in cols]
    fig = graphs.get_rating_line_chart(df_p, cols)
    return fig


def get_value_graph(col, df_p, selected_raids):

    # Get model and attribute depending on selected column
    model = column_models[col[0]][0]
    model_attr = getattr(column_models[col[0]][0], column_models[col[0]][2])


    df_p['mode'] = 'markers+lines'
    df_p['fill'] = 'none'
    profession = db.session.query(Character).filter_by(id = str(df_p['character_id'][0])).join(Profession).first().profession
    df_p['Profession_color'] = profession.color
    df_p['Profession'] = profession.name

    df_p = df_p[df_p['raid_id'].isin(selected_raids)]
    min_max = func.max(model_attr)

    for raid in df_p['raid_id']:
        raid_date = df_p.loc[df_p['raid_id']==raid, 'Date'].item()
        raid_time = df_p.loc[df_p['raid_id']==raid, 'Start Time'].item()
        raid_date = f'{raid_date} {raid_time}'

        max_attendance = db.session.query(PlayerStat.attendance_count).join(Raid).filter_by(id = raid).first()[0]
        print(f'Max Attendance: {max_attendance}')
        min_attend = int(max_attendance * 0.2)
        
        df_p.loc[df_p['raid_id']==raid, 'Date'] = raid_date
        if col[0] == 'Sticky':
            df_p.loc[df_p['raid_id']==raid, col[0]] = int(df_p.loc[df_p['raid_id']==raid, col[0]].item().split('%')[0])

        ### Get Lowest Profession
        bot_prof_value = db.session.query(func.min(model_attr)).join(PlayerStat).filter_by(raid_id=raid).filter(PlayerStat.attendance_count > min_attend).join(Character).join(Profession).filter_by(name=profession.name).group_by(PlayerStat.raid_id).scalar()
        df_bot_prof = pd.DataFrame(
            [[raid, raid_date, 'Last Prof', bot_prof_value, profession.color, profession.name, 'lines', 'none']],
            columns=['raid_id', 'Date', 'Name', col[0], 'Profession_color', 'Profession', 'mode', 'fill']
        )
        df_p = df_p.append(df_bot_prof)

        ### Get Top Profession
        top_prof_value = db.session.query(min_max).join(PlayerStat).filter_by(raid_id=raid).filter(PlayerStat.attendance_count > min_attend).join(Character).join(Profession).filter_by(name=profession.name).group_by(PlayerStat.raid_id).scalar()
        df_top_prof = pd.DataFrame(
            [[raid, raid_date, 'First Prof', top_prof_value, profession.color, profession.name, 'none', 'tonextx']],
            columns=['raid_id', 'Date', 'Name', col[0], 'Profession_color', 'Profession', 'mode', 'fill']
        )
        df_p = df_p.append(df_top_prof)

        ### Get Top Player
        top_value = db.session.query(min_max).join(PlayerStat).filter_by(raid_id=raid).filter(PlayerStat.attendance_count > min_attend).group_by(PlayerStat.raid_id).scalar()
        top_char = db.session.query(Character).join(PlayerStat).filter_by(raid_id=raid).join(model).filter(model_attr==top_value).first()
        profession2 = top_char.profession.name
        profession_color = top_char.profession.color
        df_top_n = pd.DataFrame([[raid, raid_date, '#1 Person', top_value, profession_color, profession2, 'lines', 'none']], 
            columns=['raid_id', 'Date', 'Name', col[0], 'Profession_color', 'Profession', 'mode', 'fill'])
        df_p = df_p.append(df_top_n.head())

    
    fig = graphs.get_personal_chart(df_p, col[0])
    return fig


@app.callback(
    Output('raids-top10', 'children'),
    Output("pers-raids-table", "style_data_conditional"),
    Output('hover-store', 'data'),
    Input('personal-graph', 'hoverData'),
    Input('pers-raids-table', 'selected_columns'),
    Input('name-dropdown-pers', 'value'),
    State('pers-raids-table', 'selected_rows'),
    State('pers-raids-table', 'data'),
    State('hover-store', 'data'),
    State('rating-switch-pers', 'value'),
    prevent_initial_call=True)
def display_hover_data(hoverData, col, drop, rows, data, hoverstore, rating_switch):
    print(hoverData)
    print(f'HOVERSTORE: {hoverstore}')

    ctx = dash.callback_context
    if rating_switch:
        return None, None, None
    if ctx.triggered:
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'name-dropdown-pers':
            return None, None, None

    if hoverData or hoverstore:        
        masked = False
        if current_user.is_authenticated:
            masked = False
        if hoverData:
            raid = hoverData['points'][0]['customdata']
            raid_date = hoverData['points'][0]['x']
            selected_raid = [s for s in rows if data[s]['raid_id']==raid]
        else:
            hoverstore = json.loads(hoverstore)
            raid = hoverstore[0]
            raid_date = hoverstore[1]
            selected_raid = hoverstore[2]
        model = column_models[col[0]][0]
        model_attr = getattr(column_models[col[0]][0], column_models[col[0]][2])
        show_limit = column_models[col[0]][4]

        max_attendance = db.session.query(PlayerStat.attendance_count).join(Raid).filter_by(id = raid).first()[0]
        print(f'Max Attendance: {max_attendance}')
        min_attend = int(max_attendance * 0.2)
        stat_list = db.session.query(model).filter(model_attr > 0).order_by(-model_attr).join(PlayerStat).filter_by(raid_id = raid).filter(PlayerStat.attendance_count > min_attend).limit(10).all()
        df = pd.DataFrame([s.to_dict(masked) if i >= show_limit else s.to_dict() for i, s in enumerate(stat_list)])
        fig = graphs.get_top_bar_chart_p(df, column_models[col[0]][3], raid_date)
        highlight = [{"if": {"row_index":selected_raid[0]}, "backgroundColor": "grey"},]

        return dcc.Graph(figure=fig, style=dict(height='500px'), config=config), highlight, json.dumps([raid, raid_date, selected_raid])
    raise PreventUpdate


@app.callback(
    Output('pers-raids-table', 'selected_rows'),
    Input('pers-raids-table', 'data'),
)
def select_all_rows(data):
    if data:
        rows = [s for s in range(len(data))]
        print(f'DATA::::{rows}')
        return rows

