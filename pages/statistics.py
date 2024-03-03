# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

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
        
    ],
    [
        Input({'type': 'marker', 'code_name': ALL, 'index': ALL}, 'n_clicks'),
        Input('date_range_picker_map_statistics', 'value'),
        Input('select_map_statistics', 'value')
    ],
    prevent_initial_call=True
)
def display_graph(n_clicks, date_range, selected_station):
    triggeredId = ctx.triggered_id

    modal_state = no_update
    line_plot = no_update
    box_plot = no_update
    station_value = no_update
    
    if (isinstance(triggeredId, dict) and triggeredId['type'] == 'marker') or (triggeredId == 'select_map_statistics'):
        station_id = triggeredId['code_name'] if isinstance(triggeredId, dict) else selected_station
        line_plot = figures.bike_distrubution(CITY, station_id, date_range)
        box_plot = figures.bike_boxplot(CITY, station_id, date_range)
        modal_state = True
        station_value = station_id
    
    return modal_state, line_plot, box_plot, station_value
