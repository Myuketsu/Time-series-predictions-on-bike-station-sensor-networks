# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update, ALL
from dash.exceptions import PreventUpdate

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from data.city.load_cities import CITY
import data.data as data
import view.figures as figures
import view.map_factory as map_factory

import json

register_page(__name__, path='/correlation', name='Correlation', title='TER', order=3,
              category='Statistique Descriptive', icon='arcticons:cpustats')

def layout():
    switch = dmc.Switch(
        id='mode_switch',
        offLabel=DashIconify(icon="charm:chart-line", width=20),
        onLabel=DashIconify(icon="charm:circle", width=20),
        checked=False, 
        style={'position': 'absolute', 'top': 90, 'left': 10, 'zIndex': 1000},
        size='lg'
    )

    return html.Div(
        [
            switch,
            html.Div(id='content_container'), 
            dcc.Store(id='selected_station_store', data={'selected_station': '00001-poids-de-lhuile'}),
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
        Output('viewport_map_correlation', 'key'),
        Output('viewport_map_correlation', 'children'),
        Output('correlation_graph', 'figure')
    ],
    [
        Input('select_correlation', 'value'),
        Input('transferlist_correlation', 'value'),
        Input('edit_control', 'geojson'),
        Input({'type': 'circle_marker', 'code_name': ALL, 'index': ALL}, 'n_clicks'),
        Input('correlation_graph', 'hoverData')
    ],
    [
        State('viewport_map_correlation', 'children'),
        State('correlation_hover', 'is_open'),
        State('viewport_map_correlation', 'key')
    ]
)
def correlation_plot_update(in_select, in_transferlist, in_geojson, in_n_clicks, in_hover_data, state_map_children, state_is_hover, map_key):
    triggeredId = ctx.triggered_id

    transferlist_value = in_transferlist
    map_children = no_update
    corr_graph = no_update
    
    if triggeredId == 'edit_control':
        transferlist_value = switch_station_transferlist(in_geojson, transferlist_value)

    if isinstance(triggeredId, dict) and triggeredId['type'] == 'circle_marker':
        transferlist_value = update_transferlist(transferlist_value, triggeredId['code_name'])

    hover_data = None
    if state_is_hover and in_hover_data is not None:
        hover_data = in_hover_data['points'][0]

    map_children = update_map_markers(hover_data, transferlist_value, state_map_children)

    if triggeredId != 'correlation_graph':
        corr_graph = update_graph(
            selected_columns=[station['value'] for station in transferlist_value[1]],
            in_select=in_select
        )
    
    new_map_key = (map_key or 0) + 1

    return transferlist_value, new_map_key, map_children, corr_graph

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

def update_map_markers(hover_data: dict | None, transferlist_value: list[list[dict]], state_map_children: list):
    fill_color = ['blue'] * len(CITY.df_coordinates)
    for station in transferlist_value[1]:
        fill_color[station['index']] = 'red'

    if hover_data is not None:
        for station in ['x', 'y']:
            fill_color[CITY.df_coordinates[CITY.df_coordinates['code_name'].str.contains(hover_data[station])].index[0]] = 'yellow'

    return map_factory.update_children(state_map_children, map_factory.get_circle_markers(CITY, fill_color=fill_color))

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
def toggle_mode(checked, data_cookies):
    if checked:
        selected_station = data_cookies.get('selected_station')
        correlations = data.calculate_correlations(CITY, selected_station)

        corr_map = map_factory.viewport_map(CITY, 'viewport_on_map_correlation')
        map_factory.add_to_children(corr_map, [map_factory.get_colorbar((-1, 1))])
        map_factory.add_to_children(corr_map, map_factory.get_correlation_markers(CITY, correlations, type_marker='corr_switched_marker'))

        return html.Div(
            [
                corr_map
            ],
            id='correlation_on_map'
        )
    else:
        corr_map = map_factory.viewport_map(CITY, 'viewport_map_correlation', has_edit_control=True)
        map_factory.add_to_children(corr_map, map_factory.get_circle_markers(CITY, fill_color='red'))

        return html.Div(
            [
                corr_map,
                select_and_plot()
            ],
            id='correlation_layout'
        )

@callback(
    [
        Output('selected_station_store', 'data'),
        Output('viewport_on_map_correlation', 'key'),  
        Output('viewport_on_map_correlation', 'children'),  
    ],
    [
        Input({'type': 'corr_switched_marker', 'code_name': ALL, 'index': ALL}, 'n_clicks'),  
    ],
    [
        State('viewport_on_map_correlation', 'children'),
        State('selected_station_store', 'data'),
        State('viewport_on_map_correlation', 'key')
    ],
    prevent_initial_call=True
)
def update_on_circle_marker_click(n_clicks, state_map_children, selected_station_state, map_key):
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_station = json.loads(button_id)['code_name']

    if selected_station_state.get('selected_station') == selected_station:
        raise PreventUpdate

    correlations = data.calculate_correlations(CITY, selected_station)
    map_children = map_factory.update_children(
        map_children=state_map_children,
        new_children=map_factory.get_correlation_markers(CITY, correlations, type_marker='corr_switched_marker')
    )

    new_map_key = (map_key or 0) + 1

    return {'selected_station': selected_station}, new_map_key, map_children