import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error

from typing import Self, Any
from data.city.load_cities import City
from data.data import get_interpolated_indices

from abc import ABC, abstractmethod

class ForecastModel(ABC):
    name = 'BaseModel'
    
    def __init__(self: Self, city: City, train_size: float=0.7) -> None:
        self.city = city
        self.train_size = train_size

        self.df_dataset = city.df_hours.copy()
        self.df_dataset = self.df_dataset.set_index('date')
        
        self.split_data()

    def split_data(self: Self) -> None:
        split_point = int(len(self.city.df_hours) * self.train_size)
        self.train_dataset = self.df_dataset.iloc[:split_point]
        self.test_dataset = self.df_dataset.iloc[split_point:]

    def train_test_split(self: Self, df_X: pd.DataFrame, serie_y: pd.Series, random_state: int=None) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        X_train, X_test, y_train, y_test = train_test_split(df_X, serie_y, train_size=self.train_size, random_state=random_state, shuffle=False)
        X_train: pd.DataFrame = X_train
        X_test: pd.DataFrame = X_test
        y_train: pd.Series = y_train
        y_test: pd.Series = y_test
        return X_train, X_test, y_train, y_test
    
    def save_model(self: Self, model: Any, station_name: str, compress: int=3) -> None:
        joblib.dump(model, f'./{self.name}/{station_name}.pkl', compress=compress)

    def load_model(self: Self, station_name: str) -> Any:
        return joblib.load(f'./{self.name}/{station_name}.pkl')

    @abstractmethod
    def train(self: Self) -> None:
        pass

    @abstractmethod
    def predict(self: Self, selected_station: str, data: pd.Series, forecast_length: int) -> pd.Series: # DOIT RETOURNER UNE SERIE !
        pass
    
    @staticmethod
    def create_features_from_date(date_serie: pd.Series) -> pd.DataFrame:
        df_X = pd.DataFrame()
        df_X['hour'] = date_serie.dt.hour.astype('uint8')
        df_X['day_of_week'] = date_serie.dt.dayofweek.astype('uint8')
        df_X['day_of_month'] = date_serie.dt.day.astype('uint8')
        df_X['is_weekend'] = (date_serie.dt.dayofweek >= 5).astype('uint8')
        df_X['is_sunday'] = (date_serie.dt.dayofweek == 6).astype('uint8')
        return df_X

    @staticmethod
    def get_DatetimeIndex_forecasting(serie: pd.Series, prediction_length: int) -> pd.DatetimeIndex:
        return pd.date_range(serie.index[-1], periods=prediction_length, freq='1h', inclusive='left')
    
    @staticmethod
    def get_metrics(predicted: pd.Series, reality: pd.Series, metrics: tuple[str] | str='all', exclude_interpolation_weights: bool=True) -> dict[str, float]:
        sample_weight = pd.Series(1, reality.index)
        if exclude_interpolation_weights:
            sample_weight[get_interpolated_indices(reality)] = 0

        metrics_dict: dict[str, float] = {}
        all_metric = isinstance(metrics, str) and metrics == 'all'
        if all_metric or (isinstance(metrics, tuple) and 'mse' in metrics):
            metrics_dict['mse'] = mean_squared_error(reality, predicted, sample_weight=sample_weight)
        if all_metric or (isinstance(metrics, tuple) and 'mae' in metrics):
            metrics_dict['mae'] = mean_absolute_error(reality, predicted, sample_weight=sample_weight)
        return metrics_dict