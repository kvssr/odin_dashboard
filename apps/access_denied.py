from dash import html
import dash_bootstrap_components as dbc


def layout():
    layout = dbc.Container([
        dbc.Row(
            dbc.Col(
                html.H1('Access Denied', className='mx-auto text-warning')
            )
        )
    ])
    return layout
