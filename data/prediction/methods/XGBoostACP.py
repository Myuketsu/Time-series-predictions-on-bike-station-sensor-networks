import os
import joblib
import pandas as pd
import xgboost as xgb
import numpy as np
from typing import Self
from sklearn.decomposition import PCA
from data.city.load_cities import City
from data.prediction.forecast_model import PredictSetup
from data.data import get_interpolated_indices

class PredictByXGBoostWithPCA(PredictSetup):
    name = 'XGBoostWithPCA'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float=0.7, n_components: int = 5) -> None:
        super().__init__(city, prediction_length, train_size)
        self.model_dir = os.path.join(os.path.dirname(__file__), 'XGBoostPCAModels')
        os.makedirs(self.model_dir, exist_ok=True)
        self.models = {}
        self.n_components = n_components

    def train(self: Self) -> None:
        df = self.train_dataset.copy()
        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_xgboost_pca_model.pkl')
            
            if os.path.exists(model_path):
                # Charger le modèle s'il existe déjà
                model_dict = joblib.load(model_path)
                model = model_dict['model']
                pca = model_dict['pca']
            else:
                # Entraîner le modèle s'ils n'existent pas
                df_station = df[[station]].reset_index()
                df_station.rename(columns={'date': 'ds', station: 'y'}, inplace=True)
                

                # Ajout des caractéristiques temporelles
                df_station['hour'] = df_station['ds'].dt.hour
                df_station['day_of_week'] = df_station['ds'].dt.dayofweek
                df_station['day_of_month'] = df_station['ds'].dt.day
                df_station['month'] = df_station['ds'].dt.month
                df_station['is_weekend'] = df_station['ds'].dt.dayofweek >= 5

                X = df_station[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend']]
                y = df_station['y']
                
                # Appliquer l'ACP
                pca = PCA(n_components=self.n_components)
                X_pca = pca.fit_transform(X)
                
                model = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1)
                model.fit(X_pca, y)
                
                # Sauvegarder le modèle et le modèle PCA dans un seul fichier
                model_dict = {'model': model, 'pca': pca}
                joblib.dump(model_dict, model_path)
            
            self.models[station] = model_dict

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f"Model for station {selected_station} not found.")
        
        model_dict = self.models[selected_station]
        model = model_dict['model']
        pca = model_dict['pca']
        
        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        future = pd.DataFrame({'ds': data_index})
        
        future['hour'] = future['ds'].dt.hour
        future['day_of_week'] = future['ds'].dt.dayofweek
        future['day_of_month'] = future['ds'].dt.day
        future['month'] = future['ds'].dt.month
        future['is_weekend'] = future['ds'].dt.dayofweek >= 5
        
        X_future_pca = pca.transform(future[['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend']])
        
        predictions = model.predict(X_future_pca)
        
        predictions = predictions.clip(0, 1)
        
        serie = pd.Series(predictions, index=data_index, name=PredictByXGBoostWithPCA.name)
        
        return serie
