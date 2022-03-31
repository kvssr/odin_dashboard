import json
import dash_bootstrap_components as dbc
import pandas as pd
from app import app
from dash import html, dcc, Output, Input, State, MATCH, ALL
import base64
import requests

from helpers import db_writer_json
from dash.exceptions import PreventUpdate

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
    dbc.Row(id='logs-button-row', children=[
        dbc.Col(dbc.Button(id='btn-parse-logs', children='Parse Logs'), width={'size': 2, 'offset': 3}),
        dbc.Col(dbc.Button(id='btn-download-log', children='Download Logs', disabled=True), width={'size': 2}),
        dbc.Col(dbc.Button(id='btn-save-db-log', children='Save to db', disabled=True), width={'size': 2}),
        dcc.Download(id='log-download-json'),
        dcc.Loading(dcc.Store(id='log-store'), color='grey')
    ]),
        dbc.Row(id='logs-button-row-2', children=[
        dbc.Col(id='log-output'),
        dcc.Interval(id='logs-interval', interval=1000, n_intervals=0, disabled=True),
        dcc.Store(id='task-id-store'),
        dcc.Store(id='task-status-store'),
    ]),
    dbc.Row(id='logs_summary-row', children=[
        dbc.Col(dcc.Loading(id='logs-summary-col', color='grey'))
    ]),
    dbc.Row(children=[
        dbc.Col(id='logs-table-container', children=[
            dbc.Row(dcc.Loading(dbc.Col(id='save-log-msg', children=[]), color='grey')),
            dbc.Row(dbc.Row(id='logs-table-header', children=[
                dbc.Col('Filename', class_name='logs-table-col-header', width={'size': 4, 'offset': 1}),
                dbc.Col('Size', class_name='logs-table-col-header', width={'size': 1}),
                dbc.Col([
                    'Link', 
                    dcc.Clipboard(id='clp-links',
                            style={
                                'margin-left': '10px'
                            })
                    ], class_name='logs-table-col-header', width={'size': 5}, style={'display': 'flex'}),
            ])),
            dbc.Row(id='logs-table', children=[]),
            dbc.Row(id='parse-msg', children=[]),
        ]),
    ]),
])


@app.callback(
    Output('log-output', 'children'),
    Input('task-status-store', 'data'),
    prevent_initial_call=True
)
def show_task_status(data):
    data = json.loads(data)
    if data:
        return f'Status: {data["status"]} || {data["current"]}/{data["total"]}'


@app.callback(
    Output('task-status-store', 'data'),
    Input('logs-interval', 'n_intervals'),
    State('task-id-store', 'data'),
    prevent_initial_call=True
)
def get_task_status(n, task_url):
    request = requests.get(task_url)
    return json.dumps(request.json())


@app.callback(
    Output('logs-interval', 'disabled'),
    Input('btn-parse-logs', 'n_clicks'),
    Input('task-status-store', 'data'),
    prevent_initial_call=True
)
def toggle_interval(n, data):
    if data == None:
        return False
    output = json.loads(data)
    print(output)
    if 'result' in output:
        return True


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
        filenames.sort()
        table = []

        counter = 0
        for filename, content in zip(filenames, contents):  
            content = content.split(',')[1]
            old_bytes = content.encode('utf-8')
            content_bytes = base64.b64decode(old_bytes)
            size = len(content_bytes)/(1024*1024)   

            row = dbc.Row([
                dbc.Col(id={'type': 'filename-col', 'index': counter}, children=filename, class_name='logs-table-cell', width={'size': 4, 'offset': 1}),
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
    Output('task-id-store', 'data'),
    Input('btn-parse-logs', 'n_clicks'),
    State({'type': 'link-col', 'index': ALL}, 'children'),
    prevent_initial_call=True
)
def parse_logs(n, rows):
    print(rows)
    url = 'http://cards2d.ddns.net:5321/json'
    #url = 'http://127.0.0.1:5000/json'
    links = []
    for row in rows:
        link = row['props']['children'].split('/')[-1]
        links.append({'href': f'https://dps.report/getJson?permalink={link}'})


    data = {'links': links}
    print(data)

    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
    
    print(r.json())
    print(r.headers['Location'])
    return r.headers['Location']



@app.callback(
    Output('clp-links', 'content'),
    Input('clp-links', 'n_clicks'),
    State({'type': 'link-col', 'index': ALL}, 'children'),
    prevent_initial_call=True
)
def copy_links_to_clipboard(n, links):
    result = ''
    for link in links:
        result += f'{link["props"]["href"]} \n'
    return result


@app.callback(
    Output('log-download-json', 'data'),
    Input('btn-download-log', 'n_clicks'),
    State('task-status-store', 'data'),
    prevent_initial_call=True
)
def download_log_as_json(n, data):
    data = json.loads(data)['result']
    return dict(content=json.dumps(data, indent=4), filename=f'raid_log_{data["overall_raid_stats"]["date"]}_{data["overall_raid_stats"]["start_time"]}.json')


@app.callback(
    Output('logs-summary-col', 'children'),
    Output('btn-download-log', 'disabled'),
    Output('btn-save-db-log', 'disabled'),
    Input('task-status-store', 'data'),
    prevent_initial_call=True    
)
def show_logs_summary(data):
    data = json.loads(data)
    if 'result' in data:
        data = data['result']
        df = pd.DataFrame(data['overall_raid_stats'], index=[0])
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, class_name='tableFixHead table table-striped table-bordered table-hover'), False, False
    raise PreventUpdate


@app.callback(
    Output('save-log-msg', 'children'),
    Input('btn-save-db-log', 'n_clicks'),
    State('task-status-store', 'data'),
    prevent_initial_call=True 
)
def save_logs_to_db(n, data):
    try:
        data = json.loads(data)['result']
        db_writer_json.write_xls_to_db(data)
    except Exception as e:
        print(e)  
    return 'Added to the database!'
