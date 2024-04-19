import pandas as pd

from typing import Self, Any

from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup

class PredictByMean(PredictSetup):
    name = 'Moyenne'

    def __init__(self: Self, city: City, train_size: float=0.7) -> None:
        super().__init__(city, train_size)

    def train(self: Self) -> None:
        df = self.train_dataset.copy()
        df['days'] = df.index.day_name()
        df['hours'] = df.index.hour
        df['days'] = pd.Categorical(df['days'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ordered=True)

        self.model: pd.DataFrame = df.groupby(['days', 'hours'], observed=False).mean()

    def predict(self: Self, selected_stations: list[str]=None) -> pd.DataFrame:
        if selected_stations is None:
            selected_stations = self.model.columns

        return self.model[selected_stations]