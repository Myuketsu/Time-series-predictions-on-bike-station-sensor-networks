from dash import html, dcc, Input, Output, State
from dash import register_page, callback, no_update, ctx, no_update, ALL
from pandas import Series, date_range, DataFrame
from dash_iconify import DashIconify

import dash_mantine_components as dmc

from view import map_factory
import view.figures as figures
from data.prediction.methods import ForecastModel, FORECAST_MODELS, FORECAST_LENGTHS, PREDICTED_DATA
from data.city.load_cities import CITY

register_page(__name__, path='/metrics', name='Métriques', title='TER', order=6,
              category='Prédictions', icon='mdi:odometer')

# --- PAGE ---

def layout():
    return html.Div(
        [
            metrics_map_viewport(),
            options(),
            modal_station(),
            modal_global()
        ],
        id='metrics_layout'
    )

def options():
    return html.Div(
        [
            dmc.Button(
                'MÉTRIQUES GLOBALES',
                id='metrics_global_button',
                n_clicks=0,
                variant='gradient',
                gradient={'from': 'indigo', 'to': 'cyan'},
                leftIcon=DashIconify(icon='nimbus:stats', width=20),
            ),
            html.Div(className='prediction_vertical_line'),
            dmc.DatePicker(
                id='metrics_options_date_picker',
                locale='fr',
                value=CITY.df_hours['date'].iloc[0],
                clearable=False,
                maxDate=CITY.df_hours['date'].iloc[-(list(FORECAST_LENGTHS.values())[0] - 24)],
                minDate=CITY.df_hours['date'].iloc[0],
                label=dmc.Text('Début date de prédiction', weight=700),
                inputFormat='dddd, D MMMM YYYY',
                style={'width': 170}
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

def metrics_map_viewport():
    metrics_map = map_factory.viewport_map(CITY, 'metrics_map')

    colorscale = ['blue', 'green', 'yellow', 'orange', 'red']
    map_factory.add_to_children(metrics_map, [map_factory.get_colorbar((0, 1.0), colorscale)])

    first_df_predicted_data = list(PREDICTED_DATA.values())[0]
    first_forecast_length = list(FORECAST_LENGTHS.values())[0]
    
    metrics = {
        station_name: ForecastModel.get_metrics(
            predicted=first_df_predicted_data[station_name].iloc[:first_forecast_length],
            reality=CITY.df_hours[station_name].iloc[:first_forecast_length],
            metrics='mse'
        ) for station_name in CITY.df_coordinates['code_name']
    }
    map_factory.add_to_children(metrics_map, map_factory.get_metric_markers(CITY, 'mse', metrics, type_marker='metric_marker'))
    return metrics_map

def modal_station():
    first_station = CITY.df_coordinates['code_name'].iloc[0]
    first_forecast_length = list(FORECAST_LENGTHS.values())[0]
    
    model_list = []
    metric_list = []
    metric_value_list = []
    for model_name, df_predicted_data in PREDICTED_DATA.items():
        metrics = ForecastModel.get_metrics(
            predicted=df_predicted_data[first_station].iloc[:first_forecast_length],
            reality=CITY.df_hours[first_station].iloc[:first_forecast_length],
            metrics='all'
        )
        for metric_name, metric_value in metrics.items():
            model_list.append(model_name)
            metric_list.append(metric_name)
            metric_value_list.append(metric_value)
    df_metrics = DataFrame({'model': model_list, 'metric': metric_list, 'metric_value': metric_value_list})

    return dmc.Modal(
        title=dmc.Text(
            'Performance des modèles sur la station',
            transform='uppercase',
            variant='gradient',
            gradient={'from': '#36454f', 'to': '#003153'},
            weight=700,
            fz=20
        ),
        id='metrics_modal',
        zIndex=10_000,
        size='80%',
        children=[
            dcc.Graph(
                id='metrics_modal_compare_graph',
                figure=figures.compare_graph_metrics(
                    df_metrics,
                    (CITY.df_hours['date'].iloc[0].date(), CITY.df_hours['date'].iloc[first_forecast_length - 1].date()),
                    first_station
                )
            )
        ]
    )

def modal_global():
    first_forecast_length = list(FORECAST_LENGTHS.values())[0]
    
    model_list = []
    metric_list = []
    metric_value_list = []
    for model_name, df_predicted_data in PREDICTED_DATA.items():
        for station_name in CITY.df_coordinates['code_name']:
            metrics = ForecastModel.get_metrics(
                predicted=df_predicted_data[station_name].iloc[:first_forecast_length],
                reality=CITY.df_hours[station_name].iloc[:first_forecast_length],
                metrics='all'
            )
            for metric_name, metric_value in metrics.items():
                model_list.append(model_name)
                metric_list.append(metric_name)
                metric_value_list.append(metric_value)
    df_metrics = DataFrame({'model': model_list, 'metric': metric_list, 'metric_value': metric_value_list})
    df_metrics = df_metrics.groupby(['model', 'metric']).mean().reset_index()
    df_metrics['metric'] = df_metrics['metric'].str.upper()
    df_metrics = df_metrics.sort_values(['model', 'metric'])

    return dmc.Modal(
        title=dmc.Text(
            'Performance globale des modèles',
            transform='uppercase',
            variant='gradient',
            gradient={'from': '#36454f', 'to': '#003153'},
            weight=700,
            fz=20
        ),
        id='metrics_modal_global',
        zIndex=10_000,
        size='80%',
        children=[
            dcc.Graph(
                id='metrics_modal_compare_graph_global',
                figure=figures.compare_graph_metrics(
                    df_metrics,
                    (CITY.df_hours['date'].iloc[0].date(), CITY.df_hours['date'].iloc[first_forecast_length - 1].date())
                )
            )
        ]
    )

@callback(
    [
        Output('metrics_modal_global', 'opened'),
        Output('metrics_modal_compare_graph_global', 'figure')
    ],
    [
        Input('metrics_global_button', 'n_clicks')
    ],
    [
        State('metrics_options_date_picker', 'value'),
        State('metrics_options_select', 'value')
    ],
    prevent_initial_call=True
)
def update_modal(in_btn_nclicks, state_date, state_forecast_length):
    modal_is_open = True
    modal_graph = no_update

    data_index = date_range(start=state_date, periods=state_forecast_length, freq='1h')
    
    model_list = []
    metric_list = []
    metric_value_list = []
    for model_name, df_predicted_data in PREDICTED_DATA.items():
        for station_name in CITY.df_coordinates['code_name']:
            metrics = ForecastModel.get_metrics(
                predicted=df_predicted_data[station_name].loc[data_index],
                reality=FORECAST_MODELS[model_name].df_dataset[station_name].loc[data_index],
                metrics='all'
            )
            for metric_name, metric_value in metrics.items():
                model_list.append(model_name)
                metric_list.append(metric_name)
                metric_value_list.append(metric_value)
    df_metrics = DataFrame({'model': model_list, 'metric': metric_list, 'metric_value': metric_value_list})
    df_metrics = df_metrics.groupby(['model', 'metric']).mean().reset_index()
    df_metrics['metric'] = df_metrics['metric'].str.upper()

    modal_graph = figures.compare_graph_metrics(df_metrics, (data_index[0].date(), data_index[-1].date()))

    return modal_is_open, modal_graph

@callback(
    [
        Output('metrics_map', 'key'),
        Output('metrics_map', 'children'),
        Output('metrics_options_date_picker', 'maxDate'),
        Output('metrics_modal', 'opened'),
        Output('metrics_modal_compare_graph', 'figure'),
    ],
    [
        Input({'type': 'metric_marker', 'code_name': ALL, 'index': ALL}, 'n_clicks'),
        Input('metrics_options_date_picker', 'value'),
        Input('metrics_options_select', 'value'),
        Input('metrics_options_radiogroup', 'value'),
        Input('metrics_options_segmented', 'value')
    ],
    [
        State('metrics_map', 'children'),
        State('metrics_map', 'key')
    ],
    prevent_initial_call=True
)
def update_metric(in_marker, in_date, in_forecast_length, in_metric, in_model, state_map_children, state_map_key):
    triggeredId = ctx.triggered_id

    map_children = no_update
    date_picker_maxDate = no_update
    modal_is_open = no_update
    modal_graph = no_update

    if isinstance(triggeredId, dict) and triggeredId['type'] == 'metric_marker':
        data_index = date_range(start=in_date, periods=in_forecast_length, freq='1h')

        model_list = []
        metric_list = []
        metric_value_list = []
        for model_name, df_predicted_data in PREDICTED_DATA.items():
            metrics = ForecastModel.get_metrics(
                predicted=df_predicted_data[triggeredId['code_name']].loc[data_index],
                reality=FORECAST_MODELS[in_model].df_dataset[triggeredId['code_name']].loc[data_index],
                metrics='all'
            )
            for metric_name, metric_value in metrics.items():
                model_list.append(model_name)
                metric_list.append(metric_name)
                metric_value_list.append(metric_value)
        df_metrics = DataFrame({'model': model_list, 'metric': metric_list, 'metric_value': metric_value_list})
        df_metrics['metric'] = df_metrics['metric'].str.upper()
        df_metrics = df_metrics.sort_values(['model', 'metric'])

        modal_is_open = True
        modal_graph = figures.compare_graph_metrics(
            df_metrics,
            (data_index[0].date(), data_index[-1].date()),
            triggeredId['code_name']
        )

    if triggeredId in ['metrics_options_date_picker', 'metrics_options_select', 'metrics_options_radiogroup', 'metrics_options_segmented']:
        data_index = date_range(start=in_date, periods=in_forecast_length, freq='1h')
        metrics = {
            station_name: ForecastModel.get_metrics(
                predicted=PREDICTED_DATA[in_model][station_name].loc[data_index],
                reality=FORECAST_MODELS[in_model].df_dataset[station_name].loc[data_index],
                metrics=in_metric
            ) for station_name in CITY.df_coordinates['code_name']
        }

        map_children = map_factory.update_children(
            map_children=state_map_children,
            new_children=map_factory.get_metric_markers(CITY, in_metric, metrics, type_marker='metric_marker')
        )
    
    if triggeredId == 'metrics_options_select':
        date_picker_maxDate = CITY.df_hours['date'].iloc[-(in_forecast_length - 23)]
    
    new_map_key = (state_map_key or 0) + 1
    
    return new_map_key, map_children, date_picker_maxDate, modal_is_open, modal_graph