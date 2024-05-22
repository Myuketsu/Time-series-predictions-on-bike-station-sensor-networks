import dash_leaflet as dl
import numpy as np

import view.color as color
from data.city.load_cities import City

# --- MAP MANIPULATION ---

def viewport_map(city: City, id: str, has_edit_control: bool=False):
    """
    Generate a dynamic map viewport centered around the given city.

    Parameters
    ----------
    - city (City): An instance of the City class representing the city to be displayed on the map.
    - id (str): Identifier for the map component.
    - has_edit_control (bool, optional): Whether to include an edit control for the map. Default is False.

    Returns
    -------
    - dl.Map: A dynamic map viewport configured based on the provided parameters.

    Notes
    -----
    The map viewport is centered around the centroid of the city and constrained within its boundaries.
    Various interactive features such as zooming, scrolling, and dragging are configured based on default settings.
    """
    return dl.Map(
        children=[dl.TileLayer()] + ([get_edit_control()] if has_edit_control else []),
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

def add_to_children(map: dl.Map, children_to_add: list | tuple) -> None:
    """
    Add additional children components to a dynamic map.

    Parameters
    ----------
    - map (dl.Map): The dynamic map to which children components will be added.
    - children_to_add (list or tuple): A list or tuple of children components to be added to the map.

    Returns
    -------
    - None: This function does not return anything.

    Raises
    ------
    - ValueError: If 'children_to_add' is not a list or a tuple.

    Exemples
    --------
    >>> map: dl.Map = viewport_map(city=city, id='map')
    >>> children: list[dl.CircleMarker] = get_circle_markers(city=city)
    >>> add_to_children(map=map, children_to_add=children)
    """
    if not isinstance(children_to_add, list) and not isinstance(children_to_add, tuple):
        raise ValueError('"children_to_add" must be a list or a tuple!')
    map.children += children_to_add

def update_children(map_children: list, new_children: list | tuple) -> list:
    """
    Update the children components of a map by replacing specific types of components with a new list of components.

    Parameters
    ----------
    - map_children (list): The current list of children components of the map.
    - new_children (list or tuple): A list or tuple of new children components to add to the map.

    Returns
    -------
    - list: A list containing the updated children components, with specific types of components replaced by 'new_children'.

    Raises
    ------
    - ValueError: If 'new_children' is not a list or a tuple.

    Notes
    -----
    This function is used to update the children components of a map by replacing specific types of components
    (in this case, dl.CircleMarker components) with a new list of components specified in 'new_children'.
    It filters out dl.CircleMarker components from the current list of children components and appends the 'new_children'.
    """
    if not isinstance(new_children, list) and not isinstance(new_children, tuple):
        raise ValueError('"children_to_add" must be a list or a tuple!')
    return [children for children in map_children if children['type'] != 'CircleMarker'] + new_children

# --- MAP MODULE ---

def get_circle_markers(city: City, children: list[list]=None, fill_color: list | np.ndarray | str='blue', type_marker: str='circle_marker') -> list[dl.CircleMarker]:
    """
    Generate a list of CircleMarker objects representing locations on a map.

    Parameters
    ----------
    - city (City): An instance of the City class containing coordinates data.
    - children (list of lists, optional): Additional children elements to be included in each CircleMarker. Default is None.
    - fill_color (list, np.ndarray or str, optional): Fill color for the CircleMarker. Can be either a list of color values or a single color string. Default is 'blue'.
    - type_marker (str, optional): Type identifier for the markers. Default is 'circle_marker'.

    Returns
    -------
    - list[dl.CircleMarker]: A list of CircleMarker objects, each representing a location on the map.

    Raises
    ------
    - ValueError: If the length of 'children' or 'fill_color' lists is not equal to the number of coordinates in 'city.df_coordinates'.
    """
    if children is not None and len(children) != len(city.df_coordinates):
        raise ValueError(f'The list must be the same length as df_coordinates! ({len(children)} vs {len(city.df_coordinates)})')
    if isinstance(fill_color, list) and len(fill_color) != len(city.df_coordinates):
        raise ValueError(f'The list must be the same length as df_coordinates! ({len(fill_color)} vs {len(city.df_coordinates)})')
    
    return [
        dl.CircleMarker(
            center=[row['latitude'], row['longitude']],
            children=children[index] if children is not None else None,
            id={'type': type_marker, 'code_name': row['code_name'], 'index': index},
            radius=8,
            color='black',
            fill=True,
            fillColor=fill_color[index] if isinstance(fill_color, list) or isinstance(fill_color, np.ndarray) else fill_color,
            fillOpacity=0.85,
            stroke=True,
            weight=1,
            n_clicks=0
            
        ) for index, (_, row) in enumerate(city.df_coordinates.iterrows())
    ]

def get_edit_control() -> dl.FeatureGroup:
    """
    Generate an edit control for modifying features on a map.

    Returns
    -------
    - dl.FeatureGroup: A FeatureGroup containing an EditControl element.
    """
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
    """
    Generate a color bar for visualizing a color scale.

    Parameters
    ----------
    - colorbar_range (tuple[int]): A tuple specifying the range of values for the color bar.

    Returns
    -------
    - dl.Colorbar: A Colorbar component configured based on the provided parameters.
    """
    return dl.Colorbar(
        colorscale=['blue', 'yellow'],
        width=25,
        height=300,
        max=colorbar_range[1],
        min=colorbar_range[0],
        position='bottomleft',
        nTicks=5,
        id='colorbar'
    )

# --- CUSTOM MODULE ---

def get_metric_markers(city: City, metric_name: str, metrics: dict[str, dict[str, float]], type_marker: str) -> list[dl.CircleMarker]:
    """
    Generate CircleMarker objects representing locations on a map, with fill colors based on correlation values.

    Parameters
    ----------
    - city (City): An instance of the City class containing coordinates data.
    - metrics (dict[str, float]): A dictionary containing station names as keys and correlation values as values.
    - type_marker (str): Type identifier for the markers.

    Returns
    -------
    - list[dl.CircleMarker]: A list of CircleMarker objects, each representing a location on the map with a fill color
      based on the correlation value.
    """
    children, fill_color = [], []
    for station_name, metric in metrics.items():
        children.append([dl.Tooltip(f'{station_name}: {metric_name.upper()} {metric[metric_name]:.3f}')])
        fill_color.append(color.find_color_between(color.normalize_value(metric[metric_name], 0, 0.6)))

    return get_circle_markers(
        city=city,
        children=children,
        fill_color=fill_color,
        type_marker=type_marker
    )

def get_correlation_markers(city: City, correlations: dict[str, float], type_marker: str) -> list[dl.CircleMarker]:
    """
    Generate CircleMarker objects representing locations on a map, with fill colors based on correlation values.

    Parameters
    ----------
    - city (City): An instance of the City class containing coordinates data.
    - correlations (dict[str, float]): A dictionary containing station names as keys and correlation values as values.
    - type_marker (str): Type identifier for the markers.

    Returns
    -------
    - list[dl.CircleMarker]: A list of CircleMarker objects, each representing a location on the map with a fill color
      based on the correlation value.
    """
    children, fill_color = [], []
    for station_name, corr in correlations.items():
        children.append([dl.Tooltip(f'{station_name}: Corrélation {corr:.3f}')])
        fill_color.append(color.find_color_between(color.normalize_value(corr, -1, 1)))

    return get_circle_markers(
        city=city,
        children=children,
        fill_color=fill_color,
        type_marker=type_marker
    )

def get_acp_markers(city: City, pca_values: np.ndarray) -> list[dl.CircleMarker]:
    """
    Generate CircleMarker objects representing locations on a map, with fill colors based on PCA values.

    Parameters
    ----------
    - city (City): An instance of the City class containing coordinates data.
    - pca_values (np.ndarray): An array containing PCA values associated with each location.

    Returns
    -------
    - list[dl.CircleMarker]: A list of CircleMarker objects, each representing a location on the map with a fill color
      based on the PCA value.
    """
    children = [
        [dl.Tooltip(f"{row['code_name']}: {pca_values[index]:.3f}")]
        for index, (_, row) in enumerate(city.df_coordinates.iterrows())
    ]
    normalized_value: np.ndarray = color.normalize_value(pca_values)
    fill_color = np.vectorize(color.find_color_between)(normalized_value)
    
    return get_circle_markers(
        city=city,
        children=children,
        fill_color=fill_color
    )