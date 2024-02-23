# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL, MATCH

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
            dcc.Store(id='markers_colors', data=[[], list(range(len(CITY.df_coordinates)))]),
            map.viewport_map(CITY, 'viewport_map_correlation', 'Red'),
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
        Output('correlation_graph', 'figure'),
        Output('transferlist_correlation', 'value'),
        Output({'type': 'marker', 'code_name': ALL, 'index': ALL}, 'icon'),
        Output('markers_colors', 'data')
    ],
    [
        Input('select_correlation', 'value'),
        Input('transferlist_correlation', 'value'),
        Input({'type': 'marker', 'code_name': ALL, 'index': ALL}, 'n_clicks')
    ],
    [
        State('markers_colors', 'data')
    ]
)
def correlation_plot_update(in_select, in_transferlist, in_n_clicks, state_last_transferlist):
    triggeredId = ctx.triggered_id

    corr_graph = no_update
    transferlist_value = in_transferlist
    markers_icons = [no_update] * len(CITY.df_coordinates)
    last_transferlist = no_update
    
    if isinstance(triggeredId, dict) and triggeredId['type'] == 'marker':
        transferlist_value = update_transferlist(transferlist_value, triggeredId['code_name'])

    markers_icons = update_markers(markers_icons, transferlist_value, state_last_transferlist)
    last_transferlist = [[v['index'] for v in side] for side in transferlist_value]

    selected_columns = [station['value'] for station in transferlist_value[1]]
    corr_graph = update_graph(selected_columns, in_select)

    return corr_graph, transferlist_value, markers_icons, last_transferlist

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

def update_markers(markers: list, transferlist_value: list[list[dict]], last_transferlist: list[list[int]]):
    for index, icon in enumerate([map.ICONS['Blue'], map.ICONS['Red']]):
        for station in transferlist_value[index]:
            if not station['index'] in last_transferlist[index]:
                markers[station['index']] = icon
    return markers