from dash import html
import dash_bootstrap_components as dbc
from ..components import upload_bottom


layout = html.Div([
    html.H4(['Bathymetry']),
    upload_bottom.input_bathymetry,
    upload_bottom.precision,
    upload_bottom.create_new,
    upload_bottom.form,
], id="bottom")
