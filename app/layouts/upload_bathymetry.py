from dash import html
import dash_bootstrap_components as dbc
from ..components import upload_bathymetry


layout = html.Div([
    html.H4(['Bathymetry']),
    upload_bathymetry.input_bathymetry,
    upload_bathymetry.precision,
    upload_bathymetry.create_new,
    upload_bathymetry.form,
], id="bottom-layout")
