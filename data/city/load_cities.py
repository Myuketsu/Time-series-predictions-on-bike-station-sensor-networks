import pandas as pd
from os import listdir
from os.path import isdir

CITIES_PATH = './data/city'
DATE_RANGE = ('04-01-2016', '10-31-2016')
BASE_FILENAME_HOUR = 'X_hour_'
BASE_FILENAME_COORDINATES = 'coordinates_'

class City:
    def __init__(self, name: str, df_hours: pd.DataFrame, df_coordinates: pd.DataFrame) -> None:
        self.__name = name

        self.__df_hours = df_hours
        self.__df_hours = pd.concat( # On rempli le dernier jours entièrement avec des 0.0
            [self.__df_hours, pd.DataFrame(index=range(self.__df_hours.index[-1] + 1, self.__df_hours.index[-1] + (24 - len(self.__df_hours) % 24 + 1)))]
        ).fillna(0.0)
        self.__df_hours['date'] = pd.date_range(*DATE_RANGE, freq='1h')[:len(self.__df_hours)]

        self.__df_coordinates = df_coordinates
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def centroid(self) -> list[int]:
        return self.__df_coordinates[['latitude', 'longitude']].mean().to_list()
    
    @property
    def bounds(self, tolerance: float=0.1) -> list[float]:
        min_coordinate = [self.__df_coordinates['latitude'].min(), self.__df_coordinates['longitude'].min()]
        max_coordinate = [self.__df_coordinates['latitude'].max(), self.__df_coordinates['longitude'].max()]

        lat_difference = max_coordinate[0] - min_coordinate[0]
        long_difference = max_coordinate[1] - min_coordinate[1]

        return [
            [min_coordinate[0] - lat_difference * tolerance, min_coordinate[1] - long_difference * tolerance],
            [max_coordinate[0] + lat_difference * tolerance, max_coordinate[1] + long_difference * tolerance],
        ]
    
    @property
    def df_hours(self) -> pd.DataFrame:
        return self.__df_hours.copy()
    
    @property
    def df_coordinates(self) -> pd.DataFrame:
        return self.__df_coordinates.copy()

CITIES: dict[str, City] = {}
for city in listdir(CITIES_PATH):
    if city[-3:] == '.py' or city == '__pycache__':
        continue

    CITIES[city] = City(
        name=city,
        df_hours=pd.read_csv(
            f'{CITIES_PATH}/{city}/{BASE_FILENAME_HOUR}{city.lower()}.csv',
            index_col=0
        ),
        df_coordinates=pd.read_csv(
            f'{CITIES_PATH}/{city}/{BASE_FILENAME_COORDINATES}{city.lower()}.csv',
        ).rename(columns={'Unnamed: 0': 'code_name'})
    )

CITY = CITIES['Toulouse']