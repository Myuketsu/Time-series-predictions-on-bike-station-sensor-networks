import pandas as pd
import numpy as np
import xgboost as xgb

from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup

class PredictByXGBoost(PredictSetup):
    name = 'XGBoost'

    def __init__(self, city: City, prediction_length: int, train_size: float = 0.7, params=None):
        super().__init__(city, prediction_length, train_size)
        self.params = params or {
            'max_depth': 8,
            'eta': 0.15,
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse',
            'subsample': 0.9,
            'min_child_weight': 3,
        }
        self.models = {}

    def create_features(self, df):
        """ Ajoute des caractéristiques basées sur l'index de date/heure. """
        df = df.copy()
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        return df

    def train(self):
        df = self.create_features(self.train_dataset)
        feature_columns = ['hour', 'day_of_week', 'day_of_month', 'month']

        # Création de modèles XGBoost pour chaque station
        for station in self.train_dataset.columns: 
            train_x = df[feature_columns]
            train_y = df[station]
            # On donne plus de poids aux données récentes
            weights = np.linspace(0.1, 1, len(train_y))            
            dtrain = xgb.DMatrix(train_x, label=train_y, weight=weights)
            self.models[station] = xgb.train(self.params, dtrain, num_boost_round=100)

    def predict(self, selected_station):
        pred_index = self.get_DatetimeIndex_from_Series(self.train_dataset[selected_station], self.prediction_length)
        df = self.create_features(pd.DataFrame(index=pred_index))

        model = self.models.get(selected_station)
        if model:
            dtest = xgb.DMatrix(df)
            prediction = model.predict(dtest)
            return pd.Series(prediction, index=pred_index, name=selected_station)
        else:
            return pd.Series([], index=pred_index, name=selected_station)
