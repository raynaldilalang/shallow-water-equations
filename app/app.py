import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

# from . import index

import os
import argparse


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)
app.title = "Shallow Water Equations"
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])
server = app.server
from . import index

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action='store_true',
                    default=False, help="Run in debug mode")
parser.add_argument("--reload", action='store_true',
                    default=False, help="Run with reload")


HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))

if __name__ == "__main__":
    args = parser.parse_args()
    if 'temp' not in os.listdir():
        os.mkdir('temp')
    app.run_server(host=HOST, port=PORT, debug=args.debug, use_reloader=args.reload)
