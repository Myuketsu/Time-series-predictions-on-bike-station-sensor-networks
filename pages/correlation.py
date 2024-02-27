# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from data.city.load_cities import CITY
import data.data as data
import view.figures as figures
import view.map as map

register_page(__name__, path='/correlation', name='Correlation', title='TER', order=3,
              category='Statistique Descriptive', icon='arcticons:cpustats')

def layout():
    return html.Div(
        [
            map.viewport_map(CITY, 'viewport_map_correlation', True, 'red'),
            select_and_plot()
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