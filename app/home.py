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

server = app.server

navbar = dbc.NavbarSimple(
    children=[],
    brand="Shallow Water Equations",
    brand_href="/",
    color="dark",
    dark=True,
)

layout = html.Div([
    navbar,
    dbc.Container(
        [
            html.H1("Shallow Water Equations App", className="display-3"),
            html.P(
                "Easily compute your shallow water simulations using this application.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.A("How do I use the app?", href="https://docs.google.com/document/d/1Qa7-yTlSSJiiIxOvZ9a6pWv5d-zs8ZZrxmmzYkMw7pk/edit?usp=sharing", target="_blank"),
            html.P(
                dbc.Button("Start", href="/main_app", color="primary"), className="lead"
            ),
        ],
        style={"marginTop": "30px", "marginBottom": "30px"}
    ),
])