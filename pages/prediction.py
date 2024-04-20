from dash import html, dcc, Input, Output, State
from dash import register_page, callback, no_update

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc

import data.data as data
import data.prediction.methods as prediction_method
from data.prediction.prediction_setup import PredictSetup
from data.city.load_cities import CITY

register_page(__name__, path='/prediction', name='Prédictions', title='TER', order=5,
              category='Prédictions', icon='mdi:location-off-outline')

# --- INITIALISATION ---

TRAIN_SIZE = 0.7
PREDICTION_METHODS: list[PredictSetup] = [
    prediction_method.PredictByMean(city=CITY, train_size=TRAIN_SIZE),
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
                value=CITY.df_hours['date'].iloc[0],
                clearable=False,
                maxDate=CITY.df_hours['date'].iloc[-(6 * 24)], # 7 Jours * 24 Heures = 1 Semaine
                minDate=CITY.df_hours['date'].iloc[0],
                label=dcc.Markdown('**Premier** jour de la plage de données de contexte'),
                inputFormat='dddd, D MMMM YYYY - 00:00',
                locale='fr',
                style={'width': 350}
            ),
            dmc.Divider(
                id='prediction_divider_date_range',
                label=dcc.Markdown('Plage de données d\'**une semaine**'),
                labelPosition='center'
            ),
            dmc.DatePicker(
                id='prediction_date_picker_end',
                value=CITY.df_hours['date'].iloc[5],
                label=dcc.Markdown('**Dernier** jour de la plage de données de contexte'),
                inputFormat='dddd, D MMMM YYYY - 23:00',
                locale='fr',
                disabled=True,
                style={'width': 350}
            )
        ],
        id='prediction_date_range_picker'
    )

def get_modal():
    return dmc.Modal(
        title='Gestion et traitement du jeu de données',
        id='prediction_modal',
        zIndex=10_000,
        size='70%',
        children=[
            dmc.Divider(),
            get_dataset_distribution(TRAIN_SIZE)
        ]
    )

def get_dataset_distribution(pct: float):
    return html.Div(
        [
            dmc.Text('Répartion du jeu de données', weight=700, transform='uppercase'),
            get_dataset_distribution_bar(pct)
        ],
        id='prediction_dataset_distribution'
    )

def get_dataset_distribution_bar(pct: float):
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
                            PREDICTION_METHODS[0].train_dataset.index[0].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_training_date_start'
                    ),
                    html.Div(
                        dmc.Text(
                            PREDICTION_METHODS[0].train_dataset.index[-1].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_training_date_end', style={'right': f'{100 - pct}%'}
                    ),
                    html.Div(
                        dmc.Text(
                            PREDICTION_METHODS[0].test_dataset.index[-1].strftime('%d-%m-%Y'), size=9
                        ),
                        id='prediction_dataset_test_date_end'
                    ),
                ],
                id='prediction_dataset_distribution_date'
            )
        ],
        id='prediction_dataset_distribution_body'
    )

def graph_area():
    return html.Div(
        [
            
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
    ]
)
def update_end_date(date_start):
    return (data.get_shifted_date(date_start), )


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