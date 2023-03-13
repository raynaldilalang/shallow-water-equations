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

from .app import app
from .layouts import initial_conditions, boundary_conditions, upload_bathymetry, equation_type, sensor_point
from . import Bathymetry1D, Bathymetry2D, model, save_video1D, save_video2D, g, interpolate_depth1D, interpolate_depth2D, interpolate_input_wave
from .utils.string_parser import parse_formula
from .utils.utils import parse_contents
from .utils.characters import Delta, eta
from .home import layout as home_layout
from .main_app import layout as main_app_layout

server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])


@app.callback(Output("page-content", "children"),
              Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/":
        return home_layout
    elif pathname == "/home":
        return home_layout
    elif pathname == "/main_app":
        return main_app_layout
    else:
        return "404"

@app.callback(
    Output("interval-dummy-store", "data"),
    Input("interval-cleaning", "n_intervals"),
)
def clean_temp_data(_):
    for temp_file in os.listdir('./temp'):
        if time.time() - os.path.getmtime('./temp/' + temp_file) > 3600:
            os.remove('./temp/' + temp_file)
    return ""

@app.callback(
    Output("y-min", "disabled"),
    Output("y-max", "disabled"),
    Output("dy", "disabled"),
    Output("v-initial", "disabled"),
    Output("y0", "disabled"),
    Output("left-input", "disabled"),
    Output("right-input", "disabled"),
    Output("top-input", "disabled"),
    Output("bottom-input", "disabled"),
    Output("left-upload-input", "disabled"),
    Output("right-upload-input", "disabled"),
    Output("top-upload-input", "disabled"),
    Output("bottom-upload-input", "disabled"),
    Output("d", "placeholder"),
    Output("d-label", "children"),
    Output("eta-initial-label", "children"),
    Output("u-initial-label", "children"),
    Output("left-radio", "options"),
    Output("right-radio", "options"),
    Output("top-radio", "options"),
    Output("bottom-radio", "options"),
    Input("dimension-dropdown", "value"),
    Input("create-left-bc-formula", "value"),
    Input("create-right-bc-formula", "value"),
    Input("create-top-bc-formula", "value"),
    Input("create-bottom-bc-formula", "value"),
    Input("left-input-absorbing", "value"),
    Input("right-input-absorbing", "value"),
    Input("top-input-absorbing", "value"),
    Input("bottom-input-absorbing", "value"),
)
def disable_bc(dimension, left_formula, right_formula, top_formula, bottom_formula,
               left_absorb, right_absorb, top_absorb, bottom_absorb):
    left_formula, right_formula, top_formula, bottom_formula = len(left_formula)>0, len(right_formula)>0, len(top_formula)>0, len(bottom_formula)>0
    left_absorb, right_absorb, top_absorb, bottom_absorb = len(left_absorb)>0, len(right_absorb)>0, len(top_absorb)>0, len(bottom_absorb)>0

    if dimension == '1D':
        top_disabled, bottom_disabled = True, True
        return (
            True, True, True, True, True,
            left_absorb, right_absorb, True, True,
            left_formula or left_absorb, right_formula or right_absorb, True, True,
            "x/10", html.I("d(x)"),
            html.I([eta + "(x, t", html.Sub("min"), ")"]), html.I(["u(x, t", html.Sub("min"), ")"]),
            [{'label': eta + u"(x\u2098\u2097\u2099, t)", 'value': 'eta'}, {'label': u"u(x\u2098\u2097\u2099, t)", 'value': 'u'}],
            [{'label': eta + u"(x\u2098\u2090\u2093, t)", 'value': 'eta'}, {'label': u"u(x\u2098\u2090\u2093, t)", 'value': 'u'}],
            [{'label': eta + u"(x, y\u2098\u2097\u2099, t)", 'value': 'eta', 'disabled': True}, {'label': u"v(x, y\u2098\u2097\u2099, t)", 'value': 'v', 'disabled': True}],
            [{'label': eta + u"(x, y\u2098\u2090\u2093, t)", 'value': 'eta', 'disabled': True}, {'label': u"v(x, y\u2098\u2090\u2093, t)", 'value': 'v', 'disabled': True}],
        )
    if dimension == '2D':
        return (
            False, False, False, False, False,
            left_absorb, right_absorb, top_absorb, bottom_absorb,
            left_formula or left_absorb, right_formula or right_absorb, top_formula or top_absorb, bottom_formula or bottom_absorb,
            "(x+y)/10", html.I("d(x, y)"),
            html.I([eta + "(x, y, t", html.Sub("min"), ")"]), html.I(["u(x, y, t", html.Sub("min"), ")"]),
            [{'label': eta + u"(x\u2098\u2097\u2099, y, t)", 'value': 'eta'}, {'label': u"u(x\u2098\u2097\u2099, y, t)", 'value': 'u'}],
            [{'label': eta + u"(x\u2098\u2090\u2093, y, t)", 'value': 'eta'}, {'label': u"u(x\u2098\u2090\u2093, y, t)", 'value': 'u'}],
            [{'label': eta + u"(x, y\u2098\u2097\u2099, t)", 'value': 'eta'}, {'label': u"v(x, y\u2098\u2097\u2099, t)", 'value': 'v'}],
            [{'label': eta + u"(x, y\u2098\u2090\u2093, t)", 'value': 'eta'}, {'label': u"v(x, y\u2098\u2090\u2093, t)", 'value': 'v'}],
        )


@app.callback(
    Output("button-run", "disabled"),
    Output("store", "data"),
    Input("upload-bathymetry", "contents"),
    Input("left-upload-input", "contents"),
    Input("right-upload-input", "contents"),
    Input("top-upload-input", "contents"),
    Input("bottom-upload-input", "contents"),
    Input("left-input", "value"),
    Input("right-input", "value"),
    Input("top-input", "value"),
    Input("bottom-input", "value"),
    Input("x-min", "value"),
    Input("x-max", "value"),
    Input("y-min", "value"),
    Input("y-max", "value"),
    Input("d", "value"),
    Input("t-min", "value"),
    Input("t-max", "value"),
    Input("dt", "value"),
    Input("create-bathymetry-formula", "value"),
    Input("dx", "value"),
    Input("dy", "value"),
    Input("x0", "value"),
    Input("y0", "value"),
    State("dimension-dropdown", "value"),
    State("store", "data"),
)
def disable_button(bathymetry_contents,
                   left_contents, right_contents, top_contents, bottom_contents,
                   left_formula, right_formula, top_formula, bottom_formula,
                   x_min, x_max, y_min, y_max, d_formula,
                   t_min, t_max, dt,
                   create_bathymetry,
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

    left_filled = left_formula or left_contents
    right_filled = right_formula or right_contents
    top_filled = top_formula or top_contents
    bottom_filled = bottom_formula or bottom_contents

    store_dict['t_min'], store_dict['t_max'] = t_min, t_max
    store_dict['dt'] = dt

    store_dict['left_formula'] = left_formula
    store_dict['right_formula'] = right_formula
    store_dict['top_formula'] = top_formula
    store_dict['bottom_formula'] = bottom_formula

    store_dict['left_contents'] = left_contents
    store_dict['right_contents'] = right_contents
    store_dict['top_contents'] = top_contents
    store_dict['bottom_contents'] = bottom_contents

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
    State("create-bathymetry-formula", "value"),
    State("dimension-dropdown", "value"),
    State("eta-initial", "value"),
    State("u-initial", "value"),
    State("v-initial", "value"),
    State("dt-auto", "value"),
    State("left-radio", "value"),
    State("right-radio", "value"),
    State("top-radio", "value"),
    State("bottom-radio", "value"),
    State("linearity-dropdown", "value"),
    State("eps", "value"),
    State("store", "data"),
    prevent_initial_call=True
)
def run_swe(_, create_bathymetry, dimension, eta_initial, u_initial, v_initial,
            dt_auto, left_bc, right_bc, top_bc, bottom_bc,
            linearity, eps, store):

    try:
        store_dict = json.loads(store)

        if dimension == '2D':
            dx, dy = store_dict['dx'], store_dict['dy']

            # bottom profile
            if not len(create_bathymetry):
                df_bathymetry = parse_contents(store_dict['bathymetry_contents'])
                x, y, d = interpolate_depth2D(df_bathymetry, dx=dx, dy=dy)
            else:
                x = np.arange(store_dict['x_min'], store_dict['x_max'] + dx/2, dx)
                y = np.arange(store_dict['y_min'], store_dict['y_max'] + dy/2, dy)
                X, Y = np.meshgrid(x, y)
                X, Y = X.T, Y.T
                d = parse_formula({'x': X, 'y': Y, 'pi': np.pi,
                                'Pi': np.pi}, store_dict['d'])
                if not isinstance(d, np.ndarray):
                    d = d * np.ones(X.shape)
            bathymetry = Bathymetry2D(x, y, d)

            # initial conditions
            eta_initial = parse_formula({'x': bathymetry.X, 'y': bathymetry.Y, 'pi': np.pi,
                                    'Pi': np.pi}, eta_initial)
            u_initial = parse_formula({'x': bathymetry.X, 'y': bathymetry.Y, 'pi': np.pi,
                                    'Pi': np.pi}, u_initial)
            v_initial = parse_formula({'x': bathymetry.X, 'y': bathymetry.Y, 'pi': np.pi,
                                    'Pi': np.pi}, v_initial)
            ic = {'eta': eta_initial, 'u': u_initial, 'v': v_initial}

            # boundary conditions
            H = (d+eta_initial).max()
            c = np.sqrt(g * H)
            if len(dt_auto):
                dt = 0.5 / (c * np.sqrt(1/dx**2 + 1/dy**2))
            else:
                dt = store_dict['dt']
            bc = {}
            for bound in ['left', 'right', 'top', 'bottom']:
                if store_dict[bound + '_contents']:
                    bc[bound] = parse_contents(store_dict[bound + '_contents'])
                    t, bc[bound] = interpolate_input_wave(bc[bound], dt, store_dict['t_min'], store_dict['t_max'])
                else:
                    t = np.arange(store_dict['t_min'], store_dict['t_max'], dt)
                    bc[bound] = parse_formula({'t': t, 'pi': np.pi,
                                            'Pi': np.pi}, store_dict[bound + '_formula'])
            
            i0 = 1 if left_bc == 'eta' else 0
            i1 = x.shape[0] - 1 if right_bc == 'eta' else x.shape[0]
            j0 = 1 if top_bc == 'eta' else 0
            j1 = y.shape[0] - 1 if bottom_bc == 'eta' else y.shape[0]

            start = time.time()
            E, _, _ = model.swe2D(bathymetry, t, ic, bc, i0, i1, j0, j1, linearity=linearity, eps=eps, verbose=1)
            x0, y0 = store_dict['x0'], store_dict['y0']
            x0_idx, y0_idx = np.argmin(np.abs(x - x0)), np.argmin(np.abs(y - y0))
            df = pd.DataFrame({'t': t, 'eta': E[x0_idx, y0_idx, :]})
            temp_file = './temp/' + str(uuid.uuid1()) + '.mp4'
            save_video2D(temp_file, bathymetry, E, dt=dt, fps=4)
            end = time.time()
            return f'SWE finished in {end - start} s', df.to_json(), None, None, dcc.send_file(temp_file)
        
        if dimension == '1D':
            dx = store_dict['dx']

            # bottom profile
            if not len(create_bathymetry):
                df_bathymetry = parse_contents(store_dict['bathymetry_contents'])
                x, d = interpolate_depth1D(df_bathymetry, dx=dx)
            else:
                x = np.arange(store_dict['x_min'], store_dict['x_max'] + dx/2, dx)
                d = parse_formula({'x': x, 'pi': np.pi,
                                'Pi': np.pi}, store_dict['d'])
                if not isinstance(d, np.ndarray):
                    d = d * np.ones(x.shape)

            bathymetry = Bathymetry1D(x, d)
            
            # initial conditions
            eta_initial = parse_formula({'x': x, 'pi': np.pi,
                                    'Pi': np.pi}, eta_initial)
            u_initial = parse_formula({'x': x, 'pi': np.pi,
                                    'Pi': np.pi}, u_initial)
            ic = {'eta': eta_initial, 'u': u_initial}

            # boundary conditions
            H = (d+eta_initial).max()
            c = np.sqrt(g * H)
            if len(dt_auto):
                dt = 0.5 / (c / dx)
            else:
                dt = store_dict['dt']
            
            bc = {}
            for bound in ['left', 'right']:
                if store_dict[bound + '_contents']:
                    bc[bound] = parse_contents(store_dict[bound + '_contents'])
                    t, bc[bound] = interpolate_input_wave(bc[bound], dt)
                else:
                    t = np.arange(store_dict['t_min'], store_dict['t_max'], dt)
                    print(store_dict[bound + '_formula'])
                    bc[bound] = parse_formula({'t': t, 'pi': np.pi,
                                            'Pi': np.pi}, store_dict[bound + '_formula'])
            
            i0 = 1 if left_bc == 'eta' else 0
            i1 = x.shape[0] - 1 if right_bc == 'eta' else x.shape[0]

            start = time.time()
            E, _ = model.swe1D(bathymetry, t, ic, bc, i0, i1, linearity=linearity, eps=eps, verbose=1)
            x0 = store_dict['x0']
            x0_idx = np.argmin(np.abs(x - x0))
            df = pd.DataFrame({'t': t, 'eta': E[x0_idx, :]})
            temp_file = './temp/' + str(uuid.uuid1()) + '.mp4'
            save_video1D(temp_file, bathymetry, E, dt=dt, fps=12)
            store_dict['temp_file'] = temp_file
            end = time.time()
            return (f'SWE finished in {end - start} s',
                df.to_json(), None, None, dcc.send_file(temp_file))
    
    except Exception as e:
        print(e)
        time.sleep(10)
        return (
            dbc.Alert(
                'Something went wrong when processing your request. Please check your configurations and try refreshing this page.',
                color='danger',
            ), "", None, {"display": "none"}, None
        )


@app.callback(
    Output("download-data", "data"),
    Input("button-download-data", "n_clicks"),
    State("store-final", "data"),
    prevent_initial_call=True,
)
def download_data(_, store):
    df = pd.read_json(store)
    return dcc.send_data_frame(df.to_csv, "eta.csv")


# dcb.register(app)
