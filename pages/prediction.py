from dash import html, register_page

import dash_mantine_components as dmc

import data.prediction.methods as prediction_method
from data.prediction.prediction_setup import PredictSetup
from data.city.load_cities import CITY

register_page(__name__, path='/prediction', name='Prédictions', title='TER', order=5,
              category='Prédictions', icon='mdi:location-off-outline')

# --- INITIALISATION ---

TRAIN_SIZE = 0.7
PREDICTION_METHODS: list[PredictSetup] = [
    prediction_method.PredictByMean(city=CITY, train_size=TRAIN_SIZE),
    PredictSetup(city=CITY, train_size=TRAIN_SIZE),
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
            dmc.SegmentedControl(
                id='prediction_SegmentedControl_method',
                fullWidth=False,
                value=PREDICTION_METHODS[0].name,
                data=[{'value': method.name, 'label': method.name} for method in PREDICTION_METHODS]
            ),
            dmc.Slider(
                id="prediction_Slider_predict",
                value=26,
                min=0,
                max=len(CITY.df_hours) // 168, # 24 Heures * 7 Jours = 168 Heures (Une semaine)
                updatemode="drag",
                marks=[{'value': 4 * index, 'label': month} for index, month in enumerate(CITY.df_hours['date'].dt.month_name(locale='French').unique())],
            ),
        ],
        id='prediction_form'
    )

def graph_area():
    return html.Div(
        [
            
        ],
        id='prediction_graph_area'
    )