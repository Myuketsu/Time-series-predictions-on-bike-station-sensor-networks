from dash import html, dcc, Input, Output, State
from dash import register_page, callback, no_update

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import data.data as data
import view.figures as figures
import data.prediction.methods as prediction_method
from data.city.load_cities import CITY

import pandas as pd

FORECAST_MODELS = prediction_method.FORECAST_MODELS
FORECAST_LENGTHS = prediction_method.FORECAST_LENGTHS
PREDICTED_DATA = prediction_method.PREDICTED_DATA

register_page(__name__, path='/prediction', name='Prédictions', title='TER', order=5,
              category='Prédictions', icon='clarity:bell-curve-line')

# --- PAGE ---

def layout():
    return html.Div(
        [
            form(),
            graph_area()
        ],
        id='prediction_layout'
    )

def form():
    return html.Div(
        [
            get_station_selector(),
            html.Div(className='prediction_vertical_line'),
            get_forecast_date_picker(),
            html.Div(className='prediction_vertical_line'),
            get_forecast_length_selector(),
            html.Div(className='prediction_vertical_line'),
            dmc.Button(
                'DATASET',
                id='prediction_info_button',
                n_clicks=0,
                variant='gradient',
                gradient={'from': 'indigo', 'to': 'cyan'},
                leftIcon=DashIconify(icon='material-symbols:info-outline', width=20),
            ),
            get_modal()
        ],
        id='prediction_form'
    )

def get_station_selector():
    return html.Div(
        [
            dmc.Select(
                id='prediction_station_select',
                label='Station d\'intérêt',
                placeholder='Merci de sélectionner une station...',
                nothingFound='Aucune station trouvée',
                searchable=True,
                value=CITY.df_coordinates['code_name'].iloc[0],
                data=CITY.df_coordinates['code_name'].to_list()
            )
        ],
        id='prediction_station_selector'
    )

def get_forecast_date_picker():
    return html.Div(
        [
            dmc.DatePicker(
                id='prediction_date_picker',
                locale='fr',
                value=CITY.df_hours['date'].iloc[0],
                clearable=False,
                maxDate=CITY.df_hours['date'].iloc[-1],
                minDate=CITY.df_hours['date'].iloc[0],
                label=dcc.Markdown('**Date de début de la prédiction**'),
                inputFormat='dddd, D MMMM YYYY - 00:00',
                style={'width': 320}
            )
        ],
        id='forecast_date_picker'
    )

def get_forecast_length_selector():
    first_key = list(FORECAST_LENGTHS.keys())[0]
    first_value = FORECAST_LENGTHS[first_key]
    return html.Div(
        [
            dmc.Select(
                id='forecast_length_select',
                label='Durée de la prédiction',
                placeholder='Merci de sélectionner une durée...',
                value=first_value,
                data=[{'label': k, 'value': v} for k, v in FORECAST_LENGTHS.items()]
            )
        ],
        id='forecast_length_selector'
    )

def get_modal():
    return dmc.Modal(
        title=dmc.Text(
            'Gestion et traitement du jeu de données',
            transform='uppercase',
            variant='gradient',
            gradient={'from': '#36454f', 'to': '#003153'},
            weight=700,
            fz=20
        ),
        id='prediction_modal',
        zIndex=10_000,
        size='75%',
        children=[
            dmc.Divider(label=dmc.Text('Répartion du jeu de données', weight=700, transform='uppercase'), labelPosition='center'),
            dmc.Text((
                'Nous avons procédé à la création de deux jeu de données (datasets) distincts à partir du jeu de données d\'origine. '
                'Dans un premier temps, le dataset d\'entraînement a pour objectif d\'entraîner notre modèle en lui fournissant un échantillon significatif de données. '
                'Dans un second temps, le dataset de test servira à évaluer la performance et la généralisation de notre modèle. '
                'Ils ont la répartition suivante des données du jeu de données d\'origine :'
            ), mt=12, mb=12),
            get_dataset_distribution(prediction_method.TRAIN_SIZE),
            dmc.Divider(label=dmc.Text('Caractéristiques du jeu de données', weight=700, transform='uppercase'), labelPosition='center'),
            dmc.Text((
                'Le jeu de données présente un nombre significatif de valeurs manquantes, représentées par des NaN. '
                'Afin de pallier ce problème, des interpolations de ces données manquantes ont été réalisées. '
                'Cette particularité dans la structure des données sera prise en compte lors de la phase d\'entraînement des divers modèles.'
            ), mt=12, mb=12),
            get_data_features()
        ]
    )

def get_dataset_distribution(pct: float):
    pct = pct * 100
    return html.Div(
        [
            html.Div(
                [
                    html.Div(dmc.Text(f'{pct}%', size=9), id='prediction_dataset_training_percentage', style={'width': f'{pct}%'}),
                    html.Div(dmc.Text(f'{100 - pct}%', size=9), id='prediction_dataset_test_percentage', style={'width': f'{100 - pct}%'})
                ],
                id='prediction_dataset_distribution_percentage'
            ),
            html.Div(
                [
                    html.Div(dmc.Text('Données d\'entraînement', size=11, transform='uppercase'), id='prediction_dataset_training_bar', style={'width': f'{pct}%'}),
                    html.Div(dmc.Text('Données de test', size=11, transform='uppercase'), id='prediction_dataset_test_bar', style={'width': f'{100 - pct}%'})
                ],
                id='prediction_dataset_distribution_bar'
            ),
            html.Div(
                [
                    html.Div(
                        dmc.Text(
                            prediction_method.FORECAST_MODELS['XGBoost'].train_dataset.index[0].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_training_date_start'
                    ),
                    html.Div(
                        dmc.Text(
                            prediction_method.FORECAST_MODELS['XGBoost'].train_dataset.index[-1].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_training_date_end', style={'right': f'{100 - pct}%'}
                    ),
                    html.Div(
                        dmc.Text(
                            prediction_method.FORECAST_MODELS['XGBoost'].test_dataset.index[-1].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_test_date_end'
                    ),
                ],
                id='prediction_dataset_distribution_date'
            )
        ],
        id='prediction_dataset_distribution_body'
    )

def get_data_features():
    return html.Div(
        [
            html.Div(dmc.Select(
                id='prediction_station_select_info',
                label='Station d\'intérêt',
                placeholder='Merci de sélectionner une station...',
                nothingFound='Aucune station trouvée',
                searchable=True,
                value=CITY.df_coordinates['code_name'].iloc[0],
                data=CITY.df_coordinates['code_name'].to_list()
            ), id='prediction_station_select_info_box'),
            dcc.Graph(
                id='prediction_interpolation_graph',
                figure=figures.interpolation_plot_analyzer(
                    city=CITY,
                    station=CITY.df_coordinates['code_name'].iloc[0],
                    interpolated_indices=data.get_interpolated_indices(
                        serie=CITY.df_hours[CITY.df_coordinates['code_name'].iloc[0]],
                        output_type='list'
                    )
                )
            )
        ],
        id='prediction_data_features'
    )

def graph_area():
    return html.Div(
        [
            dcc.Graph(
                id='prediction_main_graph',
                figure=figures.main_graph_prediction(
                    station_name=CITY.df_coordinates['code_name'].iloc[0],
                    methods=[],
                    reality_data=pd.Series(dtype=float)
                ),
                style={'width': '100%'}
            )
        ],
        id='prediction_graph_area'
    )

# --- CALLBACKS ---

@callback(
    Output('prediction_modal', 'opened'),
    Input('prediction_info_button', 'n_clicks'),
    State('prediction_modal', 'opened'),
    prevent_initial_call=True
)
def update_modal(in_btn_nclicks, state_opened):
    return (not state_opened, )

@callback(
    [
        Output('prediction_interpolation_graph', 'figure')
    ],
    [
        Input('prediction_station_select_info', 'value')
    ],
    prevent_initial_call=True
)
def update_modal(in_select):
    fig = figures.interpolation_plot_analyzer(
        city=CITY,
        station=in_select,
        interpolated_indices=data.get_interpolated_indices(
            serie=CITY.df_hours[in_select],
            output_type='list'
        )
    )
    return (fig, )


@callback(
    Output('prediction_main_graph', 'figure'),
    [
        Input('prediction_station_select', 'value'),
        Input('prediction_date_picker', 'value'),
        Input('forecast_length_select', 'value')
    ],
)
def update_main_graph(station, start_date, forecast_length):
    data_index = pd.date_range(start=start_date, periods=forecast_length, freq='h')
    reality_data = FORECAST_MODELS['XGBoost'].df_dataset[station].loc[data_index]

    predictions = [
        df_predicted_data[station].loc[data_index].rename(name) for name, df_predicted_data in PREDICTED_DATA.items()
    ]

    fig = figures.main_graph_prediction(
        station_name=station,
        methods=predictions,
        reality_data=reality_data
    )

    return fig