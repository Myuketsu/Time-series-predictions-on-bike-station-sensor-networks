import dash_leaflet as dl
from data.city.load_cities import City

def get_markers(city: City) -> list[dl.Marker]:
    return [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(row['code_name']), 
            ],
            id={"type": "marker", "code_name": row['code_name']},
            n_clicks=0
        ) for _, row in city.df_coordinates.iterrows()
    ]

def viewport_map(city: City, id: str):
    return dl.Map(
        [
            dl.TileLayer(),  # OpenStreetMap par défaut
        ] + get_markers(city),
        center=city.centroid,
        bounds=city.bounds,
        maxBounds=city.bounds,
        zoomControl=False,
        scrollWheelZoom=True,
        dragging=True,
        attributionControl=False,
        doubleClickZoom=False,
        zoomSnap=0.3,
        minZoom=12.4,
        id=id
    )