import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import base64
import io
import pandas as pd

from ..app import app
from ..utils.characters import Delta, eta


form = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["x", html.Sub("0")]), html_for="x0"),
                dbc.Input(
                    id="x0",
                    type="number"
                ),
            ]), width=2,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["y", html.Sub("0")]), html_for="y0"),
                dbc.Input(
                    id="y0",
                    type="number"
                ),
            ]), width=2,
        ),
    ], form=True),
], id="form-sensor")