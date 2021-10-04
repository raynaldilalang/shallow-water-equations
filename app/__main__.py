from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from dash_extensions.callback import DashCallbackBlueprint

from .app import app
from . import index

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action='store_true',
                    default=False, help="Run in debug mode")
parser.add_argument("--reload", action='store_true',
                    default=False, help="Run with reload")


HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])


@app.callback(Output("page-content", "children"),
              Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/":
        return index.layout
    else:
        return "404"

if __name__ == "__main__":
    args = parser.parse_args()
    app.run_server(host=HOST, port=PORT, debug=args.debug, use_reloader=args.reload)
