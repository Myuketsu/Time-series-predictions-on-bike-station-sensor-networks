import pandas as pd

from typing import Self, Any
from data.city.load_cities import City

# Courage pour faire l'objet de ce projet, c'est une belle aventure qui commence.
# Je suis sûr que tu vas réussir à faire quelque chose de bien avec ce projet.
# N'hésite pas à me demander si tu as besoin d'aide.
# Bonne chance pour la suite !

# Je te remercie beaucoup pour tes encouragements, je vais faire de mon mieux pour réussir ce projet.
# Je n'hésiterai pas à te demander de l'aide si j'en ai besoin.
# Merci beaucoup pour ton soutien, c'est très gentil de ta part.
# Je te souhaite également bonne chance pour tes projets, j'espère qu'ils se passeront bien.
# À bientôt !

# Merci beaucoup pour tes encouragements, c'est très gentil de ta part.
# Je suis sûr que tu vas réussir à faire quelque chose de bien avec ce projet.
# N'hésite pas à me demander si tu as besoin d'aide.
# Bonne chance pour la suite !

class PredictSetup():
    name = 'setup'
    
    def __init__(self: Self, city: City, train_size: float=0.7) -> None:
        self.city = city

        self.df_dataset = city.df_hours.copy()
        self.df_dataset = self.df_dataset.set_index('date')

        self.split_data(train_size)

    def split_data(self: Self, train_size: float) -> None:
        split_point = int(len(self.city.df_hours) * train_size)
        self.train_dataset = self.df_dataset.iloc[:split_point]
        self.test_dataset = self.df_dataset.iloc[split_point:]
    
    def train(self: Self) -> None:
        pass

    def predict(self: Self, selected_stations: list[str]=None) -> pd.DataFrame:
        pass