from dash import dcc, dash
from dash import html
from dash.dependencies import Input, Output
from flask_login import current_user, logout_user

from app import app
from apps import top_stats, details, login

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='redirect', refresh=True),
    dcc.Store(id='login-status', storage_type='session'),
    html.Div(id='user-status-div'),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Output('redirect', 'pathname'),
              Input('url', 'pathname'))
def display_page(pathname):
    view = None
    url = dash.no_update
    if pathname == '/login':
        view = login.login
    elif pathname == '/success':
        if current_user.is_authenticated:
            view = login.success
        else:
            view = login.failed
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            view = login.logout
        else:
            view = login
            url = '/login'

    elif pathname == '/':
        view = top_stats.layout
    elif pathname == '/details':
        if current_user.is_authenticated:
            view = details.layout
        else:
            view = 'Redirecting to login...'
            url = '/login'
    else:
        view = top_stats.layout
    # You could also return a 404 "URL not found" page here
    print('....display_page....')
    print(view)
    print(url)
    return view, url


if __name__ == '__main__':
    app.run_server(debug=True)
