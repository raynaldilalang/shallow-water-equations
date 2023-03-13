import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import base64
import io
import pandas as pd

from ..app import app
from ..utils.characters import Delta, eta, eps


form = html.Div([
    dbc.Row([
            dbc.Col(
                dbc.FormGroup([
                    dbc.Label("Dimension", html_for="dy"),
                    dcc.Dropdown(
                        id='linearity-dropdown',
                        options=[
                            {'label': 'Linear', 'value': 'linear'},
                            {'label': 'Half-linear', 'value': 'half-linear'},
                            {'label': 'Non-linear', 'value': 'non-linear'},
                        ],
                        value='linear',
                        clearable=False
                    )
                ]), width=4,
            )
    ]),
    dbc.Row([
            dbc.Col(
                dbc.FormGroup([
                    dbc.Label(html.I(eps), html_for="eps"),
                    dbc.Input(
                        id="eps",
                        type="number",
                        max=1e-1,
                        min=0,
                        placeholder=0
                    ),
                ]), width=2,
            )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label("Friction", id="cf-label", html_for="cf-upload"),
                dcc.Upload(
                    id="cf-upload",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload frictious/ porous points"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-cf-formula",
                    options=[{'label': 'Formulate coefficient of friction', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="cf",
                ),
            ]), width=3,
        )
    ])
])


@app.callback(
    Output("cf", "style"),
    Output("cf-upload", "disabled"),
    Input("create-cf-formula", "value")
)
def show_form_cf(create_new_value):
    if len(create_new_value):
        return None, True
    else:
        return {"display": "none"}, False


@app.callback(
    Output("cf-upload", "children"),
    Input("cf-upload", "contents"),
    Input("cf-upload", "filename"),
)
def show_filename_cf(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Grey"}))
    else:
        return html.A(html.Div([
            "Upload frictious/ porous points"
        ]))