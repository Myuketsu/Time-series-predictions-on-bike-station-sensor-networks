import dash_leaflet as dl
from data.city.load_cities import City

def get_markers(city: City) -> list[dl.Marker]:
    return [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(row['code_name']), 
            ],
            id={"type": "marker", "code_name": row['code_name']}
        ) for _, row in city.df_coordinates.iterrows()
    ]