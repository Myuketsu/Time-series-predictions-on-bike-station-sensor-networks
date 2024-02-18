import dash_leaflet as dl
from data.city.load_cities import City

def get_markers(city: City) -> list[dl.Marker]:
    return [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(row['Unnamed: 0']), 
            ],
            id={"type": "marker", "index": row['Unnamed: 0']}  
        ) for _, row in city.df_coordinates.iterrows()
    ]


def get_bounds(city: City, tolerance: float=0.1) -> list[float]:
    min_coordinate = [city.df_coordinates['latitude'].min(), city.df_coordinates['longitude'].min()]
    max_coordinate = [city.df_coordinates['latitude'].max(), city.df_coordinates['longitude'].max()]

    lat_difference = max_coordinate[0] - min_coordinate[0]
    long_difference = max_coordinate[1] - min_coordinate[1]

    return [
        [min_coordinate[0] - lat_difference * tolerance, min_coordinate[1] - long_difference * tolerance],
        [max_coordinate[0] + lat_difference * tolerance, max_coordinate[1] + long_difference * tolerance],
    ]