import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from typing import Self
import joblib
from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup

class RandomForestPredictor(PredictSetup):
    name = 'RandomForestPredictor'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float = 0.7, n_estimators: int = 5, max_depth: int = 5, min_samples_leaf: int = 5, hours: int = 168) -> None:
        super().__init__(city, prediction_length, train_size)
        self.models = {}
        self.hours = hours
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.model_dir = os.path.join(os.path.dirname(__file__), 'RFModels')
        os.makedirs(self.model_dir, exist_ok=True)

    def train(self: Self) -> None:
        df = self.train_dataset.copy()
        time_window = self.hours
        forecasting_window = self.prediction_length

        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_model.pkl')
            if os.path.exists(model_path):
                model = joblib.load(model_path)
            else:
                s = df[station]
                X = []
                y = []
                for i in range(0, len(s) - time_window - forecasting_window):
                    X.append(s.iloc[i:i + time_window].reset_index(drop=True))
                    y.append(s.iloc[i + time_window: i + time_window + forecasting_window].reset_index(drop=True))
                X = pd.DataFrame(X)
                y = pd.DataFrame(y)

                model = RandomForestRegressor(
                    n_estimators=self.n_estimators,
                    max_depth=self.max_depth,
                    min_samples_leaf=self.min_samples_leaf,
                    n_jobs=-1,
                    verbose=2
                )
                model.fit(X, y)

                joblib.dump(model, model_path, compress=7)  

            self.models[station] = model

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f"Model for station {selected_station} not found.")

        model = self.models[selected_station]

        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        time_window = self.hours

        future = data.iloc[-time_window:].reset_index(drop=True)
        if len(future) != time_window:
            raise ValueError(f"Expected {time_window} data points, but got {len(future)}.")

        X_future = pd.DataFrame([future])

        predictions = model.predict(X_future).flatten()
        predictions = predictions.clip(0, 1)

        serie = pd.Series(predictions, index=data_index, name=RandomForestPredictor.name)
        return serie
