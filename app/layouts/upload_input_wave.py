from dash import html
import dash_bootstrap_components as dbc
from ..components import upload_input_wave


layout = html.Div([
    html.H4(['Input Wave']),
    upload_input_wave.input_wave,
    upload_input_wave.precision,
    upload_input_wave.create_new,
    upload_input_wave.form,
], id="bottom")
