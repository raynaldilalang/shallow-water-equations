from dash import html
import dash_bootstrap_components as dbc
from ..components import initial_conditions


layout = html.Div([
    html.H4(['Initial Conditions']),
    initial_conditions.form,
], id="ic-layout")
