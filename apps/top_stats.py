import base64
import io

from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px

import pandas as pd
from app import app

profession_colours = {
    'Guardian': '#186885',
    'Dragonhunter': '#186885',
    'Firebrand': '#186885',
    'Revenant': '#661100',
    'Herald': '#661100',
    'Renegade': '#661100',
    'Warrior': '#CAAA2A',
    'Berserker': '#CAAA2A',
    'Spellbreaker': '#CAAA2A',
    'Engineer': '#87581D',
    'Scrapper': '#87581D',
    'Holosmith': '#87581D',
    'Ranger': '#67A833',
    'Druid': '#67A833',
    'Soulbeast': '#67A833',
    'Thief': '#974550',
    'Daredevil': '#974550',
    'Deadeye': '#974550',
    'Elementalist': '#DC423E',
    'Tempest': '#DC423E',
    'Weaver': '#DC423E',
    'Mesmer': '#69278A',
    'Chronomancer': '#69278A',
    'Mirage': '#69278A',
    'Necromancer': '#2C9D5D',
    'Reaper': '#2C9D5D',
    'Scourge': '#2C9D5D',

}
profession_shorts = {
    'Guardian': 'Gnd',
    'Dragonhunter': 'Dgh',
    'Firebrand': 'Fbd',
    'Revenant': 'Rev',
    'Herald': 'Her',
    'Renegade': 'Ren',
    'Warrior': 'War',
    'Berserker': 'Brs',
    'Spellbreaker': 'Spb',
    'Engineer': 'Eng',
    'Scrapper': 'Scr',
    'Holosmith': 'Hls',
    'Ranger': 'Rgr',
    'Druid': 'Dru',
    'Soulbeast': 'Slb',
    'Thief': 'Thf',
    'Daredevil': 'Dar',
    'Deadeye': 'Ded',
    'Elementalist': 'Ele',
    'Tempest': 'Tmp',
    'Weaver': 'Wea',
    'Mesmer': 'Mes',
    'Chronomancer': 'Chr',
    'Mirage': 'Mir',
    'Necromancer': 'Nec',
    'Reaper': 'Rea',
    'Scourge': 'Scg',
}

layout = dbc.Container(id='container', children=[
    dbc.Row(id='header', children=[
        html.Img(id='logo', className='col-sm-1', src='../assets/logo.png'),
        dbc.Col(children=[
            html.H1('ODIN Carrot Awards', 'title'),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                # Allow multiple files to be uploaded
                multiple=True
            )])]),
    html.Hr(),
    html.Div(id='output-data-upload'),
])


def get_short_profession(profession):
    return "(" + profession_shorts[profession] + ")"


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), sheet_name='dmg')
            df_dmg = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='rips')
            df_rips = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='stab')
            df_stab = df.head(5)

            df = pd.read_excel(io.BytesIO(decoded), sheet_name='cleanses')
            df_cleanses = df.head(5)

            #for index, row in df.iterrows():
                #df.at[index, 'Name'] = "{:<25}".format(row['Name']) + get_short_profession(row['Profession']) + " "

            fig_dmg = get_top_damage_chart(df_dmg)
            fig_rips = get_top_rips_chart(df_rips)
            fig_stab = get_top_stab_chart(df_stab)
            fig_cleanses = get_top_cleanses_chart(df_cleanses)

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-dmg-chart',
                    figure=fig_dmg
                ), md=6),
            dbc.Col(
                dcc.Graph(
                    id='top-rips-chart',
                    figure=fig_rips
                ), md=6)
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='top-stab-chart',
                    figure=fig_stab
                ), md=6),
            dbc.Col(
                dcc.Graph(
                    id='top-cleanses-chart',
                    figure=fig_cleanses
                ), md=6)
        ])
    ])


def get_top_damage_chart(df_dmg):
    fig = px.bar(df_dmg, y="Name", x="Total dmg", color="Profession", text="Total dmg", barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours)
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#EEE',
        title="Top Damage",
        showlegend=False,
    )
    # adds the labels for dmg/s and times top/attendance
    for name in df_dmg["Name"]:
        fig.add_annotation(y=name, x=df_dmg[df_dmg["Name"] == name]["Total dmg"].values[0],
                           text=str(int(df_dmg[df_dmg["Name"] == name]["Average dmg per s"].values[0])),
                           showarrow=False,
                           yshift=0,
                           xshift=0,
                           xanchor="left"),
        fig.add_annotation(y=name, x=0,
                           text=" " + str(int(df_dmg[df_dmg["Name"] == name]["Times Top"].values[0]))
                                + " / " +
                                str(int(df_dmg[df_dmg["Name"] == name]["Attendance (number of fights)"].values[0])),
                           showarrow=False,
                           yshift=0,
                           xshift=0,
                           xanchor="left",
                           )
    return fig


def get_top_rips_chart(df):
    fig = px.bar(df, y="Name", x="Total rips", color="Profession", text="Total rips", barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours)
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#EEE',
        title="Top Rips",
        showlegend=False,
    )
    return fig


def get_top_stab_chart(df):
    fig = px.bar(df, y="Name", x="Total stab", color="Profession", text="Total stab", barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours)
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#EEE',
        title="Top Stability",
        showlegend=False,
    )
    return fig


def get_top_cleanses_chart(df):
    fig = px.bar(df, y="Name", x="Total cleanses", color="Profession", text="Total cleanses", barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours)
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#EEE',
        title="Top Cleanses",
        showlegend=False,
    )
    return fig


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    print("Getting content..")
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
