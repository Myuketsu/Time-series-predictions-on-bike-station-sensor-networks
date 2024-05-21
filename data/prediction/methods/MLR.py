import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Self
import joblib
from data.city.load_cities import City
from data.prediction.forecast_model import PredictSetup

class PredictByMultipleLinearRegression(PredictSetup):
    name = 'MultipleLinearRegression'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float = 0.7, lags: int = 3) -> None:
        super().__init__(city, prediction_length, train_size)
        self.models = {}
        self.feature_names = {}
        self.lags = lags
        self.model_dir = os.path.join(os.path.dirname(__file__), 'MLRModels')
        os.makedirs(self.model_dir, exist_ok=True)

    def add_lag_features(self, df: pd.DataFrame, station: str) -> pd.DataFrame:
        for lag in range(1, self.lags + 1):
            df[f'lag_{lag}'] = df[station].shift(lag + self.prediction_length).fillna(method='bfill')
        df = df.dropna().reset_index(drop=True)
        return df

    def train(self: Self) -> None:
        df = self.train_dataset.copy()

        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_model.pkl')

            if os.path.exists(model_path):
                model = joblib.load(model_path)
                with open(os.path.join(self.model_dir, f'{station}_feature_names.pkl'), 'rb') as f:
                    self.feature_names[station] = joblib.load(f)
            else:
                df_station = df[[station]].reset_index()
                df_station.rename(columns={'date': 'ds'}, inplace=True)

                df_station['hour'] = df_station['ds'].dt.hour
                df_station['day_of_week'] = df_station['ds'].dt.dayofweek
                df_station['day_of_month'] = df_station['ds'].dt.day
                df_station['month'] = df_station['ds'].dt.month
                df_station['is_weekend'] = df_station['ds'].dt.dayofweek >= 5
                df_station['is_sunday'] = df_station['ds'].dt.dayofweek == 6


                df_station = pd.get_dummies(df_station, columns=['hour','day_of_week','day_of_month', 'month','is_weekend', 'is_sunday'], drop_first=True)

                X = df_station.drop(columns=['ds', station])
                y = df_station[station]

                self.feature_names[station] = X.columns.tolist()

                model = LinearRegression()
                model.fit(X, y)

                joblib.dump(model, model_path)
                with open(os.path.join(self.model_dir, f'{station}_feature_names.pkl'), 'wb') as f:
                    joblib.dump(self.feature_names[station], f)

            self.models[station] = model

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f"Model for station {selected_station} not found.")

        model = self.models[selected_station]

        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        future = pd.DataFrame({'ds': data_index})
        future['hour'] = future['ds'].dt.hour
        future['day_of_week'] = future['ds'].dt.dayofweek
        future['day_of_month'] = future['ds'].dt.day
        future['month'] = future['ds'].dt.month
        future['is_weekend'] = future['ds'].dt.dayofweek >= 5
        future['is_sunday'] = future['ds'].dt.dayofweek == 6


        future = pd.get_dummies(future, columns=['hour','day_of_week','day_of_month', 'month','is_weekend', 'is_sunday'], drop_first=True)

        for col in self.feature_names[selected_station]:
            if col not in future.columns:
                future[col] = 0

        X_future = future[self.feature_names[selected_station]]

        predictions = model.predict(X_future).flatten()
        predictions = predictions.clip(0, 1)

        serie = pd.Series(predictions, index=data_index, name=PredictByMultipleLinearRegression.name)
        return serie