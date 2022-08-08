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
                dbc.Label(html.I([eta + "(x, y, t", html.Sub("min"), ")"]), id="eta-initial-label", html_for="eta-initial"),
                dbc.Input(
                    id="eta-initial",
                ),
            ]), width=4,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["u(x, y, t", html.Sub("min"), ")"]), id="u-initial-label", html_for="u-initial"),
                dbc.Input(
                    id="u-initial",
                ),
            ]), width=4,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["v(x, y, t", html.Sub("min"), ")"]), id="v-initial-label", html_for="v-initial"),
                dbc.Input(
                    id="v-initial",
                ),
            ]), width=4,
        ),
    ], form=True),
], id="form-ic",)

