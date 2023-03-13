from dash import html, dcc
import dash_bootstrap_components as dbc
from ..components import initial_conditions


layout = html.Div([
    html.H4(['Initial Conditions']),
    initial_conditions.form,
    html.P([
        html.I('You can use most standard mathematical functions in the formula that is available in this '),
        dcc.Link(html.I('numpy API.'), href='https://numpy.org/doc/stable/reference/routines.math.html')
    ], style={"font-size": "small"}),
    html.P(html.I('To create dam-break initial conditions, utilize the sign function.'), style={"font-size": "small"})
], id="ic-layout")
