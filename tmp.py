import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from mycolorpy import colorlist as mcp
from data.city.load_cities import City


DATE_RANGE = ('04-01-2016', '10-31-2016')

df = pd.read_csv(
    f'./data/city/Toulouse/X_hour_toulouse.csv',
    index_col=0
)
df['date'] = pd.date_range(*DATE_RANGE, freq='1h')[:len(df)]

df.set_index('date', inplace=True)
df_mean_by_hour = df.groupby(df.index.hour).mean()

from data.data import get_acp_dataframe, get_tsne_dataframe
get_acp_dataframe(df_mean_by_hour.T)

# get_tsne_dataframe(df)

# Calcul des moyennes par heure sur l'ensemble des stations
def get_forecasts_method_basic(city:City):
    mean_values = df.drop(columns=['date']).mean(axis=1)
    return mean_values

# Calcul de l'erreur par heure et par station
def calculate_hourly_station_errors(city:City):
    df = city.df_hours
    forecasts = get_forecasts_method_basic(df)
    errors = df.set_index('date') - forecasts
    return errors

# Calcul de la moyenne par heure sur l'ensemble des stations
def calculate_hourly_mean_across_stations(city:City):
    df = city.df_hours
    forecasts = get_forecasts_method_basic(df)
    mean_forecast = forecasts.mean(axis=1)
    mean_observed = df.set_index('date').mean(axis=1)
    error = mean_observed - mean_forecast
    return error

# Calcul des erreurs par jour
def calculate_daily_errors(city:City):
    df = city.df_hours
    forecasts = get_forecasts_method_basic(df)
    # Agrégation par jour
    df_daily = df.set_index('date').resample('D').mean()
    forecasts_daily = forecasts.resample('D').mean()
    errors = df_daily - forecasts_daily
    return errors

# Calcul des erreurs par semaine
def calculate_weekly_errors(city:City):
    df = city.df_hours
    forecasts = get_forecasts_method_basic(df)
    # Agrégation par semaine
    df_weekly = df.set_index('date').resample('W').mean()
    forecasts_weekly = forecasts.resample('W').mean()
    errors = df_weekly - forecasts_weekly
    return errors

def plot_predictions_vs_actual(city:City):
    df = city.df_hours
    forecasts = get_forecasts_method_basic(df)
    
    # Sélection des données observées pour un jour spécifique
    observed_data = df.set_index('date').loc['04-01-2016']
    
    # Création du graphique
    plt.figure(figsize=(10, 6))
    plt.plot(observed_data.index, observed_data.values, label='Vraies données', color='blue')
    plt.plot(observed_data.index, forecasts.loc['04-01-2016'], label='Données prédites', color='red')
    
    plt.title('Prévisions vs Vraies données pour le 1er avril 2016')
    plt.xlabel('Heure')
    plt.ylabel('Valeur')
    plt.legend()
    plt.grid(True)
    plt.show()

plot_predictions_vs_actual(City)