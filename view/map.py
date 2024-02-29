import dash_leaflet as dl
from data.city.load_cities import City

ICONS = {
    'red': {
        'iconUrl': './assets/pictures/marker/marker-icon-red.png',
        'shadowUrl': './assets/pictures/marker/marker-icon-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    },
    'gold': {
        'iconUrl': './assets/pictures/marker/marker-icon-gold.png',
        'shadowUrl': './assets/pictures/marker/marker-icon-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    },
    'blue': None
}

def get_markers(city: City, markers_distribution: dict[int, str]={}, default_markers_colors: str='blue') -> list[dl.Marker]:
    return [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            children=[dl.Tooltip(row['code_name'])],
            id={'type': 'marker', 'code_name': row['code_name'], 'index': index},
            icon=ICONS[markers_distribution.get(index, default_markers_colors)],
            n_clicks=0
        ) for index, row in city.df_coordinates.iterrows()
    ]

def get_edit_control():
    return dl.FeatureGroup(
        [
            dl.EditControl(
                id='edit_control',
                draw={
                    'circle': False,
                    'polyline': False,
                    'rectangle': False,
                    'marker': False,
                    'circlemarker': False,
                },
                edit={'edit': False},
                geojson={'type': 'FeatureCollection', 'features': []}
            )
        ]
    )

def get_map_children(city: City, markers_distribution: list[list[dict]]={}, has_edit_control: bool=False, default_markers_colors: str='blue'):
    children = [dl.TileLayer()] # OpenStreetMap par défaut
    if has_edit_control:
        children += [get_edit_control()]
    return children + get_markers(city, markers_distribution, default_markers_colors)

def viewport_map(city: City, id: str, has_edit_control: bool=False, default_markers_colors: str='blue'):
    return dl.Map(
        children=get_map_children(
            city=city,
            has_edit_control=has_edit_control,
            default_markers_colors=default_markers_colors
        ),
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
        preferCanvas=True,
        id=id
    )