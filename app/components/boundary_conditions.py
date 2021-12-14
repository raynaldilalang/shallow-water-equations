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


precision = dbc.Row([
    dbc.Col(
        dbc.FormGroup([
            dbc.Label(html.I(Delta + "t"), html_for="dt"),
            dbc.Input(
                id="dt",
                type="number"
            ),
            dcc.Checklist(
                id="dt-auto",
                options=[{'label': "Auto", 'value': "auto"}],
                value=[]
            )
        ]), width=2,
    ),
], form=True,)

form = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["t", html.Sub("min")]), html_for="t-min"),
                dbc.Input(
                    id="t-min",
                    type="number"
                ),
            ]), width=2,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["t", html.Sub("max")]), html_for="t-max"),
                dbc.Input(
                    id="t-max",
                    type="number"
                ),
            ]), width=2,
        ),
    ], form=True),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[
                        {'label': eta + u"(x\u2098\u2097\u2099, y, t)", 'value': 'eta'},
                        {'label': u"u(x\u2098\u2097\u2099, y, t)", 'value': 'u'},
                    ],
                    value='u',
                    id="left-radio",
                    inline=True,
                ),
                dbc.Input(
                    id="left-input",
                ),
                dcc.Upload(
                    dbc.Button("Upload", id="left-upload", color="light"),
                    id="left-upload-input",
                    multiple=False,
                    accept=".csv"
                )
            ]), width=4,
        ),
    ], form=True),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[
                        {'label': eta + u"(x\u2098\u2090\u2093, y, t)", 'value': 'eta'},
                        {'label': u"u(x\u2098\u2090\u2093, y, t)", 'value': 'u'},
                    ],
                    value='u',
                    id="right-radio",
                    inline=True,
                ),
                dbc.Input(
                    id="right-input",
                ),
                dcc.Upload(
                    dbc.Button("Upload", id="right-upload", color="light"),
                    id="right-upload-input",
                    multiple=False,
                    accept=".csv"
                )
            ]), width=4,
        )
    ], form=True),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[
                        {'label': eta + u"(x, y\u2098\u2097\u2099, t)", 'value': 'eta'},
                        {'label': u"u(x, y\u2098\u2097\u2099, t)", 'value': 'u'},
                    ],
                    value='u',
                    id="top-radio",
                    inline=True,
                ),
                dbc.Input(
                    id="top-input",
                ),
                dcc.Upload(
                    dbc.Button("Upload", id="top-upload", color="light"),
                    id="top-upload-input",
                    multiple=False,
                    accept=".csv"
                )
            ]), width=4,
        )
    ], form=True),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[
                        {'label': eta + u"(x, y\u2098\u2090\u2093, t)", 'value': 'eta'},
                        {'label': u"u(x, y\u2098\u2090\u2093, t)", 'value': 'u'},
                    ],
                    value='u',
                    id="bottom-radio",
                    inline=True,
                ),
                dbc.Input(
                    id="bottom-input",
                ),
                dcc.Upload(
                    dbc.Button("Upload", id="bottom-upload", color="light"),
                    id="bottom-upload-input",
                    multiple=False,
                    accept=".csv"
                )
            ]), width=4,
        )
    ], form=True),
], id="form-bc",)


@app.callback(
    Output("dt", "disabled"),
    Input("dt-auto", "value")
)
def disable_dt_field(auto):
    return len(auto) > 0