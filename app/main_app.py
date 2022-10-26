import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import os
import base64
import io
import pandas as pd
import pickle
import numpy as np
import time
import uuid
import json

from swe import bottom

from .app import app
# from .app import dcb
from .layouts import initial_conditions, boundary_conditions, upload_bathymetry, sensor_point
from . import Bathymetry1D, Bathymetry2D, model, save_video1D, save_video2D, g, interpolate_depth1D, interpolate_depth2D, interpolate_input_wave
from .utils.string_parser import parse_formula
from .utils.utils import parse_contents
from .utils.characters import Delta, eta

server = app.server

navbar = dbc.NavbarSimple(
    children=[],
    brand="Shallow Water Equations",
    brand_href="#",
    color="dark",
    dark=True,
)
download_data_button = html.Div([
    dbc.Button("Download Data", color="info",
               id="button-download-data", style={"display": "none"}),
    dcc.Download(id="download-data")
])
button_run = html.Div([
    dcc.Checklist(
        id="non-linear-checklist",
        options=[{'label': 'Use non-linear equations', 'value': 1}],
        value=[]
    ),
    dbc.Button("Run", id="button-run", color="primary",
               className="mr-1 mb-3 float-right", disabled=True),
    dcc.Download(id="download-video")
])

layout = html.Div([
    navbar,
    dbc.Container(dbc.Row(
        dcc.Loading(
            id="loading",
            type="circle",
            children=html.Div(id="loading-output"),
        ), justify="center", align="center", className="h-50"
    ), className="loading-container"),
    dbc.Container([
        dcc.Store(data='{}', id="store"),
        dcc.Store(id="store-show"),
        dcc.Store(id="store-hide"),
        dcc.Store(id="store-final"),
        html.Div(id="grey-area", className="grey-area", style={"display": "none"}),
        upload_bathymetry.layout,
        html.Hr(),
        initial_conditions.layout,
        html.Hr(),
        boundary_conditions.layout,
        html.Hr(),
        sensor_point.layout,
        html.Hr(),
        download_data_button,
        html.Div(id="info", className="mt-3"),
        button_run,
        dcc.Store(id="interval-dummy-store"),
        dcc.Interval(id="interval-cleaning", interval=6e+3)
    ], id="page-container", style={"marginTop": "30px", "marginBottom": "30px"})
])