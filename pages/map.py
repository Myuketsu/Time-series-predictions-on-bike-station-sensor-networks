from dash import html, register_page, Input, Output, State, no_update, callback, ctx, dcc
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from data.city.load_cities import CITIES
from view.map_params import get_markers, get_bounds

register_page(__name__, path='/map', name='Carte', title='TER', order=2,
              category='Statistique Descriptive', icon='lets-icons:map-duotone')

def layout():
    return html.Div(
        [
            viewport_map(index=0)
        ]
    )

def viewport_map(index: int):
    return dl.Map(
        [
            dl.TileLayer(), # (open-street-map)
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
        id='viewport_map'
    )