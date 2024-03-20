import dash_leaflet as dl
from data.city.load_cities import City
from data.data import calculate_correlations

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

def get_map_children(city: City, markers_distribution: list[list[dict]]={}, has_edit_control: bool=False, default_markers_colors: str='blue', circle_mode: bool=False, selected_station: str=None):
    children = [dl.TileLayer()] # OpenStreetMap par défaut
    if has_edit_control:
        children += [get_edit_control()]
    if circle_mode and selected_station:
        children += get_correlation_markers(city, selected_station)
    else:
        children += get_markers(city, markers_distribution, default_markers_colors)
    return children

def viewport_map(city: City, id: str, has_edit_control: bool=False, default_markers_colors: str='blue', circle_mode: bool=False, selected_station: str=None):
    return dl.Map(
        children=get_map_children(
            city=city,
            has_edit_control=has_edit_control,
            default_markers_colors=default_markers_colors,
            circle_mode=circle_mode,
            selected_station=selected_station
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


def get_correlation_markers(city: City, selected_station: str) -> list[dl.CircleMarker]:
    correlations = calculate_correlations(city, selected_station)
    
    def correlation_color(correlation_value):
        if round(correlation_value, 3) == 1.0:
            return 'yellow'
        if correlation_value < -0.3:
            return 'red'
        elif correlation_value > 0.3:
            return 'green'
        return 'blue'
    
    return [
        dl.CircleMarker(
            center=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(f"{row['code_name']}: Corrélation {correlations[row['code_name']]:.2f}")
            ],
            id={'type': 'circle_marker', 'code_name': row['code_name'], 'index': index},
            radius=8,  # Vous pouvez ajuster la taille du cercle ici
            color='black',  # Couleur du contour
            fill=True,
            fillColor=correlation_color(correlations[row['code_name']]),  # Couleur de remplissage basée sur la corrélation
            fillOpacity=0.7,  # Transparence du remplissage
            stroke=True,
            weight=1,  # Épaisseur du contour
            n_clicks=0
        ) for index, row in city.df_coordinates.iterrows()
    ]

