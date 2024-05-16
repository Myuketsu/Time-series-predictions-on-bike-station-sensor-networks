import os
import joblib
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Self
from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup
from data.data import get_interpolated_indices

class PredictByRidgeAndRandomForest(PredictSetup):
    name = 'RidgeAndRandomForest'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float=0.7, n_clusters: int = 5) -> None:
        super().__init__(city, prediction_length, train_size)
        self.model_dir = os.path.join(os.path.dirname(__file__), 'RidgeRandomForestModels')
        os.makedirs(self.model_dir, exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.cluster_model = None
        self.station_clusters = None
        self.n_clusters = n_clusters

    def train(self: Self) -> None:
        df = self.train_dataset.copy()

        # Calculer la matrice de corrélation des stations
        correlation_matrix = df.corr().values

        # Effectuer le clustering des stations basé sur la matrice de corrélation
        self.cluster_model = KMeans(n_clusters=self.n_clusters, random_state=42)
        clusters = self.cluster_model.fit_predict(correlation_matrix)
        self.station_clusters = {station: cluster for station, cluster in zip(df.columns, clusters)}

        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_ridge_randomforest_model.pkl')
            scaler_path = os.path.join(self.model_dir, f'{station}_scaler.pkl')
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                # Charger le modèle et le scaler s'ils existent déjà
                ridge_model, rf_model = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
            else:
                # Entraîner le modèle s'ils n'existent pas
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

                X = df_station[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'is_sunday', 'station_cluster']]
                y = df_station['y']
                
                # Normaliser les caractéristiques
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Entraîner les modèles
                ridge_model = Ridge().fit(X_scaled, y)
                rf_model = RandomForestRegressor(n_estimators=100, max_depth = 1000, criterion='friedman_mse').fit(X_scaled, y)
                
                # Sauvegarder les modèles
                joblib.dump((ridge_model, rf_model), model_path)
                joblib.dump(scaler, scaler_path)
            
            self.models[station] = (ridge_model, rf_model)
            self.scalers[station] = scaler

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f"Model for station {selected_station} not found.")
        
        ridge_model, rf_model = self.models[selected_station]
        scaler = self.scalers[selected_station]
        
        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        future = pd.DataFrame({'ds': data_index})
        
        future['hour'] = future['ds'].dt.hour
        future['day_of_week'] = future['ds'].dt.dayofweek
        future['day_of_month'] = future['ds'].dt.day
        future['month'] = future['ds'].dt.month
        future['is_weekend'] = future['ds'].dt.dayofweek >= 5
        future['is_sunday'] = future['ds'].dt.dayofweek == 6
        future['station_cluster'] = self.station_clusters[selected_station]
        
        # Normaliser les caractéristiques
        X_future_scaled = scaler.transform(future[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'is_sunday', 'station_cluster']])
        
        # Prédictions basées sur Ridge et Random Forest
        ridge_predictions = ridge_model.predict(X_future_scaled)
        rf_predictions = rf_model.predict(X_future_scaled)
        
        # Moyenne des deux prédictions pour plus de robustesse
        future['prediction'] = (ridge_predictions + rf_predictions) / 2
        
        serie = pd.Series(future['prediction'].values, index=data_index, name=PredictByRidgeAndRandomForest.name)
        
        return serie
