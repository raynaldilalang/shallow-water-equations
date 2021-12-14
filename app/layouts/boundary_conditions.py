from dash import html
import dash_bootstrap_components as dbc
from ..components import boundary_conditions


layout = html.Div([
    html.H4(['Boundary Conditions']),
    # boundary_conditions.input_wave_uploader,
    boundary_conditions.precision,
    # boundary_conditions.create_new,
    boundary_conditions.form,
], id="bc-layout")
