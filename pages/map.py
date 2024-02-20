# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL

# Dash extensions
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import json

from data.city.load_cities import CITIES
from view.map_params import get_markers
from view import figures

register_page(__name__, path='/map', name='Carte', title='TER', order=2,
              category='Statistique Descriptive', icon='lets-icons:map-duotone')

CITY = CITIES['Toulouse']

def layout():
    return html.Div(
        [
            viewport_map(),
            map_menus(),
            get_modal()
        ]
    )

def get_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Distribution des vélos")
            ),
            dbc.ModalBody(
                dcc.Graph(figure=None, id='bike-graph')
            )
        ],
        id="modal-graph",
        is_open=False, 
        size='xl'
    )

def map_menus():
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
                id='date_range_picker_map',
            ),
            dmc.Select(
                data=codes_names_list,
                clearable=True,
                searchable=True,
                nothingFound='Nom de station inconnue...',
                icon=DashIconify(icon='fluent:rename-16-regular'),
                id='select_map',
            )
        ],
        id='map_menus'
    )

def viewport_map():
    return dl.Map(
        [
            dl.TileLayer(),  # OpenStreetMap par défaut
        ] + get_markers(CITY),
        center=CITY.centroid,
        bounds=CITY.bounds,
        maxBounds=CITY.bounds,
        zoomControl=False,
        scrollWheelZoom=True,
        dragging=True,
        attributionControl=False,
        doubleClickZoom=False,
        zoomSnap=0.3,
        minZoom=12.4,
        id='viewport_map'
    )

@callback(
    [
        Output("modal-graph", "is_open"),
        Output("bike-graph", "figure")
    ],
    [
        Input({"type": "marker", "code_name": ALL}, "n_clicks")
    ], 
    [
        State("modal-graph", "is_open")
    ]
)
def display_graph(n_clicks, is_open):
    if not any(n_clicks):
        return no_update
    
    station_id = ctx.triggered[0]['prop_id'].split(".")[0]
    code_name = json.loads(station_id)["code_name"]
    figure = figures.bike_distrubution(CITY, code_name)

    return not is_open, figure 