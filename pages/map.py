from dash import html, register_page, Input, Output, State, no_update, callback, ctx, dcc
import dash_leaflet as dl
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime, date

from data.city.load_cities import CITIES
from view.map_params import get_markers

register_page(__name__, path='/map', name='Carte', title='TER', order=2,
              category='Statistique Descriptive', icon='lets-icons:map-duotone')

def layout():
    index_city = 1
    return html.Div(
        [
            viewport_map(index=index_city),
            map_menus(index=index_city)
        ]
    )

def map_menus(index: int):
    codes_names_list = CITIES[index].df_coordinates['code_name'].to_list()
    date_range = [CITIES[index].df_hours['date'].min().date(), CITIES[index].df_hours['date'].max().date()]
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

def viewport_map(index: int):
    return dl.Map(
        [
            dl.TileLayer(), # (open-street-map)
        ] + get_markers(CITIES[index]),
        center=CITIES[index].centroid,
        bounds=CITIES[index].bounds,
        maxBounds=CITIES[index].bounds,
        zoomControl=False,
        scrollWheelZoom=True,
        dragging=True,
        attributionControl=False,
        doubleClickZoom=False,
        zoomSnap=0.3,
        minZoom=12.4,
        id='viewport_map'
    )