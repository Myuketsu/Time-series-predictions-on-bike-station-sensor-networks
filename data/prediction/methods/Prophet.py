import os
import joblib
import pandas as pd
from typing import Self
from prophet import Prophet
from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup

class PredictByProphet(PredictSetup):
    name = 'Prophet'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float=0.7) -> None:
        super().__init__(city, prediction_length, train_size)
        self.model_dir = os.path.join(os.path.dirname(__file__), 'ProphetModels')
        os.makedirs(self.model_dir, exist_ok=True)
        self.models = {}

    def train(self: Self) -> None:
        df = self.train_dataset.copy()
        
        for station in df.columns:
            model_path = os.path.join(self.model_dir, f'{station}_prophet_model.pkl')
            
            if os.path.exists(model_path):
                # Charger le modèle s'il existe déjà
                model = joblib.load(model_path)
            else:
                # Entraîner le modèle s'il n'existe pas
                df_station = df[[station]].reset_index()
                df_station.rename(columns={'date': 'ds', station: 'y'}, inplace=True)
                
                model = Prophet(
                    weekly_seasonality=True,
                    daily_seasonality=True,
                    seasonality_mode='multiplicative',
                    changepoint_prior_scale=0.05,
                )
                model.add_country_holidays(country_name='FR')
                model.fit(df_station)
                
                # Sauvegarder le modèle
                joblib.dump(model, model_path)
                
            self.models[station] = model

    def predict(self: Self, selected_station: str, data: pd.Series) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f"Model for station {selected_station} not found.")
        
        model = self.models[selected_station]
        
        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        future = pd.DataFrame({'ds': data_index})
        
        forecast = model.predict(future)
        predictions = forecast['yhat'].values
        
        # Contrainte des valeurs entre 0 et 1
        predictions = predictions.clip(0, 1)
        
        serie = pd.Series(predictions, index=data_index, name=PredictByProphet.name)
        
        return serie

