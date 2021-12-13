import base64
import datetime
import io

from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app
import pandas as pd

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
    html.Div(id='details-output-data-upload'),
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

            df_pie = df[['Profession', 'Total dmg']].groupby('Profession').sum().reset_index()
            print(df_pie)
            pie_chart_average = px.pie(df_pie,
                                       values='Total dmg',
                                       names='Profession',
                                       color='Profession',
                                       color_discrete_map=profession_colours,
                                       title='Total dmg%')
            df_pie_average = df[['Profession', 'Total dmg']].groupby('Profession').mean().reset_index()
            pie_chart = px.pie(df_pie_average,
                               values='Total dmg',
                               names='Profession',
                               color='Profession',
                               color_discrete_map=profession_colours,
                               title='Average dmg%')

            pie_chart.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#EEE'
            )
            pie_chart_average.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#EEE'
            )

            for index, row in df.iterrows():
                df.at[index, 'Name'] = "{:<25}".format(row['Name']) + get_short_profession(row['Profession']) + " "
            fig = px.bar(df, y="Name", x="Total dmg", color="Profession", text="Total dmg", barmode="relative",
                         orientation='h', height=1000,
                         color_discrete_map=profession_colours)
            fig.update_layout(
                yaxis_categoryorder='total ascending',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#EEE'
            )
            # adds the labels for dmg/s and times top/attendance
            for name in df["Name"]:
                fig.add_annotation(y=name, x=df[df["Name"] == name]["Total dmg"].values[0],
                                   text=str(int(df[df["Name"] == name]["Average dmg per s"].values[0])),
                                   showarrow=False,
                                   yshift=0,
                                   xshift=0,
                                   xanchor="left"),
                fig.add_annotation(y=name, x=0,
                                   text=" " + str(int(df[df["Name"] == name]["Times Top"].values[0]))
                                        + " / " +
                                        str(int(df[df["Name"] == name]["Attendance (number of fights)"].values[0])),
                                   showarrow=False,
                                   yshift=0,
                                   xshift=0,
                                   xanchor="left",
                                   ),
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),
        dash_table.DataTable(
            data=df_pie.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df_pie.columns]
        ),

        html.Hr(),

        dcc.Graph(
            id='example-graph',
            figure=fig
        ),
        html.Div([
            dcc.Graph(
                id='pie-chart',
                figure=pie_chart,
            ),
            dcc.Graph(
                id='pie-chart-average',
                figure=pie_chart_average,

            ),
        ]),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('details-output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
