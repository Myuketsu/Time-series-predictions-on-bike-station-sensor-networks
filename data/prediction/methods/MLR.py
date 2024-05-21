import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import Self
import joblib
from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup

class PredictByMultipleLinearRegression(PredictSetup):
    name = 'MultipleLinearRegression'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float = 0.7, lags: int = 3) -> None:
        super().__init__(city, prediction_length, train_size)
        self.models = {}
        self.scalers = {}
        self.lags = lags
        self.model_dir = os.path.join(os.path.dirname(__file__), 'MLRModels')
        os.makedirs(self.model_dir, exist_ok=True)

    def add_lag_features(self, df: pd.DataFrame, station: str) -> pd.DataFrame:
        for lag in range(1, self.lags + 1):
            df[f'lag_{lag}'] = df[station].shift(lag + self.prediction_length).fillna(0)
        df = df.dropna().reset_index(drop=True)
        return df

    def train(self: Self) -> None:
        df = self.train_dataset.copy()

        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_model.pkl')
            scaler_path = os.path.join(self.model_dir, f'{station}_scaler.pkl')

            if os.path.exists(model_path) and os.path.exists(scaler_path):
                model = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
            else:
                df_station = df[[station]].reset_index()
                df_station.rename(columns={'date': 'ds'}, inplace=True)

                df_station['hour'] = df_station['ds'].dt.hour
                df_station['day_of_week'] = df_station['ds'].dt.dayofweek
                df_station['day_of_month'] = df_station['ds'].dt.day
                df_station['month'] = df_station['ds'].dt.month
                df_station['is_weekend'] = df_station['ds'].dt.dayofweek >= 5
                df_station['is_sunday'] = df_station['ds'].dt.dayofweek == 6

                df_station = self.add_lag_features(df_station, station)

                df_station = pd.get_dummies(df_station, columns=['day_of_week', 'is_weekend', 'is_sunday'], drop_first=True)

                X = df_station.drop(columns=['ds', station])
                y = df_station[station]

                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)

                model = LinearRegression()
                model.fit(X_scaled, y)

                joblib.dump(model, model_path)
                joblib.dump(scaler, scaler_path)

            self.models[station] = model
            self.scalers[station] = scaler

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f"Model for station {selected_station} not found.")

        model = self.models[selected_station]
        scaler = self.scalers[selected_station]

        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        future = pd.DataFrame({'ds': data_index})
        future['hour'] = future['ds'].dt.hour
        future['day_of_week'] = future['ds'].dt.dayofweek
        future['day_of_month'] = future['ds'].dt.day
        future['month'] = future['ds'].dt.month
        future['is_weekend'] = future['ds'].dt.dayofweek >= 5
        future['is_sunday'] = future['ds'].dt.dayofweek == 6

        history = data[-(self.lags + self.prediction_length):]  
        for lag in range(1, self.lags + 1):
            if lag < len(history):
                future[f'lag_{lag}'] = history.shift(lag).fillna(0).values[-len(future):]
            else:
                future[f'lag_{lag}'] = 0

        future = pd.get_dummies(future, columns=['day_of_week', 'is_weekend', 'is_sunday'], drop_first=True)

        for col in scaler.feature_names_in_:
            if col not in future.columns:
                future[col] = 0

        X_future = future.drop(columns=['ds'])

        X_future_scaled = scaler.transform(X_future)

        predictions = model.predict(X_future_scaled).flatten()
        predictions = predictions.clip(0, 1)

        serie = pd.Series(predictions, index=data_index, name=PredictByMultipleLinearRegression.name)
        return serie

