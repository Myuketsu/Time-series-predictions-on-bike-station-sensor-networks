import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import re

from data.city.load_cities import City
from data.data import get_data_between_dates, compute_kde, get_data_month,get_data_month_all

def create_empty_graph(title: str=''):
    return px.line(None, title=title)

def radar_chart_distribution(city: City, station: str):
    station_name = station.replace('-', ' ')
    station_name = re.sub(r'\d+', '', station_name)
    station_name = ' '.join(station_name.split())
    station_name = station_name.capitalize()
    data_station = get_data_month(city)
    data_station = data_station[station].reset_index()
    data_station.columns = ['Mois', 'Valeur']
    mois_noms = {1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'}
    data_station['Mois'] = data_station['Mois'].map(mois_noms)
    data_station['Valeur'] = pd.to_numeric(data_station['Valeur'], errors='coerce')  

    data_all = get_data_month_all(city)
    data_all = data_all.reset_index()
    data_all.columns = ['Mois', 'Valeur']
    data_all['Mois'] = data_all['Mois'].map(mois_noms)
    data_all['Valeur'] = pd.to_numeric(data_all['Valeur'], errors='coerce')  

    fig = px.line_polar(data_station, r='Valeur', theta='Mois', line_close=True,
                        range_r=[0,1], template="seaborn",
                        title=f'Radar Chart pour la station {station_name}')
    
    fig2 = px.line_polar(data_all, r='Valeur', theta='Mois', line_close=True,
                        range_r=[0,1], template="seaborn", color_discrete_sequence=['red'])
    for trace in fig2['data']:
        fig.add_trace(trace)

    fig.add_trace(
        go.Scatterpolar(
            r=data_all['Valeur'],
            theta=data_all['Mois'],
            mode='lines',
            name='Toutes les stations réunies',
            line=dict(color='red')  # Couleur de la ligne pour toutes les stations réunies
        )
    )

    fig.add_annotation(
        x=1, y=1,
        xref='paper', yref='paper',
        text=f'Station: {station_name}',
        showarrow=False
    )
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
    return px.line(
        data_frame=get_data_between_dates(city, date_range),
        x='date',
        y=station,
        title=f"Distribution des vélos dans la station : {station_name}",
        template="seaborn"
    )

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