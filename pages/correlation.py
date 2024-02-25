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
            map.viewport_map(CITY, 'viewport_map_correlation', 'red'),
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
            get_correlation_plot()
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
    return dmc.LoadingOverlay(
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
        Input({'type': 'marker', 'code_name': ALL, 'index': ALL}, 'n_clicks')
    ]
)
def correlation_plot_update(in_select, in_transferlist, in_n_clicks):
    triggeredId = ctx.triggered_id

    transferlist_value = in_transferlist
    map_children = no_update
    corr_graph = no_update
    
    if isinstance(triggeredId, dict) and triggeredId['type'] == 'marker':
        transferlist_value = update_transferlist(transferlist_value, triggeredId['code_name'])

    map_children = update_map_markers(transferlist_value)

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

def update_map_markers(transferlist_value: list[list[dict]]):
    distribution = {station['index']: 'red' for station in transferlist_value[1]}
    return map.get_map_children(CITY, distribution, 'blue')