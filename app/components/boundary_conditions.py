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
                # dcc.Upload(
                #     dbc.Button("Upload", id="left-upload", color="light"),
                #     id="left-upload-input",
                #     multiple=False,
                #     accept=".csv"
                # ),
                dcc.Upload(
                    id="left-upload-input",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload left boundary condition"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-left-bc-formula",
                    options=[{'label': 'Formulate left boundary condition', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="left-input",
                ),
                dcc.Checklist(
                    id="left-input-absorbing",
                    options=[{'label': 'Absorbing', 'value': 1}],
                    value=[]
                ),
            ]), width=4,
        ),
        dbc.Col(width=1),
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
                # dcc.Upload(
                #     dbc.Button("Upload", id="right-upload", color="light"),
                #     id="right-upload-input",
                #     multiple=False,
                #     accept=".csv"
                # ),
                dcc.Upload(
                    id="right-upload-input",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload right boundary condition"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-right-bc-formula",
                    options=[{'label': 'Formulate right boundary condition', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="right-input",
                ),
                dcc.Checklist(
                    id="right-input-absorbing",
                    options=[{'label': 'Absorbing', 'value': 1}],
                    value=[]
                ),
            ]), width=4,
        )
    ], form=True),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[
                        {'label': eta + u"(x, y\u2098\u2097\u2099, t)", 'value': 'eta'},
                        {'label': u"v(x, y\u2098\u2097\u2099, t)", 'value': 'v'},
                    ],
                    value='v',
                    id="top-radio",
                    inline=True,
                ),
                # dcc.Upload(
                #     dbc.Button("Upload", id="top-upload", color="light"),
                #     id="top-upload-input",
                #     multiple=False,
                #     accept=".csv"
                # ),
                dcc.Upload(
                    id="top-upload-input",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload top boundary condition"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-top-bc-formula",
                    options=[{'label': 'Formulate top boundary condition', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="top-input",
                ),
                dcc.Checklist(
                    id="top-input-absorbing",
                    options=[{'label': 'Absorbing', 'value': 1}],
                    value=[]
                ),
            ]), width=4,
        ),
        dbc.Col(width=1),
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[
                        {'label': eta + u"(x, y\u2098\u2090\u2093, t)", 'value': 'eta'},
                        {'label': u"v(x, y\u2098\u2090\u2093, t)", 'value': 'v'},
                    ],
                    value='v',
                    id="bottom-radio",
                    inline=True,
                ),
                # dcc.Upload(
                #     dbc.Button("Upload", id="bottom-upload", color="light"),
                #     id="bottom-upload-input",
                #     multiple=False,
                #     accept=".csv"
                # ),
                dcc.Upload(
                    id="bottom-upload-input",
                    className="uploader-mini",
                    children=html.A(html.Div([
                        "Upload bottom boundary condition"
                    ])),
                    multiple=False,
                    accept=".csv"
                ),
                dcc.Checklist(
                    id="create-bottom-bc-formula",
                    options=[{'label': 'Formulate bottom boundary condition', 'value': 1}],
                    value=[]
                ),
                dbc.Input(
                    id="bottom-input",
                ),
                dcc.Checklist(
                    id="bottom-input-absorbing",
                    options=[{'label': 'Absorbing', 'value': 1}],
                    value=[]
                ),
            ]), width=4,
        ),
    ], form=True),
], id="form-bc",)


@app.callback(
    Output("dt", "disabled"),
    Input("dt-auto", "value")
)
def disable_dt_field(auto):
    return len(auto) > 0


@app.callback(
    Output("left-input", "style"),
    Input("create-left-bc-formula", "value")
)
def show_form_left(create_new_value):
    if len(create_new_value):
        return None
    else:
        return {"display": "none"}


@app.callback(
    Output("right-input", "style"),
    Input("create-right-bc-formula", "value")
)
def show_form_right(create_new_value):
    if len(create_new_value):
        return None
    else:
        return {"display": "none"}


@app.callback(
    Output("top-input", "style"),
    Input("create-top-bc-formula", "value")
)
def show_form_top(create_new_value):
    if len(create_new_value):
        return None
    else:
        return {"display": "none"}


@app.callback(
    Output("bottom-input", "style"),
    Input("create-bottom-bc-formula", "value")
)
def show_form_bottom(create_new_value):
    if len(create_new_value):
        return None
    else:
        return {"display": "none"}


@app.callback(
    Output("left-upload-input", "children"),
    Input("left-upload-input", "contents"),
    Input("left-upload-input", "filename"),
)
def show_filename_left(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Blue"}))
    else:
        return html.A(html.Div([
            "Upload left boundary condition"
        ]))


@app.callback(
    Output("right-upload-input", "children"),
    Input("right-upload-input", "contents"),
    Input("right-upload-input", "filename"),
)
def show_filename_bottom(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Blue"}))
    else:
        return html.A(html.Div([
            "Upload right boundary condition"
        ]))


@app.callback(
    Output("top-upload-input", "children"),
    Input("top-upload-input", "contents"),
    Input("top-upload-input", "filename"),
)
def show_filename_top(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Blue"}))
    else:
        return html.A(html.Div([
            "Upload top boundary condition"
        ]))


@app.callback(
    Output("bottom-upload-input", "children"),
    Input("bottom-upload-input", "contents"),
    Input("bottom-upload-input", "filename"),
)
def show_filename_bottom(contents, filename):
    if contents:
        return html.A(html.Div([
            html.I(filename)
        ], style={"color": "Blue"}))
    else:
        return html.A(html.Div([
            "Upload bottom boundary condition"
        ]))