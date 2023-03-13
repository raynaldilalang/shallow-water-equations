from dash import html
import dash_bootstrap_components as dbc
from ..components import equation_type


layout = html.Div([
    html.H4(['Equation Type']),
    equation_type.form,
], id="equation-type-layout")
