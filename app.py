import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table
import plotly.express as px
import dash_daq as daq

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


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
            fig = px.bar(df, y="Name", x="Total dmg", color="Profession", text="Total dmg", barmode="relative",
                         orientation='h', height=1000,
                         color_discrete_map={
                             'Guardian': '#72C1D9',
                             'Dragonhunter': '#72C1D9',
                             'Firebrand': '#72C1D9',
                             'Revenant': '#D16E5A',
                             'Herald': '#D16E5A',
                             'Renegade': '#D16E5A',
                             'Warrior': '#FFD166',
                             'Berserker': '#FFD166',
                             'Spellbreaker': '#FFD166',
                             'Engineer': '#D09C59',
                             'Scrapper': '#D09C59',
                             'Holosmith': '#D09C59',
                             'Ranger': '#8CDC82',
                             'Druid': '#8CDC82',
                             'Soulbeast': '#8CDC82',
                             'Thief': '#C08F95',
                             'Daredevil': '#C08F95',
                             'Deadeye': '#C08F95',
                             'Elementalist': '#F68A87',
                             'Tempest': '#F68A87',
                             'Weaver': '#F68A87',
                             'Mesmer': '#B679D5',
                             'Chronomancer': '#B679D5',
                             'Mirage': '#B679D5',
                             'Necromancer': '#52A76F',
                             'Reaper': '#52A76F',
                             'Scourge': '#52A76F',
                         })
            fig.update_layout(yaxis_categoryorder='total ascending')

            for name in df["Name"]:
                fig.add_annotation(y=name, x=df[df["Name"] == name]["Total dmg"].values[0],
                                   text=str(int(df[df["Name"] == name]["Average dmg per s"].values[0])),
                                   showarrow=False,
                                   yshift=0,
                                   xshift=0,
                                   xanchor="left"),
                fig.add_annotation(y=name, x=0,
                                   text=str(int(df[df["Name"] == name]["Times Top"].values[0]))
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

        html.Hr(),  # horizontal line

        dcc.Graph(
            id='example-graph',
            figure=fig
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)
