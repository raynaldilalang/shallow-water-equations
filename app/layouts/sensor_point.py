from dash import html
import dash_bootstrap_components as dbc
from ..components import sensor_point


layout = html.Div([
    html.H4(['Sensor Point']),
    sensor_point.form,
], id="sensor-point")
