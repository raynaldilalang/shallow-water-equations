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


input_wave = dcc.Upload(
    id="upload-wave",
    className="uploader",
    children=html.A(html.Div([
        "Upload input wave"
    ])),
    multiple=False,
    accept=".csv"
)

create_new = dcc.Checklist(
    id="create-new-wave",
    options=[{'label': 'Create a wave function', 'value': 1}],
    value=[]
)

precision = dbc.Row([
    dbc.Col(
        dbc.FormGroup([
            dbc.Label(html.I(Delta + "t"), html_for="dt"),
            dbc.Input(
                id="dt",
                type="number"
            ),
        ]), width=2,
    ),
], form=True, style={"display": "none"})

form = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["t", html.Sub("min")]), html_for="t_min"),
                dbc.Input(
                    id="t_min",
                    type="number"
                ),
            ]), width=2,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["t", html.Sub("max")]), html_for="t_max"),
                dbc.Input(
                    id="t_max",
                    type="number"
                ),
            ]), width=2,
        ),
    ], form=True),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(eta + "(0, y, t)"), id="eta-label", html_for="eta"),
                dbc.Input(
                    id="eta",
                    placeholder="0.5*sin(t/30)",
                ),
            ]), width=8,
        ),
    ], form=True)
], id="form-wave", style={"display": "none"})


@app.callback(
    Output("form-wave", "style"),
    Output("upload-wave", "disabled"),
    Input("create-new-wave", "value")
)
def show_form(create_new_value):
    if len(create_new_value):
        return None, True
    else:
        return {"display": "none"}, False


@app.callback(
    Output("upload-wave", "children"),
    Input("upload-wave", "contents"),
    Input("upload-wave", "filename"),
)
def show_filename(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "DodgerBlue"}))
    else:
        return html.A(html.Div([
            "Upload input wave"
        ]))