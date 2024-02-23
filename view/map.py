import dash_leaflet as dl
from data.city.load_cities import City

ICONS = {
    'Red': {
        'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    },
    'Blue': None
}

def get_markers(city: City, default_markers_colors: str='Blue') -> list[dl.Marker]:
    return [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(row['code_name']), 
            ],
            id={'type': 'marker', 'code_name': row['code_name'], 'index': index},
            n_clicks=0,
            icon=ICONS[default_markers_colors]
        ) for index, row in city.df_coordinates.iterrows()
    ]

def viewport_map(city: City, id: str, default_markers_colors: str='Blue'):
    return dl.Map(
        [
            dl.TileLayer(),  # OpenStreetMap par défaut
        ] + get_markers(city, default_markers_colors),
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