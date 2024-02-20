# Dash imports
from dash import html, dcc, Input, Output, State
from dash import register_page, callback
from dash import ctx, no_update

# Dash extensions
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from data.city.load_cities import CITY
import data.data as data
from view.map import viewport_map
from view.figures import correlation_plot

register_page(__name__, path='/correlation', name='Correlation', title='TER', order=3,
              category='Statistique Descriptive', icon='arcticons:cpustats')

def layout():
    return html.Div(
        [
            viewport_map(CITY, 'viewport_map_correlation'),
            select_and_plot()
        ],
        id='correlation_layout'
    )

def select_and_plot():
    initial_values_codes_names = [[], [
        {'value': city, 'label': city}
        for city in CITY.df_coordinates['code_name'].to_list()]]
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
                data=['Alphabétique', 'Regroupement'],
                value='Alphabétique',
                id='select_correlation'
            )
        ],
        id='select_container_correlation'
    )

def get_correlation_plot():
    return dmc.LoadingOverlay(
        [
            dcc.Graph(
                figure=correlation_plot(
                    data.get_correlation_on_selected_stations(
                        city=CITY,
                        columns=CITY.df_coordinates['code_name'].to_list(),
                        ordered=True
                    )
                ),
                id='correlation_graph'
            )
        ],
        id='correlation_plot'
    )