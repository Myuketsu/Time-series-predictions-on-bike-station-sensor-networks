from dash import html, dcc, Input, Output, State
from dash import register_page, callback, no_update

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc

import data.data as data
import view.figures as figures
import data.prediction.methods as prediction_method
from data.prediction.prediction_setup import PredictSetup
from data.city.load_cities import CITY

register_page(__name__, path='/prediction', name='Prédictions', title='TER', order=5,
              category='Prédictions', icon='mdi:location-off-outline')

# --- INITIALISATION ---

CONTEXT_LENGTH = 168 # 24 Heures * 7 Jours = 168 Heures = 1 Semaine
PREDICTION_LENGTH = 168 # 24 Heures * 7 Jours = 168 Heures = 1 Semaine

TRAIN_SIZE = 0.7
PREDICTION_METHODS: list[PredictSetup] = [
    prediction_method.PredictByMean(city=CITY, prediction_length=PREDICTION_LENGTH, train_size=TRAIN_SIZE),
    prediction_method.PredictByXGBoost(city=CITY, prediction_length=PREDICTION_LENGTH, train_size=TRAIN_SIZE),
    prediction_method.PredictByXGBoostWithPCA(city=CITY, prediction_length=PREDICTION_LENGTH, train_size=TRAIN_SIZE),
    prediction_method.PredictByPCA(city=CITY, prediction_length=PREDICTION_LENGTH, train_size=TRAIN_SIZE)
]

for method in PREDICTION_METHODS:
    method.train()

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
            get_date_range_picker(),
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

def get_date_range_picker():
    return html.Div(
        [
            dmc.DatePicker(
                id='prediction_date_picker_start',
                locale='fr',
                value=CITY.df_hours['date'].iloc[0],
                clearable=False,
                maxDate=CITY.df_hours['date'].iloc[-(CONTEXT_LENGTH + PREDICTION_LENGTH - 24)],
                minDate=CITY.df_hours['date'].iloc[0],
                label=dcc.Markdown('**Premier** jour de la plage de données de contexte'),
                inputFormat='dddd, D MMMM YYYY - 00:00',
                style={'width': 350}
            ),
            dmc.Divider(
                id='prediction_divider_date_range',
                label=dcc.Markdown('Plage de données d\'**une semaine**'),
                labelPosition='center'
            ),
            dmc.DatePicker(
                id='prediction_date_picker_end',
                locale='fr',
                value=update_end_date(CITY.df_hours['date'].iloc[0])[0],
                label=dcc.Markdown('**Dernier** jour de la plage de données de contexte'),
                inputFormat='dddd, D MMMM YYYY - 23:00',
                disabled=True,
                style={'width': 350}
            )
        ],
        id='prediction_date_range_picker'
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
            get_dataset_distribution(TRAIN_SIZE),
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
                            PREDICTION_METHODS[1].train_dataset.index[0].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_training_date_start'
                    ),
                    html.Div(
                        dmc.Text(
                            PREDICTION_METHODS[1].train_dataset.index[-1].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_training_date_end', style={'right': f'{100 - pct}%'}
                    ),
                    html.Div(
                        dmc.Text(
                            PREDICTION_METHODS[1].test_dataset.index[-1].strftime('%d-%m-%Y'), size=9
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
    context_data = PREDICTION_METHODS[1].df_dataset[CITY.df_coordinates['code_name'].iloc[0]].iloc[:CONTEXT_LENGTH]
    reality_data = PREDICTION_METHODS[1].df_dataset[CITY.df_coordinates['code_name'].iloc[0]].iloc[CONTEXT_LENGTH:CONTEXT_LENGTH + PREDICTION_LENGTH]
    return html.Div(
        [
            dcc.Graph(
                id='prediction_main_graph',
                figure=figures.main_graph_prediction(
                    station_name=CITY.df_coordinates['code_name'].iloc[0],
                    methods=[method.predict(CITY.df_coordinates['code_name'].iloc[0], context_data) for method in PREDICTION_METHODS],
                    reality_data=reality_data
                ),
                style={'width': '100%'}
            )
        ],
        id='prediction_graph_area'
    )

# --- CALLBACKS ---

@callback(
    [
        Output('prediction_date_picker_end', 'value')
    ],
    [
        Input('prediction_date_picker_start', 'value')
    ],
    prevent_initial_call=True
)
def update_end_date(date_start):
    return (data.get_shifted_date(date_start, CONTEXT_LENGTH - 1), )


@callback(
    [
        Output('prediction_modal', 'opened')
    ],
    [
        Input('prediction_info_button', 'n_clicks')
    ],
    [
        State('prediction_modal', 'opened')
    ],
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
    [
        Output('prediction_main_graph', 'figure')
    ],
    [
        Input('prediction_station_select', 'value'),
        Input('prediction_date_picker_start', 'value')
    ],
    prevent_initial_call=True
)
def update_main_graph(in_select, in_start_date):
    context_data = PREDICTION_METHODS[1].df_dataset[in_select].loc[
        in_start_date:data.get_shifted_date(in_start_date, CONTEXT_LENGTH - 1)
    ]
    reality_data = PREDICTION_METHODS[1].df_dataset[in_select].loc[
        data.get_shifted_date(in_start_date, CONTEXT_LENGTH):data.get_shifted_date(in_start_date, CONTEXT_LENGTH + PREDICTION_LENGTH - 1)
    ]

    fig = figures.main_graph_prediction(
        station_name=in_select,
        methods=[method.predict(in_select, context_data) for method in PREDICTION_METHODS],
        reality_data=reality_data
    )

    return (fig, )