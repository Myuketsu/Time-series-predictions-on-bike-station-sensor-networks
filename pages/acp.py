from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL
from dash.exceptions import PreventUpdate

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from data.city.load_cities import CITY
import view.figures as figures
import view.map as map


register_page(__name__, path='/acp', name='ACP', title='TER', order=4,
              category='Statistique Descriptive', icon='codicon:graph-scatter')

def layout():
    return html.Div(
        [
            map.viewport_map(CITY, 'viewport_map_acp', acp_mode=True, index=0, has_colorbar=True),
            dcc.Graph(id='acp_plot', figure=figures.acp_eigenvectors_plot(CITY, [0,1]))
        ],
        id='acp_layout'
    )