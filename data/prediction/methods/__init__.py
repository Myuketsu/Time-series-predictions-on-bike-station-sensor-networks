import joblib
import pandas as pd

from tqdm import tqdm

from data.prediction.methods.mean_predictor import PredictByMean
from data.prediction.methods.XGBoost import XGBoost
from data.prediction.methods.XGBoostACP import XGBoostPCA
from data.prediction.methods.PCApredictor import PredictByPCA
from data.prediction.methods.MLR import MultipleLinearRegression
from data.prediction.methods.RandomForest import RandomForestPredictor

from data.prediction.forecast_model import ForecastModel, PATH_MODEL

from data.city.load_cities import CITY

# --- INITIALISATION ---

TRAIN_SIZE = 0.7
FORECAST_LENGTHS: dict[str, int] = {'1 semaine': 168, '1 jour': 24}

__MODELS: list[ForecastModel] = [
    PredictByMean,
    PredictByPCA,
    XGBoost,
    XGBoostPCA,
    MultipleLinearRegression,
    RandomForestPredictor
]

FORECAST_MODELS: dict[str, ForecastModel] = {
    model.name: model(city=CITY, train_size=TRAIN_SIZE) for model in __MODELS
}

for forecast_model in FORECAST_MODELS.values():
    forecast_model.train()

PREDICTED_DATA: dict[str, pd.DataFrame] = {}
try:
    PREDICTED_DATA = joblib.load(f'{PATH_MODEL}predicted_data.pkl')
except FileNotFoundError:
    __start_date: pd.Series = pd.Series(1, index=[CITY.df_hours['date'].iloc[0]])
    for name, model in tqdm(FORECAST_MODELS.items(), desc='Génération des prédictions pour chaque modèle'):
        series_list: list[pd.Series ] = [
            model.predict(station_name, __start_date, len(CITY.df_hours)).rename(station_name)
            for station_name in CITY.df_coordinates['code_name']
        ]
        PREDICTED_DATA[name] = pd.concat(series_list, axis='columns')
    joblib.dump(PREDICTED_DATA, f'{PATH_MODEL}predicted_data.pkl', compress=3)