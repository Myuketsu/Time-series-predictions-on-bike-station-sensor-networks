from dash import html, register_page

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

register_page(__name__, path='/acp', name='ACP', title='TER', order=4,
              category='Statistique Descriptive', icon='codicon:graph-scatter')

def layout():
    return html.Div(
        [
            get_tabs()
        ],
        id='acp_layout'
    )

def get_tabs():
    return dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.Tab('Gallery', value='gallery'),
                    dmc.Tab('Messages', value='messages'),
                    dmc.Tab('Settings', value='settings'),
                ],
                position='center'
            ),
            dmc.TabsPanel('Gallery tab content', value='gallery'),
            dmc.TabsPanel('Messages tab content', value='messages'),
            dmc.TabsPanel('Settings tab content', value='settings'),
        ],
        id='acp_tabs'
    )