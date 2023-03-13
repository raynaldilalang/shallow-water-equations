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
                dcc.Upload(
                    id="eta-initial-upload-button",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload initial water level"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-eta-initial-formula",
                    options=[{'label': 'Formulate initial water level', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="eta-initial",
                ),
            ]), width=3,
        ),
        dbc.Col(width=1),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["u(x, y, t", html.Sub("min"), ")"]), id="u-initial-label", html_for="u-initial"),
                dcc.Upload(
                    id="u-initial-upload-button",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload initial x-directional velocity"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-u-initial-formula",
                    options=[{'label': 'Formulate initial x-directional velocity', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="u-initial",
                ),
            ]), width=3,
        ),
        dbc.Col(width=1),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label(html.I(["v(x, y, t", html.Sub("min"), ")"]), id="v-initial-label", html_for="v-initial"),
                dcc.Upload(
                    id="v-initial-upload-button",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload initial y-directional velocity"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-v-initial-formula",
                    options=[{'label': 'Formulate initial y-directional velocity', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="v-initial",
                ),
            ]), width=3
        ),
    ], form=True),
], id="form-ic",)


@app.callback(
    Output("eta-initial", "style"),
    Output("eta-initial-upload-button", "disabled"),
    Input("create-eta-initial-formula", "value")
)
def show_form_eta(create_new_value):
    if len(create_new_value):
        return None, True
    else:
        return {"display": "none"}, False

@app.callback(
    Output("u-initial", "style"),
    Output("u-initial-upload-button", "disabled"),
    Input("create-u-initial-formula", "value")
)
def show_form_u(create_new_value):
    if len(create_new_value):
        return None, True
    else:
        return {"display": "none"}, False


@app.callback(
    Output("v-initial", "style"),
    Output("v-initial-upload-button", "disabled"),
    Input("create-v-initial-formula", "value"),
    Input("dimension-dropdown", "value")
)
def show_form_v(create_new_value, dimension):

    if dimension == "1D" or len(create_new_value):
        upload_disabled = True
    else:
        upload_disabled = False
    
    if len(create_new_value):
        formula_style = None
    else:
        formula_style = {"display": "none"}

    return formula_style, upload_disabled


@app.callback(
    Output("eta-initial-upload-button", "children"),
    Input("eta-initial-upload-button", "contents"),
    Input("eta-initial-upload-button", "filename"),
)
def show_filename_eta(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Blue"}))
    else:
        return html.A(html.Div([
            "Upload initial water level"
        ]))


@app.callback(
    Output("u-initial-upload-button", "children"),
    Input("u-initial-upload-button", "contents"),
    Input("u-initial-upload-button", "filename"),
)
def show_filename_u(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Blue"}))
    else:
        return html.A(html.Div([
            "Upload initial x-directional velocity"
        ]))


@app.callback(
    Output("v-initial-upload-button", "children"),
    Input("v-initial-upload-button", "contents"),
    Input("v-initial-upload-button", "filename"),
)
def show_filename_v(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Blue"}))
    else:
        return html.A(html.Div([
            "Upload initial y-directional velocity"
        ]))