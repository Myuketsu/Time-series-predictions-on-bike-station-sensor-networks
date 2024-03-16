import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import re

from data.city.load_cities import City
from data.data import get_data_between_dates, compute_kde, get_data

def create_empty_graph(title: str=''):
    return px.line(None, title=title)

def radar_chart_distribution(city: City, station: str):
    data = get_data(city)
    fig = px.line_polar(
        data_frame=data,
        theta=data.index,
        r=station,
        line_close=True,
        title=f"Distribution des vélos dans la station {station}",
        template="seaborn"
    )
    fig.update_traces(fill='toself')
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
    print(data)
    return fig


#def bike_distrubution(city: City, station: str, date_range: list[str]):
#    return px.line(
#        data_frame=get_data_between_dates(city, date_range),
#        x='date',
#        y=station,
#       title=f"Distribution des vélos dans la station {station}",
#        template="seaborn"
#    )

def bike_distrubution(city: City, station: str, date_range: list[str]):
    station_name = station.replace('-', ' ')
    station_name = re.sub(r'\d+', '', station_name)
    station_name = ' '.join(station_name.split())
    station_name = station_name.capitalize()
    
    # Obtenez les données de la station spécifique
    data = get_data(city)
    if station in data.columns:
        station_data = data[station]
    else:
        # Gérer le cas où la station spécifiée n'est pas présente dans les données
        raise ValueError(f"La station {station} n'est pas présente dans les données.")
    
    # Tracer le graphique
    fig = px.line(
        data_frame=station_data,
        x=station_data.index,  # Utilisez l'index comme axe x
        y=station_data.values,  # Utilisez les valeurs de la station comme axe y
        title=f"Distribution des vélos dans la station : {station_name}",
        template="seaborn"
    )
    return fig


#def bike_boxplot(city: City, station: str, date_range: list[str]):
#    return px.box(
#        data_frame=get_data_between_dates(city, date_range),
#        x=station,
#        title=f"Boîte à moustache de la station : {station}",
#        template="seaborn"
#   )

def bike_boxplot(city: City, station: str, date_range: list[str]):
    # Mettre une majuscule au début de la station
    station_name = station.replace('-', ' ')
    station_name = re.sub(r'\d+', '', station_name)
    station_name = ' '.join(station_name.split())
    station_name = station_name.capitalize()
    return px.box(
        data_frame=get_data_between_dates(city, date_range),
        x=station,
        title=f"Boîte à moustache de la station : {station_name}",
        template="seaborn"
    )
  
def histogram(city: City, station: str, date_range: list[str]):
    df_filtered = get_data_between_dates(city, date_range)
    x, y = compute_kde(df_filtered, station)
    station_name = station.replace('-', ' ')
    station_name = re.sub(r'\d+', '', station_name)
    station_name = ' '.join(station_name.split())
    station_name = station_name.capitalize()
    fig = px.histogram(
        df_filtered,
        x=station,
        nbins=int(1 / 0.05) - 1,
        title=f"Histogramme et densité de la station : {station_name}",
        template="seaborn",
        histnorm='probability density',
        range_x=[0, 1],
        labels={"value": "Valeur"}
    )
    
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Densité (KDE)', line=dict(color='firebrick', width=2)))
    fig.update_layout(
        xaxis_title="Valeur",
        yaxis_title="Densité de probabilité",
        legend_title="Légende"
    )
    return fig

def correlation_plot(df: pd.DataFrame):
    df_splited = df.T.columns.str.split('-', n=1, expand=True)
    codes_columns = df_splited.get_level_values(0)
    names = df_splited.get_level_values(1)
    
    names = [[[i, y] for i in names] for y in names]
    fig = go.Figure(
        data=go.Heatmap(
            z=df.T,
            x=codes_columns,
            y=codes_columns,
            customdata=names,
            hovertemplate=''+\
                '<b>Corrélation: %{z}</b><br>'+\
                '<b>Axe x:</b><br>'+\
                    '- Code: %{x}<br>'+\
                    '- Station: %{customdata[0]}<br>'+\
                '<b>Axe y:</b><br>'+\
                    '- Code: %{y}<br>'+\
                    '- Station: %{customdata[1]}',
            name='',
            zmax=1.0,
            zmin=-1.0,
            hoverongaps=False
        )
    )

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5)
    )
    return fig