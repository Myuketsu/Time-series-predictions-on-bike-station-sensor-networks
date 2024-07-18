import pandas as pd
import xgboost as xgb
from typing import Self
from sklearn.decomposition import PCA
from data.city.load_cities import City
from data.prediction.forecast_model import ForecastModel, PATH_MODEL
from data.data import get_interpolated_indices
from os import makedirs

class XGBoostPCA(ForecastModel):
    name = 'XGBoostPCA'

    def __init__(self: Self, city: City, train_size: float = 0.7, n_components: int = 4) -> None:
        super().__init__(city, train_size)
        makedirs(f'{PATH_MODEL}{self.name}', exist_ok=True)
        self.models = {}
        self.n_components = n_components

    def train(self: Self) -> None:
        df = self.train_dataset.copy()

        for station in df.columns:
            try:
                model_dict = self.load_model(station)
                model = model_dict['model']
                pca = model_dict['pca']
            except FileNotFoundError:
                interpolated_indices = get_interpolated_indices(df[station], output_type='mask')
                df_filtered = df.drop(index=interpolated_indices)
                
                df_X = ForecastModel.create_features_from_date(df_filtered.index.to_series())
                df_y = df_filtered[station]

                pca = PCA(n_components=self.n_components)
                X_pca = pca.fit_transform(df_X)

                model = xgb.XGBRegressor(n_estimators=100, max_depth=10, learning_rate=0.1)
                model.fit(X_pca, df_y)

                model_dict = {'model': model, 'pca': pca}
                self.save_model(model_dict, station)
            
            self.models[station] = model_dict

    def predict(self: Self, selected_station: str, data: pd.Series, forecast_length: int) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f'Model for station {selected_station} not found.')

        model_dict = self.models[selected_station]
        model = model_dict['model']
        pca = model_dict['pca']

        data_index = ForecastModel.get_DatetimeIndex_forecasting(data, forecast_length)
        df_X_future = ForecastModel.create_features_from_date(data_index.to_series())

        X_future_pca = pca.transform(df_X_future)
        predictions = model.predict(X_future_pca)
        predictions = predictions.clip(0, 1)

        return pd.Series(predictions, index=data_index, name=self.name)
