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
from view.map import viewport_map, get_markers
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
            dbc.ModalHeader(dbc.ModalTitle('Distribution des vélos')),
            dbc.ModalBody(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                dcc.Graph(figure=figures.create_empty_graph(), id='bike-graph'),
                                label="Graphique Linéaire",
                                tab_id="tab-line-chart",
                            ),
                            dbc.Tab(
                                dcc.Graph(figure=figures.create_empty_graph(), id='box-plot'),
                                label="Box Plot",
                                tab_id="tab-box-plot",
                            ),
                        ],
                        id="tabs",
                        active_tab="tab-line-chart",
                    )
                ]
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
        Output('bike-graph', 'figure'),
        Output('box-plot', 'figure'),
        Output('select_map_statistics', 'value'),
        Output('viewport_map_statistics', 'children'),
    ],
    [
        Input({'type': 'marker', 'code_name': ALL}, 'n_clicks'),
        Input('date_range_picker_map_statistics', 'value'),
        Input('select_map_statistics', 'value'),
        Input('modal-graph', 'is_open')
    ]
)
def display_graph(marker_clicks, date_range, select_value, is_open_modal):
    open_modal = no_update
    updated_figure_line = no_update
    updated_figure_box = no_update
    updated_select_value = no_update 
    map_children = no_update

    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else ''
    triggered_value = ctx.triggered[0]['value'] if ctx.triggered else ''

    if triggered_id == '':
        return open_modal, updated_figure_line, updated_figure_box, updated_select_value, map_children

    print(triggered_id, triggered_value)

    if ('marker' in triggered_id and triggered_value) or ('select_map_statistics' in triggered_id and triggered_value):
        station_id = json.loads(triggered_id.split('.')[0])['code_name'] if 'marker' in triggered_id else select_value
        open_modal = True
        updated_select_value = station_id
        updated_figure_line = figures.bike_distrubution(CITY, station_id, date_range)
        updated_figure_box = figures.bike_boxplot(CITY, station_id, date_range)
        map_children = viewport_map(CITY, 'viewport_map_statistics', highlight=station_id)

    if 'modal-graph' in triggered_id and not is_open_modal:
        map_children = viewport_map(CITY, 'viewport_map_statistics')

    return open_modal, updated_figure_line, updated_figure_box, updated_select_value, map_children
