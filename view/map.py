import dash_leaflet as dl
import numpy as np

import view.color as color
from data.city.load_cities import City
from data.data import calculate_correlations, get_acp

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
                    'circlemarker': False
                },
                edit={'edit': False},
                geojson={'type': 'FeatureCollection', 'features': []}
            )
        ]
    )

def get_colorbar(colorbar_range: tuple[int]) -> dl.Colorbar:
    return dl.Colorbar(
        colorscale=['blue', 'yellow'],
        width=20,
        height=200,
        max=colorbar_range[1],
        min=colorbar_range[0],
        position='topright',
        nTicks=5,
        id='colorbar'
    )

def get_map_children(city: City, markers_distribution: list[list[dict]]={}, has_edit_control: bool=False,
                     default_markers_colors: str='blue', circle_mode: bool=False, selected_station: str=None,
                     acp_mode: bool=False, index: int=0, has_colorbar: bool=False, colorbar_range: tuple[int]=(-1, 1)):
    children = [dl.TileLayer()] # OpenStreetMap par défaut
    if has_edit_control:
        children += [get_edit_control()]
    if circle_mode and selected_station:
        children += get_correlation_markers(city, selected_station)
    elif acp_mode:
        _, pca, _ = get_acp(city)
        children += [get_colorbar((np.min(pca.components_[index]), np.max(pca.components_[index])))]
        children += get_acp_markers(city, index)
        return children
    else:
        children += get_markers(city, markers_distribution, default_markers_colors)
    
    if has_colorbar:
        children += [get_colorbar(colorbar_range)]
    return children

def viewport_map(city: City, id: str, has_edit_control: bool=False, default_markers_colors: str='blue',
                 circle_mode: bool=False, selected_station: str=None, acp_mode: bool=False, index: int=0, has_colorbar: bool=False,
                 colorbar_range: tuple[int]=(-1, 1)):
    return dl.Map(
        children=get_map_children(
            city=city,
            has_edit_control=has_edit_control,
            default_markers_colors=default_markers_colors,
            circle_mode=circle_mode,
            selected_station=selected_station,
            acp_mode=acp_mode,
            index=index,
            has_colorbar=has_colorbar,
            colorbar_range=colorbar_range
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
    
    return [
        dl.CircleMarker(
            center=[row['latitude'], row['longitude']],
            children=[
                dl.Tooltip(f"{row['code_name']}: Corrélation {correlations[row['code_name']]:.2f}")
            ],
            id={'type': 'circle_marker', 'code_name': row['code_name'], 'index': index},
            radius=8,  
            color='black',  
            fill=True,
            fillColor=color.find_color_between(color.normalize_value(correlations[row['code_name']], -1, 1)),  # Couleur de remplissage basée sur la corrélation
            fillOpacity=0.85,  
            stroke=True,
            weight=1, 
            n_clicks=0,
            
        ) for index, row in city.df_coordinates.iterrows()
    ]


def get_acp_markers(city, index):
    _, pca, _ = get_acp(city)
    
    pca_values = pca.components_[index]
    normalized_value: np.ndarray = color.normalize_value(pca_values)
    
    markers = []
    for i, row in city.df_coordinates.iterrows():
        # color = px.colors.sample_colorscale(color_scale, norm_pca_values[i])[0]
        current_color = color.find_color_between(normalized_value[i])
        
        marker = dl.CircleMarker(
            center=(row['latitude'], row['longitude']),
            children=[
                dl.Tooltip(f"{row['code_name']}: {pca_values[i]:.3f}")
            ],
            radius=8,  
            color='black',
            fill=True,
            fillColor=current_color,
            fillOpacity=0.85,  
            weight=1,
            id={"type": "pca_marker", "index": i}
        )
        markers.append(marker)
    
    return markers