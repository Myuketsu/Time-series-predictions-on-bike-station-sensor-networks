import pandas as pd

from typing import Self, Any
from data.city.load_cities import City


class PredictSetup():
    name = 'Setup'
    
    def __init__(self: Self, city: City, prediction_length: int, train_size: float=0.7) -> None:
        self.city = city
        self.prediction_length = prediction_length

        self.df_dataset = city.df_hours.copy()
        self.df_dataset = self.df_dataset.set_index('date')
        
        self.split_data(train_size)

    def split_data(self: Self, train_size: float) -> None:
        split_point = int(len(self.city.df_hours) * train_size)
        self.train_dataset = self.df_dataset.iloc[:split_point]
        self.test_dataset = self.df_dataset.iloc[split_point:]

    @staticmethod
    def get_DatetimeIndex_from_Series(serie: pd.Series, prediction_length: int) -> pd.DatetimeIndex:
        return pd.date_range(
            start=serie.index[-1] + pd.DateOffset(hours=1),
            end=serie.index[-1] + pd.DateOffset(hours=prediction_length),
            freq='h'
        )
    
    def train(self: Self) -> None:
        pass

    def predict(self: Self, selected_stations: str, data: pd.Series) -> pd.Series: # DOIT RETOURNER UNE SERIE !
        pass