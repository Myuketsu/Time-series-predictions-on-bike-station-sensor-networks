import dash_leaflet as dl
from data.city.load_cities import City

ICONS_MAKRERS = {
    'red': {
        'iconUrl': './assets/pictures/marker/marker-icon-red.png',
        'shadowUrl': './assets/pictures/marker/marker-icon-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    },
    'blue': None
}

ICONS_DIV_MAKRERS = {
    'red': dict(
        className='div_marker_map_red',
        iconSize=[17, 17]
    ),
    'blue': dict(
        className='div_marker_map_blue',
        iconSize=[17, 17]
    ),
}

def get_markers(city: City, distribution: dict[int, str]=[]) -> list[dl.Marker]:
    return [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            children=[dl.Tooltip(row['code_name'])],
            id={'type': 'marker', 'code_name': row['code_name'], 'index': index},
            icon=ICONS_MAKRERS[distribution.get(index, 'blue')],
            n_clicks=0
        ) for index, row in city.df_coordinates.iterrows()
    ]

def get_div_markers(city: City, default_markers_colors: str='blue') -> list[dl.Marker]:
    return [
        dl.DivMarker(
            position=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(row['code_name']), 
            ],
            id={'type': 'marker', 'code_name': row['code_name'], 'index': index},
            n_clicks=0,
            iconOptions=ICONS_DIV_MAKRERS[default_markers_colors]
        ) for index, row in city.df_coordinates.iterrows()
    ]

def get_map_children(city: City, distribution: list[list[dict]]=None, default_markers_colors: str='blue'):
    children = [dl.TileLayer()]
    for index, row in city.df_coordinates.iterrows():
        children.append(
            dl.Marker(
                position=[row['latitude'], row['longitude']],
                children=[dl.Tooltip(row['code_name'])],
                id={'type': 'marker', 'code_name': row['code_name'], 'index': index},
                icon=ICONS_MAKRERS[default_markers_colors],
                n_clicks=0
            )
        )

def viewport_map(city: City, id: str, use_img_icon: bool=True, default_markers_colors: str='blue'):
    if use_img_icon:
        markers = get_markers(city, default_markers_colors)
    else:
        markers = get_div_markers(city, default_markers_colors)
    return dl.Map(
        [
            dl.TileLayer(),  # OpenStreetMap par défaut
        ] + markers,
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