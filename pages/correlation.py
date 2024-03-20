# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL

import json

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from data.city.load_cities import CITY
from data.data import calculate_correlations
import data.data as data
import view.figures as figures
import view.map as map

register_page(__name__, path='/correlation', name='Correlation', title='TER', order=3,
              category='Statistique Descriptive', icon='arcticons:cpustats')

selected_station_store = dcc.Store(id='selected_station_store', data={'selected_station': '00001-poids-de-lhuile'})

def layout():
    switch = dmc.Switch(
        id='mode_switch',
        checked=False, 
        style={'position': 'absolute', 'top': 90, 'left': 10, 'zIndex': 1000}
    )
    
    content_container = html.Div(id='content_container')

    return html.Div(
        [
            switch,
            content_container, 
            selected_station_store,
            dcc.Store(id='correlation_data_store', data={})
        ],
        id='correlation_layout'
    )


def select_and_plot():
    initial_values_codes_names = [[], [
        {'value': row['code_name'], 'label': row['code_name'], 'index': index}
        for index, row in CITY.df_coordinates.iterrows()]]
    return html.Div(
        [
            dmc.TransferList(
                value=initial_values_codes_names,
                searchPlaceholder=['Rechercher une station à ajouter...', 'Rechercher une station à enlever...'],
                nothingFound=['Impossible de trouver la station à ajouter', 'Impossible de trouver la station à enlever'],
                placeholder=['Il n\'y a plus de station à ajouter', 'Il n\'y a plus de station à enlever'],
                listHeight=200,
                id='transferlist_correlation'
            ),
            dmc.Divider(label='CORRÉLATION DES STATIONS SÉLECTIONNÉES', labelPosition='center', id='divider_correlation'),
            get_select_sort(),
            get_correlation_plot(),
            dbc.Popover(
                is_open=False,
                target='correlation_plot',
                trigger='hover',
                id='correlation_hover',
                className='d-none'
            )
        ],
        id='select_and_plot_correlation'
    )

def get_select_sort():
    return html.Div(
        [
            html.Span('Type de tri', id='title_select_correlation'),
            dmc.Select(
                data=[
                    {'value': False, 'label': 'Alphabétique'},
                    {'value': True, 'label': 'Regroupement'}
                ],
                value=False,
                id='select_correlation'
            )
        ],
        id='select_container_correlation'
    )

def get_correlation_plot():
    return html.Div(
        [
            dcc.Graph(
                figure=figures.correlation_plot(
                    data.get_correlation_on_selected_stations(
                        city=CITY,
                        columns=CITY.df_coordinates['code_name'].to_list()
                    )
                ),
                id='correlation_graph'
            )
        ],
        id='correlation_plot'
    )

@callback(
    [
        Output('transferlist_correlation', 'value'),
        Output('viewport_map_correlation', 'children'),
        Output('correlation_graph', 'figure')
    ],
    [
        Input('select_correlation', 'value'),
        Input('transferlist_correlation', 'value'),
        Input('edit_control', 'geojson'),
        Input({'type': 'marker', 'code_name': ALL, 'index': ALL}, 'n_clicks'),
        Input('correlation_graph', 'hoverData')
    ],
    [
        State('correlation_hover', 'is_open')
    ]
)
def correlation_plot_update(in_select, in_transferlist, in_geojson, in_n_clicks, in_hover_data, state_is_hover):
    triggeredId = ctx.triggered_id

    transferlist_value = in_transferlist
    map_children = no_update
    corr_graph = no_update
    
    if triggeredId == 'edit_control':
        transferlist_value = switch_station_transferlist(in_geojson, transferlist_value)

    if isinstance(triggeredId, dict) and triggeredId['type'] == 'marker':
        transferlist_value = update_transferlist(transferlist_value, triggeredId['code_name'])

    hover_data = None
    if state_is_hover and in_hover_data is not None:
        hover_data = in_hover_data['points'][0]

    map_children = update_map_markers(hover_data, transferlist_value)

    if triggeredId != 'correlation_graph':
        corr_graph = update_graph(
            selected_columns=[station['value'] for station in transferlist_value[1]],
            in_select=in_select
        )

    return transferlist_value, map_children, corr_graph

def update_graph(selected_columns: list, in_select: bool):
    if len(selected_columns) < 2:
        return figures.create_empty_graph(
            'Nombre insuffisant de stations sélectionnées...')
    
    return figures.correlation_plot(
        data.get_correlation_on_selected_stations(
            city=CITY,
            columns=selected_columns,
            ordered=in_select
        )
    )

def update_transferlist(transferlist_value: list[list[dict]], station: str):
    for in_current_list_index, values in enumerate(transferlist_value):
        for index in range(len(values)):
            if station == values[index]['value']:
                transferlist_value[not in_current_list_index].append(values[index])
                del values[index]
                return transferlist_value
    raise ValueError('The station isn\'t on either list, it has to be!')

def update_map_markers(hover_data: dict | None, transferlist_value: list[list[dict]]):
    distribution = {station['index']: 'red' for station in transferlist_value[1]}
    if hover_data is not None:
        for station in ['x', 'y']:
            distribution[CITY.df_coordinates[CITY.df_coordinates['code_name'].str.contains(hover_data[station])].index[0]] = 'gold'
    return map.get_map_children(CITY, distribution, True, 'blue')

def switch_station_transferlist(geojson, transferlist_value: list[list[dict]]):
    if not geojson['features']:
        return transferlist_value
    
    station_to_switch = data.check_if_station_in_polygon(CITY, geojson)
    for station in station_to_switch:
        transferlist_value = update_transferlist(transferlist_value, station)
    return transferlist_value


@callback(
    Output('content_container', 'children'),
    Input('mode_switch', 'checked'),
    State('selected_station_store', 'data')
)
def toggle_mode(checked, data):
    if checked:
        selected_station = data.get('selected_station')
        return html.Div(
            [
                map.viewport_map(
                    CITY, 'viewport_on_map_correlation', 
                    circle_mode=bool(selected_station),  # Active circle_mode si une station est sélectionnée
                    selected_station=selected_station
                ),
            ],
            id='correlation_on_map'
        )
    else:
        # Retournez le contenu actuel de la page pour le mode par défaut
        return html.Div(
            [
                map.viewport_map(CITY, 'viewport_map_correlation', True, 'red'),
                select_and_plot()
            ],
            id='correlation_layout'
        )


@callback(
    Output('selected_station_store', 'data'),
    [Input({'type': 'circle_marker', 'code_name': ALL, 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def on_marker_click(n_clicks):
    if not ctx.triggered:
        return no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_station = json.loads(button_id)['code_name']

    return {'selected_station': selected_station}

@callback(
    Output('correlation_data_store', 'data'),
    [Input('selected_station_store', 'data')]
)
def update_correlation_data(selected_station_data):
    selected_station = selected_station_data['selected_station']
    correlations = calculate_correlations(CITY, selected_station)
    return correlations 

@callback(
    Output('viewport_on_map_correlation', 'children'),  
    [Input('correlation_data_store', 'data'), Input('selected_station_store', 'data')]
)
def update_markers(correlation_data, station_data):
    selected_station = station_data['selected_station']
    return map.get_map_children(CITY, circle_mode=True ,selected_station=selected_station)

