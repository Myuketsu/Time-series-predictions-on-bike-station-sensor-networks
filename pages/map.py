from dash import html, register_page, Input, Output, State, no_update, callback, ctx, dcc, callback_context, ALL
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_mantine_components as dmc
import json
from dash_iconify import DashIconify

from data.city.load_cities import CITIES
from view.map_params import get_markers, get_bounds
from view import figures

register_page(__name__, path='/map', name='Carte', title='TER', order=2,
              category='Statistique Descriptive', icon='lets-icons:map-duotone')

modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Distribution des vélos")),
        dbc.ModalBody(dcc.Graph(figure=figures.bike_distrubution("00037-ste-lucie"),id='bike-graph')),
    ],
    id="modal-graph",
    is_open=False, 
    size='xl'
)


def layout():
    return html.Div(
        [
            modal,
            viewport_map(1),
        ]
    )

def viewport_map(index: int):
    return dl.Map(
        [
            dl.TileLayer(),  # OpenStreetMap par défaut
        ] + get_markers(CITIES[index]),
        center=CITIES[index].centroid,
        bounds=get_bounds(CITIES[index]),
        maxBounds=get_bounds(CITIES[index]),
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
    [Output("modal-graph", "is_open"), Output("bike-graph", "figure")],
    [Input({"type": "marker", "index": ALL}, "n_clicks")], 
    [State("modal-graph", "is_open")],
)
def display_graph(n_clicks, is_open):
    if not any(n_clicks):
        return no_update
    else:
        ctx = callback_context
        station_id = ctx.triggered[0]['prop_id'].split(".")[0]
        station_id = json.loads(station_id)["index"]
        figure = figures.bike_distrubution(station_id)
        return not is_open, figure 