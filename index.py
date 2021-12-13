from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from apps import top_stats, details

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return top_stats.layout
    if pathname == '/details':
        return details.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
