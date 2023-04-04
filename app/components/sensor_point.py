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
        # dbc.Col(
        #     dbc.FormGroup([
        #         dbc.Label(html.I(["x", html.Sub("0")]), html_for="x0"),
        #         dbc.Input(
        #             id="x0",
        #             type="number"
        #         ),
        #     ]), width=2,
        # ),
        # dbc.Col(
        #     dbc.FormGroup([
        #         dbc.Label(html.I(["y", html.Sub("0")]), html_for="y0"),
        #         dbc.Input(
        #             id="y0",
        #             type="number"
        #         ),
        #     ]), width=2,
        # ),
        dbc.Col(
            dbc.FormGroup([
                # dbc.Label("Sensor Point", id="sensor-label", html_for="sensor-upload"),
                dcc.Upload(
                    id="sensor-upload",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload sensor points"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
            ]), width=3,
        )
    ], form=True),
], id="form-sensor")


@app.callback(
    Output("sensor-upload", "children"),
    Input("sensor-upload", "contents"),
    Input("sensor-upload", "filename"),
)
def show_filename_sensor(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Red"}))
    else:
        return html.A(html.Div([
            "Upload sensor points"
        ]))