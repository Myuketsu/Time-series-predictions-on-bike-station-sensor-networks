import os
import joblib
import pandas as pd
import xgboost as xgb
import numpy as np
from typing import Self
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup
from data.data import get_interpolated_indices

class PredictByXGBoostWithPCA(PredictSetup):
    name = 'XGBoostWithPCA'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float=0.7, n_clusters: int = 5, n_components: int = 5) -> None:
        super().__init__(city, prediction_length, train_size)
        self.model_dir = os.path.join(os.path.dirname(__file__), 'XGBoostPCAModels')
        os.makedirs(self.model_dir, exist_ok=True)
        self.models = {}
        self.n_clusters = n_clusters
        self.n_components = n_components

    def train(self: Self) -> None:
        df = self.train_dataset.copy()

        # Calculer la matrice de corrélation des stations
        correlation_matrix = df.corr().values

        # Effectuer le clustering des stations basé sur la matrice de corrélation
        self.cluster_model = KMeans(n_clusters=self.n_clusters, random_state=42)
        clusters = self.cluster_model.fit_predict(correlation_matrix)
        self.station_clusters = {station: cluster for station, cluster in zip(df.columns, clusters)}

        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_xgboost_pca_model.pkl')
            
            if os.path.exists(model_path):
                # Charger le modèle s'il existe déjà
                model_dict = joblib.load(model_path)
                model = model_dict['model']
                scaler = model_dict['scaler']
                pca = model_dict['pca']
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
                df_station['station_cluster'] = self.station_clusters[station]

                X = df_station[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'station_cluster']]
                y = df_station['y']
                
                # Normaliser les caractéristiques
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Appliquer l'ACP
                pca = PCA(n_components=self.n_components)
                X_pca = pca.fit_transform(X_scaled)
                
                # Entraîner le modèle XGBoost
                model = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1)
                model.fit(X_pca, y)
                
                # Sauvegarder le modèle, le scaler et le modèle PCA dans un seul fichier
                model_dict = {'model': model, 'scaler': scaler, 'pca': pca}
                joblib.dump(model_dict, model_path)
            
            self.models[station] = model_dict

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f"Model for station {selected_station} not found.")
        
        model_dict = self.models[selected_station]
        model = model_dict['model']
        scaler = model_dict['scaler']
        pca = model_dict['pca']
        
        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        future = pd.DataFrame({'ds': data_index})
        
        future['hour'] = future['ds'].dt.hour
        future['day_of_week'] = future['ds'].dt.dayofweek
        future['day_of_month'] = future['ds'].dt.day
        future['month'] = future['ds'].dt.month
        future['is_weekend'] = future['ds'].dt.dayofweek >= 5
        future['station_cluster'] = self.station_clusters[selected_station]
        
        # Normaliser les caractéristiques
        X_future_scaled = scaler.transform(future[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'station_cluster']])
        
        # Appliquer l'ACP
        X_future_pca = pca.transform(X_future_scaled)
        
        # Prédictions basées sur XGBoost
        predictions = model.predict(X_future_pca)
        
        # Contrainte des valeurs entre 0 et 1
        predictions = predictions.clip(0, 1)
        
        serie = pd.Series(predictions, index=data_index, name=PredictByXGBoostWithPCA.name)
        
        return serie

