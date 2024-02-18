import pandas as pd
from os import listdir
from os.path import isdir

CITIES_PATH = './data/city'
BASE_FILENAME_HOUR = 'X_hour_'
BASE_FILENAME_COORDINATES = 'coordinates_'

class City:
    def __init__(self, name: str, df_hours: pd.DataFrame, df_coordinates: pd.DataFrame) -> None:
        self.__name = name
        self.__df_hours = df_hours
        self.__df_coordinates = df_coordinates
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def centroid(self) -> list[int]:
        return self.__df_coordinates[['latitude', 'longitude']].mean().to_list()
    
    @property
    def df_hours(self) -> pd.DataFrame:
        return self.__df_hours.copy()
    
    @property
    def df_coordinates(self) -> pd.DataFrame:
        return self.__df_coordinates.copy()

CITIES: list[City] = []
for city in listdir(CITIES_PATH):
    if city[-3:] == '.py' or city == '__pycache__':
        continue

    CITIES.append(
        City(
            name=city,
            df_hours=pd.read_csv(f'{CITIES_PATH}/{city}/{BASE_FILENAME_HOUR}{city.lower()}.csv'),
            df_coordinates=pd.read_csv(f'{CITIES_PATH}/{city}/{BASE_FILENAME_COORDINATES}{city.lower()}.csv')
        )
    )