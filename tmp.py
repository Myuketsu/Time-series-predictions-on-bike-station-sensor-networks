import pandas as pd
import dash_leaflet as dl

from view.map_params import get_bounds

df = pd.read_csv('./data/city/Paris/coordinates_paris.csv')
print(df['latitude'].min())

print(get_bounds())