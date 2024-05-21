import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup
from data.data import get_interpolated_indices
from tqdm import tqdm
from typing import Self, Any
import numpy as np
import os
import joblib

class PredictByLightGBM(PredictSetup):
    name = 'LightGBM'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float = 0.7, n_clusters: int = 5) -> None:
        super().__init__(city, prediction_length, train_size)
        self.models_dir = os.path.join(os.path.dirname(__file__), 'LightGBMModels')
        os.makedirs(self.models_dir, exist_ok=True)
        self.cluster_model = None
        self.station_clusters = None
        self.n_clusters = n_clusters

    def train(self: Self) -> None:
        df = self.train_dataset.copy()
        correlation_matrix = df.corr().values
        self.cluster_model = KMeans(n_clusters=self.n_clusters, random_state=42)
        clusters = self.cluster_model.fit_predict(correlation_matrix)
        self.station_clusters = {station: cluster for station, cluster in zip(df.columns, clusters)}

        df_station = df.copy().reset_index()
        df_station.rename(columns={'date': 'ds'}, inplace=True)
        df_station['hour'] = df_station['ds'].dt.hour
        df_station['day_of_week'] = df_station['ds'].dt.dayofweek
        df_station['day_of_month'] = df_station['ds'].dt.day
        df_station['month'] = df_station['ds'].dt.month
        df_station['is_weekend'] = df_station['ds'].dt.dayofweek >= 5

        for station in df.columns:
            station_path = os.path.join(self.models_dir, f'{station}_lightgbm_model.txt')
            scaler_path = os.path.join(self.models_dir, f'{station}_scaler.pkl')

            if os.path.exists(station_path) and os.path.exists(scaler_path):
                continue

            y = df_station[station].astype(float)
            X = df_station[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend']]

            window_size = 30 * 24  # 30 jours, 24 heures par jour
            forecasting_window = 7 * 24  # 7 jours, 24 heures par jour

            models = []
            scalers = []

            for start in tqdm(range(0, len(X) - window_size - forecasting_window + 1, forecasting_window)):
                end = start + window_size
                X_window = X.iloc[start:end]
                y_window = y.iloc[start:end]

                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_window)
                train_data = lgb.Dataset(X_scaled, label=y_window.values)

                params = {
                    'objective': 'regression',
                    'metric': 'rmse',
                    'n_estimators': 100,
                    'max_depth': 5,
                    'learning_rate': 0.05
                }
                model = lgb.train(params, train_data)

                models.append(model)
                scalers.append(scaler)

            # Save the last model and scaler
            models[-1].save_model(station_path)
            joblib.dump(scalers[-1], scaler_path)

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        station_path = os.path.join(self.models_dir, f'{selected_station}_lightgbm_model.txt')
        scaler_path = os.path.join(self.models_dir, f'{selected_station}_scaler.pkl')

        if not os.path.exists(station_path) or not os.path.exists(scaler_path):
            raise ValueError(f"Model for station {selected_station} not found.")

        model = lgb.Booster(model_file=station_path)
        scaler = joblib.load(scaler_path)

        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        future = pd.DataFrame({'ds': data_index})
        future['hour'] = future['ds'].dt.hour
        future['day_of_week'] = future['ds'].dt.dayofweek
        future['day_of_month'] = future['ds'].dt.day
        future['month'] = future['ds'].dt.month
        future['is_weekend'] = future['ds'].dt.dayofweek >= 5

        X_future_scaled = scaler.transform(future[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend']])
        predictions = model.predict(X_future_scaled)

        predictions = predictions.clip(0, 1)
        
        serie = pd.Series(predictions, index=data_index, name=PredictByLightGBM.name)
        
        return serie

# Exemple d'utilisation
# city = City()  # Instancier votre objet City
# method = PredictByLightGBM(city=city, prediction_length=168)
# method.train()
# predictions = method.predict('00001-poids-de-lhuile', data)
# print(predictions)
