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
            get_tabs(),
            dcc.Graph(id='acp_plot', figure=figures.acp_eigenvectors_plot(CITY, [0,1])),
            map.viewport_map(CITY, 'viewport_map_acp', acp_mode=True, index=0)
        ],
        id='acp_layout'
    )

def get_tabs():
    return dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.Tab('Vecteur propres', value='vp'),
                    dmc.Tab('Cartes coefficient', value='map'),
                    dmc.Tab('Settings', value='settings'),
                ],
                position='center'
            ),
            dmc.TabsPanel('Gallery tab content', value='vp'),
            dmc.TabsPanel('Messages tab content', value='map'),
            dmc.TabsPanel('Settings tab content', value='settings'),
        ],
        id='acp_tabs'
    )