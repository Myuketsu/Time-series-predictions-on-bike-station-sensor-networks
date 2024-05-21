import pandas as pd

from typing import Self, Any

from data.city.load_cities import City
from data.prediction.prediction_setup import PredictSetup

class PredictByMean(PredictSetup):
    name = 'Moyenne'

    def __init__(self: Self, city: City, prediction_length: int, train_size: float=0.7) -> None:
        super().__init__(city, prediction_length, train_size)

    def train(self: Self) -> None:
        df = self.train_dataset.copy()
        df['hours'] = df.index.hour
        df['days'] = pd.Categorical(
            values=df.index.day_name(),
            categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            ordered=True
        )
        
        self.model: pd.DataFrame = df.groupby(['days', 'hours'], observed=False).mean()

    def predict(self: Self, selected_stations: str, data: pd.Series) -> pd.Series:
        serie = self.model[selected_stations]
        serie.name = PredictByMean.name

        # On doit ré-indexer les données dans l'ordre des données passé en paramètre
        # ex: la semaine de données commence par Vendredi, il faut décaler toutes les valeurs de la prédiction (Car commence Lundi 00:00) 
        # pour que la première soit celle de Vendredi 00:00
        data_index = PredictSetup.get_DatetimeIndex_from_Series(data, self.prediction_length)
        tmp_data_index = data_index.to_series().copy().to_frame()
        tmp_data_index['days'] = tmp_data_index.index.day_name()
        tmp_data_index['hours'] = tmp_data_index.index.hour
        
        return serie.reindex_like(tmp_data_index.set_index(['days', 'hours'])).set_axis(data_index)