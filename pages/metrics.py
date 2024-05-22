from dash import html, dcc, Input, Output, State
from dash import register_page, callback, no_update

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from view import map_factory
from data.prediction.methods import ForecastModel, FORECAST_MODELS, FORECAST_LENGTHS
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
                label=dmc.Text('Période de prédiction', weight=700),
                placeholder='Select one',
                value=list(FORECAST_LENGTHS.values())[0],
                data=[{'value': v, 'label': l} for l, v in FORECAST_LENGTHS.items()],
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
                        value=list(FORECAST_MODELS.keys())[0],
                        radius='md',
                        data=list(FORECAST_MODELS.keys()),
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

    metrics = {
        station_name: ForecastModel.get_metrics(
            predicted=list(FORECAST_MODELS.values())[0].predict(station_name, ),
            reality=list(FORECAST_MODELS.values())[0],
            metrics='mse'
        ) for station_name in CITY.df_coordinates['code_name']
    }
    map_factory.add_to_children(metrics_map, map_factory.get_metric_markers(CITY, 'mse', metrics, type_marker='metric_marker'))
    return metrics_map