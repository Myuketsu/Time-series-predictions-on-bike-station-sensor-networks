from data.prediction.methods.mean_predictor import PredictByMean
from data.prediction.methods.XGBoost import XGBoost
from data.prediction.methods.XGBoostACP import PredictByXGBoostWithPCA
from data.prediction.methods.PCApredictor import PredictByPCA
from data.prediction.methods.MLR import PredictByMultipleLinearRegression
from data.prediction.methods.RandomForest import RandomForestPredictor

from data.prediction.forecast_model import ForecastModel

from data.city.load_cities import CITY

# --- INITIALISATION ---

TRAIN_SIZE = 0.7

__MODELS: list[ForecastModel] = [
    PredictByMean,
    PredictByPCA,
    XGBoost,
    PredictByXGBoostWithPCA,
    PredictByMultipleLinearRegression,
    RandomForestPredictor
]

FORECAST_MODELS: dict[str, ForecastModel] = {
    method.name: method(city=CITY, train_size=TRAIN_SIZE) for method in __MODELS
}

for forecast_model in FORECAST_MODELS.values():
    forecast_model.train()