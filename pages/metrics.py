from dash import html, dcc, Input, Output, State
from dash import register_page, callback, no_update

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc

import data.data as data
import view.figures as figures
from view import map_factory
import data.prediction.methods as prediction_method
from data.city.load_cities import CITY

register_page(__name__, path='/metrics', name='Métriques', title='TER', order=6,
              category='Prédictions', icon='mdi:odometer')

# --- PAGE ---

def layout():
    return html.Div(
        [
            metrics_map(),
            options()
        ],
        id='metrics_layout'
    )

def options():
    return html.Div(
        [
            dmc.DatePicker(
                id='metrics_options_date_picker',
                locale='fr',
                value=CITY.df_hours['date'].iloc[0],
                clearable=False,
                maxDate=CITY.df_hours['date'].iloc[-(prediction_method.CONTEXT_LENGTH + prediction_method.PREDICTION_LENGTH - 24)],
                minDate=CITY.df_hours['date'].iloc[0],
                label=dmc.Text('Plage de données de contexte', weight=700),
                inputFormat='dddd, D MMMM YYYY',
                style={'width': 200}
            ),
            dmc.Select(
                label=dmc.Text('Période (prédiction / contexte)', weight=700),
                placeholder='Select one',
                value=168,
                data=[
                    {'value': 24, 'label': '1 jour / 1 semaine'},
                    {'value': 168, 'label': '1 semaine / 1 mois'}
                ],
                id='metrics_options_select'
            ),
            html.Div(
                [
                    dmc.RadioGroup(
                        label=dmc.Text('Métrique', weight=700),
                        value='mse',
                        children=[dmc.Radio(l, value=v) for v, l in {'mse': 'MSE', 'mae': 'MAE'}.items()],
                        size='sm',
                        spacing='sm',
                        id='metrics_options_radiogroup'
                    )
                ],
                id='metrics_options_radiogroup_box'
            ),
            html.Div(
                [
                    dmc.Text('Choix du modèle de prédiction', weight=700, size=14, color='rgb(33, 37, 41)'),
                    dmc.SegmentedControl(
                        value=prediction_method.PREDICTION_METHODS[0].name,
                        radius='md',
                        data=[method.name for method in prediction_method.PREDICTION_METHODS],
                        id='metrics_options_segmented',
                    )
                ],
                id='metrics_options_segmented_box'
            )
            
        ],
        id='metrics_options'
    )

def metrics_map():
    metrics_map = map_factory.viewport_map(CITY, 'metrics_map')
    map_factory.add_to_children(metrics_map, [map_factory.get_colorbar((0, 0.5))])

    metrics = {station_name: prediction_method.PREDICTION_METHODS[0].predict() for station_name in }
    map_factory.add_to_children(metrics_map, map_factory.get_metric_markers(CITY, 'mse', metrics, type_marker='metric_marker'))
    return metrics_map