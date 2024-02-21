import pandas as pd
import numpy as np

from scipy.cluster import hierarchy
from scipy.spatial import distance

from data.city.load_cities import City

def get_correlation_on_selected_stations(city: City, columns: list[str], ordered: bool=False):
    df_corr = city.df_hours[columns].corr().round(3)

    if ordered:
        distance_matrix = distance.squareform(1 - df_corr.abs().values)
        linkage_matrix = hierarchy.linkage(distance_matrix, method='average')
        order = hierarchy.leaves_list(linkage_matrix)
        df_corr = df_corr.iloc[order, order]

    # Mask to matrix
    mask = np.zeros_like(df_corr, dtype=bool)
    mask[np.triu_indices_from(mask)] = True

    return df_corr.mask(mask)

def get_data_between_dates(city: City, date_range: list[str]):
    return city.df_hours[(city.df_hours['date'] >= pd.to_datetime(date_range[0])) & (city.df_hours['date'] < pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))]