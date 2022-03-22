import json
from typing import final
import dash_bootstrap_components as dbc
from flask import request
from app import app
from dash import html, dcc, Output, Input, State, MATCH, ALL
import base64
import requests

from helpers import db_writer_json

layout = dbc.Row([
    dbc.Row(dbc.Col(id='json-header', children=[html.H1("Add logs")], width={'size': 12}), style={'text-align': 'center'}),
    dbc.Row(dbc.Col(id='logs-upload-col', children=(
        dcc.Upload(
            id='upload-logs', 
            children=('Upload files'), 
            className='upload-data',
            multiple=True
        )
        ))),
    dbc.Row(dbc.Row(id='logs-table-header', children=[
        dbc.Col('Filename', class_name='logs-table-col-header', width={'size': 3}),
        dbc.Col('Size', class_name='logs-table-col-header', width={'size': 1}),
        dbc.Col('Link', class_name='logs-table-col-header', width={'size': 5}),
        dbc.Col(dbc.Button(id='btn-parse-logs', children='Parse Logs'), width={'size': 3})
    ])),
    dbc.Row(id='logs-table', children=[]),
    dbc.Row(id='parse-msg', children=[]),
])


@app.callback(
    Output('logs-table', 'children'),
    Input('upload-logs', 'filename'),
    State('upload-logs', 'contents'),
    prevent_initial_call=True
)
def show_logs_in_table(filenames, contents):
    if filenames:
        extension = filenames[0].split('.')[-1]
        if extension not in ['zevtc', 'evtc']:
            print('No .zevtc file')
            return

        table = []

        counter = 0
        for filename, content in zip(filenames, contents):  
            content = content.split(',')[1]
            old_bytes = content.encode('utf-8')
            content_bytes = base64.b64decode(old_bytes)
            size = len(content_bytes)/(1024*1024)   

            row = dbc.Row([
                dbc.Col(id={'type': 'filename-col', 'index': counter}, children=filename, class_name='logs-table-cell', width={'size': 3}),
                dbc.Col(id={'type': 'size-col', 'index': counter}, children=[f'{size:.2f} MB'], class_name='logs-table-cell', width={'size': 1}),
                dbc.Col(dcc.Loading(html.Div(id={'type': 'link-col', 'index': counter}, children=['']), color='grey'), class_name='logs-table-cell', width={'size': 5}),
            ], class_name='logs-table-row')
            counter += 1
            table.append(row)
        return table
    pass


@app.callback(
    Output({'type': 'link-col', 'index': MATCH}, 'children'),
    Input({'type': 'filename-col', 'index': MATCH}, 'children'),
    State({'type': 'filename-col', 'index': MATCH}, 'id'),
    State('upload-logs', 'contents')
)
def upload_to_dps_report(filename, id, contents):
    index = id['index']
    url='https://dps.report/uploadContent?json=1&generator=ei&detailedwvw=true'
    print(index)
    print(f'Filename {index}: {filename}')
    print(f'Content {index}: {contents[index][0:100]}')

    content = contents[index].split(',')[1]
    old_bytes = content.encode('utf-8')
    content_bytes = base64.b64decode(old_bytes)

    files = {
        'file': (filename, content_bytes, 'application/octet-stream'),
        'Content-Disposition': f'form-data; name="file"; filename={filename}',
        'Content-Type': 'application/octet-stream'
    }
    
    print('Making request..')
    request = requests.post(url, files=files)
    print(request.status_code)
    if request.status_code == 200:
        print('Request success!')
        link = request.json()['permalink']
        return html.A(href=link,children=link)
    else:
        return ''


@app.callback(
    Output('parse-msg', 'children'),
    Input('btn-parse-logs', 'n_clicks'),
    State({'type': 'link-col', 'index': ALL}, 'children'),
    prevent_initial_call=True
)
def parse_logs(n, rows):
    print(rows)
    url = 'http://192.168.2.12:5678/json'
    links = []
    for row in rows:
        link = row['props']['children'].split('/')[-1]
        links.append({'href': f'https://dps.report/getJson?permalink={link}'})


    data = {'links': links}

    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
    
    print(r.json())

    try:
        db_writer_json.write_xls_to_db(r.json())
    except Exception as e:
        print(e)
    
    return 'Added to the database!'