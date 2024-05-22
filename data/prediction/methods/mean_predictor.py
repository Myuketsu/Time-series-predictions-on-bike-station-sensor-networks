import pandas as pd

from typing import Self, Any

from data.city.load_cities import City
from data.prediction.forecast_model import ForecastModel

class PredictByMean(ForecastModel):
    name = 'Moyenne'

    def __init__(self: Self, city: City, train_size: float=0.7) -> None:
        super().__init__(city, train_size)

    def train(self: Self) -> None:
        df = self.train_dataset.copy()
        df['hours'] = df.index.hour
        df['days'] = pd.Categorical(
            values=df.index.day_name(),
            categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            ordered=True
        )
        
        self.model: pd.DataFrame = df.groupby(['days', 'hours'], observed=False).mean()

    def predict(self: Self, selected_station: str, data: pd.Series, forecast_length: int) -> pd.Series:
        serie = self.model[selected_station]
        serie.name = PredictByMean.name

        data_index = ForecastModel.get_DatetimeIndex_forecasting(data, forecast_length)
        tmp_data_index = data_index.to_series().copy().to_frame()
        tmp_data_index['days'] = tmp_data_index.index.day_name()
        tmp_data_index['hours'] = tmp_data_index.index.hour
        
        return serie.reindex_like(tmp_data_index.set_index(['days', 'hours'])).set_axis(data_index)