import os
import joblib
import pandas as pd
import xgboost as xgb
from typing import Self
from sklearn.cluster import KMeans
from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup
from data.data import get_interpolated_indices


class PredictByXGBoost(PredictSetup):
    name = 'XGBoost'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float = 0.7, n_clusters: int = 5) -> None:
        super().__init__(city, prediction_length, train_size)
        self.model_dir = os.path.join(os.path.dirname(__file__), 'XGBoostModels')
        os.makedirs(self.model_dir, exist_ok=True)
        self.models = {}
        self.cluster_model = None
        self.station_clusters = None
        self.n_clusters = n_clusters

    def train(self: Self) -> None:
        df = self.train_dataset.copy()

        correlation_matrix = df.corr().values

        self.cluster_model = KMeans(n_clusters=self.n_clusters, random_state=42)
        clusters = self.cluster_model.fit_predict(correlation_matrix)
        self.station_clusters = {station: cluster for station, cluster in zip(df.columns, clusters)}

        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_xgboost_model.pkl')
            
            if os.path.exists(model_path):
                model = joblib.load(model_path)
            else:
                df_station = df[[station]].reset_index()
                df_station.rename(columns={'date': 'ds', station: 'y'}, inplace=True)
                
                # Retirer les données interpolées
                interpolated_indices = get_interpolated_indices(df_station['y'])
                df_station = df_station.drop(interpolated_indices)

                # Ajout des caractéristiques temporelles
                df_station['hour'] = df_station['ds'].dt.hour
                df_station['day_of_week'] = df_station['ds'].dt.dayofweek
                df_station['day_of_month'] = df_station['ds'].dt.day
                df_station['month'] = df_station['ds'].dt.month
                df_station['is_weekend'] = df_station['ds'].dt.dayofweek >= 5
                df_station['is_sunday'] = df_station['ds'].dt.dayofweek == 6
                df_station['station_cluster'] = self.station_clusters[station]
                # On rajoute du lagging avec un décalage qui correspond à la longueur de la prédiction (prediction_length) pour éviter le data leakage
                df_station['y_lag'] = df_station['y'].shift(self.prediction_length)

                X = df_station[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'is_sunday', 'station_cluster', 'y_lag']]
                y = df_station['y']

                model = xgb.XGBRegressor(n_estimators=50, max_depth=9, learning_rate=0.05)
                model.fit(X, y)


                joblib.dump(model, model_path, compress=5)
            
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
        future['station_cluster'] = self.station_clusters[selected_station]
        future['y_lag'] = data.values[-self.prediction_length:]

        X_future = future[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'is_sunday', 'station_cluster', 'y_lag']]

        predictions = model.predict(X_future)

        predictions = predictions.clip(0, 1)

        serie = pd.Series(predictions, index=data_index, name=PredictByXGBoost.name)
        return serie
