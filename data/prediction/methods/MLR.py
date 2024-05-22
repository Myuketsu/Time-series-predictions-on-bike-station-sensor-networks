import pandas as pd
from sklearn.linear_model import LinearRegression
from typing import Self
from data.city.load_cities import City
from data.prediction.forecast_model import ForecastModel
from os import makedirs

class MultipleLinearRegression(ForecastModel):
    name = 'MultipleLinearRegression'

    def __init__(self: Self, city: City, train_size: float = 0.7) -> None:
        super().__init__(city, train_size)
        makedirs(self.name, exist_ok=True)
        self.models = {}

    def train(self: Self) -> None:
        df = self.train_dataset.copy()

        for station in df.columns:
            try:
                model_dict = self.load_model(station)
                model = model_dict['model']
                feature_order = model_dict['feature_order']
            except FileNotFoundError:
                df_X = ForecastModel.create_features_from_date(df.index.to_series())
                df_y = df[station]

                df_X = pd.get_dummies(df_X, columns=['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'is_sunday'], drop_first=True)

                feature_order = df_X.columns.tolist()

                model = LinearRegression()
                model.fit(df_X, df_y)

                model_dict = {'model': model, 'feature_order': feature_order}
                self.save_model(model_dict, station)

            self.models[station] = {'model': model, 'feature_order': feature_order}

    def predict(self: Self, selected_station: str, data: pd.Series, forecast_length: int) -> pd.Series:
        if selected_station not in self.models:
            raise ValueError(f'Model for station {selected_station} not found.')

        model_dict = self.models[selected_station]
        model = model_dict['model']
        feature_order = model_dict['feature_order']

        data_index = ForecastModel.get_DatetimeIndex_forecasting(data, forecast_length)
        future = ForecastModel.create_features_from_date(data_index.to_series())

        future = pd.get_dummies(future, columns=['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend', 'is_sunday'], drop_first=True)

        for col in feature_order:
            if col not in future.columns:
                future[col] = 0

        X_future = future[feature_order]

        predictions = model.predict(X_future).flatten()
        predictions = predictions.clip(0, 1)

        return pd.Series(predictions, index=data_index, name=self.name)
