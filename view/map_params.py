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