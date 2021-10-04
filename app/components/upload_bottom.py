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


input_bathymetry = dcc.Upload(
    id="upload-bathymetry",
    className="uploader",
    children=html.A(html.Div([
        "Upload bathymetry"
    ])),
    multiple=False,
    accept=".csv"
)

create_new = dcc.Checklist(
    id="create-new-bathymetry",
    options=[{'label': 'Create new bathymetry', 'value': 1}],
    value=[]
)

precision = dbc.Row([
    dbc.Col(
        dbc.FormGroup([
            dbc.Label("Dimension", html_for="dy"),
            dcc.Dropdown(
                id='dimension-dropdown',
                options=[
                    {'label': '1D', 'value': '1D'},
                    {'label': '2D', 'value': '2D'},
                ],
                value='2D',
                clearable=False
            )
        ]), width=2,
    ),
    dbc.Col(
        dbc.FormGroup([
            dbc.Label(html.I(Delta + "x"), html_for="dx"),
            dbc.Input(
                id="dx",
                type="number"
            ),
        ]), width=2,
    ),
    dbc.Col(
        dbc.FormGroup([
            dbc.Label(html.I(Delta + "y"), html_for="dy"),
            dbc.Input(
                id="dy",
                type="number"
            ),
        ]), width=2,
    ),
], form=True)

form = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["x", html.Sub("min")]), html_for="x_min"),
                dbc.Input(
                    id="x_min",
                    type="number"
                ),
            ]), width=2,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["x", html.Sub("max")]), html_for="x_max"),
                dbc.Input(
                    id="x_max",
                    type="number"
                ),
            ]), width=2,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["y", html.Sub("min")]), html_for="y_min"),
                dbc.Input(
                    id="y_min",
                    type="number"
                ),
            ]), width=2,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["y", html.Sub("max")]), html_for="y_max"),
                dbc.Input(
                    id="y_max",
                    type="number"
                ),
            ]), width=2,
        ),
    ], form=True),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I("d(x, y)"), id="d-label", html_for="d"),
                dbc.Input(
                    id="d",
                    placeholder="(x+y)/10",
                ),
            ]), width=8,
        ),
    ], form=True)
], id="form-bathymetry", style={"display": "none"})


@app.callback(
    Output("form-bathymetry", "style"),
    Output("upload-bathymetry", "disabled"),
    Input("create-new-bathymetry", "value")
)
def show_form(create_new_value):
    if len(create_new_value):
        return None, True
    else:
        return {"display": "none"}, False


@app.callback(
    Output("upload-bathymetry", "children"),
    Input("upload-bathymetry", "contents"),
    Input("upload-bathymetry", "filename"),
)
def show_filename(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Orange"}))
    else:
        return html.A(html.Div([
            "Upload bathymetry"
        ]))
