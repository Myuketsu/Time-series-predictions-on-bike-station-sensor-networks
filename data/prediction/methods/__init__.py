from data.prediction.methods.mean_predictor import PredictByMean
from data.prediction.methods.XGBoost import XGBoost
from data.prediction.methods.XGBoostACP import XGBoostPCA
from data.prediction.methods.PCApredictor import PredictByPCA
from data.prediction.methods.MLR import MultipleLinearRegression
from data.prediction.methods.RandomForest import RandomForestPredictor

from data.prediction.forecast_model import ForecastModel

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