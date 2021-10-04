import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash_extensions.callback import DashCallbackBlueprint

import base64
import io
import pandas as pd
import pickle
import numpy as np
import time
import uuid
import json

from .app import app, dcb
from .layouts import upload_bottom, upload_input_wave, sensor_point
from . import Bathymetry1D, Bathymetry2D, model, save_video1D, save_video2D, g, interpolate_depth1D, interpolate_depth2D, interpolate_input_wave
from .utils.string_parser import parse_formula
from .utils.utils import parse_contents
from .utils.characters import Delta, eta

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
        upload_bottom.layout,
        html.Hr(),
        upload_input_wave.layout,
        html.Hr(),
        sensor_point.layout,
        html.Hr(),
        button_run,
        download_data_button,
        html.Div(id="info", className="mt-3"),
    ], id="page-container", style={"marginTop": "30px", "marginBottom": "30px"})
])


@app.callback(
    Output("y_min", "disabled"),
    Output("y_max", "disabled"),
    Output("dy", "disabled"),
    Output("y0", "disabled"),
    Output("d", "placeholder"),
    Output("d-label", "children"),
    Output("eta-label", "children"),
    Input("dimension-dropdown", "value"),
)
def disable_y(dimension):
    if dimension == '1D':
        return True, True, True, True, "x/10", html.I("d(x)"), html.I(eta + "(0, t)")
    if dimension == '2D':
        return False, False, False, False, "(x+y)/10", html.I("d(x, y)"), html.I(eta + "(0, y, t)")


@app.callback(
    Output("button-run", "disabled"),
    Output("store", "data"),
    Input("upload-bathymetry", "contents"),
    Input("upload-wave", "contents"),
    Input("x_min", "value"),
    Input("x_max", "value"),
    Input("y_min", "value"),
    Input("y_max", "value"),
    Input("d", "value"),
    Input("t_min", "value"),
    Input("t_max", "value"),
    Input("eta", "value"),
    Input("create-new-bathymetry", "value"),
    Input("create-new-wave", "value"),
    Input("dx", "value"),
    Input("dy", "value"),
    Input("x0", "value"),
    Input("y0", "value"),
    State("dimension-dropdown", "value"),
    State("store", "data"),
)
def disable_button(bathymetry_contents, wave_contents,
                   x_min, x_max, y_min, y_max, d_formula,
                   t_min, t_max, eta_formula,
                   create_bathymetry, create_wave,
                   dx, dy, x0, y0, dimension, store):

    disabled = False
    store_dict = json.loads(store)

    if dimension == '2D':
        if any([val is None for val in [dx, dy, x0, y0]]):
            disabled = True
        else:
            store_dict['dx'], store_dict['dy'] = dx, dy
            store_dict['x0'], store_dict['y0'] = x0, y0
    else:
        if any([val is None for val in [dx, x0]]):
            disabled = True
        else:
            store_dict['dx'] = dx
            store_dict['x0'] = x0

    if len(create_bathymetry):
        if dimension == '2D':
            if any([val is None for val in [x_min, x_max, y_min, y_max, d_formula]]):
                disabled = True
            else:
                store_dict['x_min'], store_dict['x_max'] = x_min, x_max
                store_dict['y_min'], store_dict['y_max'] = y_min, y_max
                store_dict['d'] = d_formula
        else:
            if any([val is None for val in [x_min, x_max, d_formula]]):
                disabled = True
            else:
                store_dict['x_min'], store_dict['x_max'] = x_min, x_max
                store_dict['d'] = d_formula
    else:
        if bathymetry_contents is None:
            disabled = True
        else:
            store_dict['bathymetry_contents'] = bathymetry_contents

    if len(create_wave):
        if any([val is None for val in [t_min, t_max, eta_formula]]):
            disabled = True
        else:
            store_dict['t_min'], store_dict['t_max'] = t_min, t_max
            store_dict['eta'] = eta_formula
    else:
        if wave_contents is None:
            disabled = True
        else:
            store_dict['wave_contents'] = wave_contents

    return disabled, json.dumps(store_dict)


@app.callback(
    Output("grey-area", "style"),
    Input("store-show", "data"),
    Input("store-hide", "data"),
    prevent_initial_call=True
)
def change_grey_area(_, __):
    triggered = dash.callback_context.triggered
    triggered_props = {ctx["prop_id"] for ctx in triggered}

    if 'store-show.data' in triggered_props:
        return None

    if 'store-hide.data' in triggered_props:
        return {"display": "none"}


@app.callback(
    Output("store-show", "data"),
    Input("button-run", "n_clicks"),
    prevent_initial_call=True
)
def trigger_store_show_gray(n):
    return n


@app.callback(
    Output("store-hide", "data"),
    Input("info", "children"),
    prevent_initial_call=True
)
def trigger_store_hide_gray(a):
    return a


@app.callback(
    Output("info", "children"),
    Output("store-final", "data"),
    Output("loading-output", "children"),
    Output("button-download-data", "style"),
    Output("download-video", "data"),
    Input("button-run", "n_clicks"),
    State("create-new-bathymetry", "value"),
    State("create-new-wave", "value"),
    State("dimension-dropdown", "value"),
    State("store", "data"),
    prevent_initial_call=True
)
def run_swe(_, create_bathymetry, create_wave, dimension, store):

    store_dict = json.loads(store)

    if dimension == '2D':
        dx, dy = store_dict['dx'], store_dict['dy']

        # bottom profile
        if not len(create_bathymetry):
            df_bathymetry = parse_contents(store_dict['bathymetry_contents'])
            x, y, d = interpolate_depth2D(df_bathymetry, dx=dx, dy=dy)
        else:
            x = np.arange(store_dict['x_min'], store_dict['x_max'], dx)
            y = np.arange(store_dict['y_min'], store_dict['y_max'], dy)
            X, Y = np.meshgrid(x, y)
            X, Y = X.T, Y.T
            d = parse_formula({'x': X, 'y': Y, 'pi': np.pi,
                            'Pi': np.pi}, store_dict['d'])
        bathymetry = Bathymetry2D(x, y, d)

        # wave
        H = d.max()
        c = np.sqrt(g * H)
        dt = 0.5 / (c * np.sqrt(1/dx**2 + 1/dy**2))
        if not len(create_wave):
            df_wave = parse_contents(store_dict['wave_contents'])
            t, input_wave = interpolate_input_wave(df_wave, dt)
        else:
            t = np.arange(store_dict['t_min'], store_dict['t_max'], dt)
            input_wave = parse_formula(
                {'t': t, 'pi': np.pi, 'Pi': np.pi}, store_dict['eta'])

        start = time.time()
        E, _, _ = model.swe2D(bathymetry, t, input_wave, verbose=1)
        x0, y0 = store_dict['x0'], store_dict['y0']
        i0, j0 = np.argmin(np.abs(x - x0)), np.argmin(np.abs(y - y0))
        df = pd.DataFrame({'t': t, 'eta': E[i0, j0, :]})
        temp_file = './temp/' + str(uuid.uuid1()) + '.mp4'
        save_video2D(temp_file, bathymetry, E, dt=dt, fps=1)
        end = time.time()
        return f'SWE finished in {end - start} s', df.to_json(), None, None, dcc.send_file(temp_file)
    
    if dimension == '1D':
        dx = store_dict['dx']

        # bottom profile
        if not len(create_bathymetry):
            df_bathymetry = parse_contents(store_dict['bathymetry_contents'])
            x, d = interpolate_depth1D(df_bathymetry, dx=dx)
        else:
            x = np.arange(store_dict['x_min'], store_dict['x_max'], dx)
            d = parse_formula({'x': x, 'pi': np.pi,
                            'Pi': np.pi}, store_dict['d'])
        bathymetry = Bathymetry1D(x, d)

        # wave
        H = d.max()
        c = np.sqrt(g * H)
        dt = 0.5 / (c / dx)
        if not len(create_wave):
            df_wave = parse_contents(store_dict['wave_contents'])
            t, input_wave = interpolate_input_wave(df_wave, dt)
        else:
            t = np.arange(store_dict['t_min'], store_dict['t_max'], dt)
            input_wave = parse_formula(
                {'t': t, 'pi': np.pi, 'Pi': np.pi}, store_dict['eta'])

        start = time.time()
        E, _ = model.swe1D(bathymetry, t, input_wave, verbose=1)
        x0 = store_dict['x0']
        i0 = np.argmin(np.abs(x - x0))
        df = pd.DataFrame({'t': t, 'eta': E[i0, :]})
        temp_file = './temp/' + str(uuid.uuid1()) + '.mp4'
        save_video1D(temp_file, bathymetry, E, dt=dt, fps=1)
        end = time.time()
        return f'SWE finished in {end - start} s', df.to_json(), None, None, dcc.send_file(temp_file)


@app.callback(
    Output("download-data", "data"),
    Input("button-download-data", "n_clicks"),
    State("store-final", "data"),
    prevent_initial_call=True,
)
def download_data(_, store):
    df = pd.read_json(store)
    return dcc.send_data_frame(df.to_csv, "eta.csv")


dcb.register(app)
