# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import json

from data.city.load_cities import CITY
from view.map import viewport_map
from view import figures

register_page(__name__, path='/statistique_map', name='Statistique', title='TER', order=2,
              category='Statistique Descriptive', icon='lets-icons:map-duotone')

def layout():
    return html.Div(
        [
            viewport_map(CITY, 'viewport_map_statistics'),
            menus_map(),
            get_modal()
        ]
    )

def get_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle('Distribution des vélos')
            ),
            dbc.ModalBody(
                dcc.Graph(figure=figures.create_empty_graph(), id='bike-graph')
            )
        ],
        id='modal-graph',
        is_open=False, 
        size='xl'
    )

def menus_map():
    codes_names_list = CITY.df_coordinates['code_name'].to_list()
    date_range = [CITY.df_hours['date'].min().date(), CITY.df_hours['date'].max().date()]
    return html.Div(
        [
            dmc.DateRangePicker(
                minDate=date_range[0],
                maxDate=date_range[1],
                value=date_range,
                allowSingleDateInRange=True,
                clearable=False,
                transition='fade',
                id='date_range_picker_map_statistics',
            ),
            dmc.Select(
                data=codes_names_list,
                clearable=True,
                searchable=True,
                nothingFound='Nom de station inconnue...',
                icon=DashIconify(icon='fluent:rename-16-regular'),
                id='select_map_statistics',
            )
        ],
        id='menus_map_statistics'
    )

@callback(
    [
        Output('modal-graph', 'is_open'),
        Output('bike-graph', 'figure')
    ],
    [
        Input({'type': 'marker', 'code_name': ALL}, 'n_clicks')
    ]
)
def display_graph(n_clicks):
    if n_clicks is None or not any(n_clicks):
        return no_update, no_update
    
    station_id = ctx.triggered[0]['prop_id'].split('.')[0]
    code_name = json.loads(station_id)['code_name']
    figure = figures.bike_distrubution(CITY, code_name)

    return True, figure