import plotly.express as px
import numpy as np

def normalize_value(value: float | list, min_value: float=None, max_value: float=None) -> float | np.ndarray:
    is_float = isinstance(value, float)
    value = np.array([value]).flatten()
    
    if min_value is None:
        min_value = np.min(value)

    if max_value is None:
        max_value = np.max(value)

    if not all(min_value <= value) and not all(value <= max_value):
        raise ValueError('La valeur doit être comprise entre ["min_value", "max_value"].')
    
    if is_float:
        return ((value - min_value) / (max_value - min_value))[0]
    return (value - min_value) / (max_value - min_value)

def find_color_between(value: float, lowcolor: tuple[float]=(0, 0, 255), highcolor: tuple[float]=(255, 255, 0)) -> str:
    if not 0 <= value <= 1:
        raise ValueError('La valeur doit être comprise entre [0, 1].')

    return '#%02x%02x%02x' % tuple(map(int, px.colors.find_intermediate_color(lowcolor, highcolor, value))) # to hex