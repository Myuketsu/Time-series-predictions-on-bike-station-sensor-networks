import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

from data.city.load_cities import City
from data.data import get_data_between_dates, compute_kde

def create_empty_graph(title: str=''):
    return px.line(None, title=title)

def bike_distrubution(city: City, station: str, date_range: list[str]):
    return px.line(
        data_frame=get_data_between_dates(city, date_range),
        x='date',
        y=station,
        title=f"Distribution des vélos dans la station {station}",
        template="seaborn"
    )

def bike_boxplot(city: City, station: str, date_range: list[str]):
    return px.box(
        data_frame=get_data_between_dates(city, date_range),
        x=station,
        title=f"Boîte à moustache de la station {station}",
        template="seaborn"
    )
  
def histogram(city: City, station: str, date_range: list[str]):
    df_filtered = get_data_between_dates(city, date_range)
    x, y = compute_kde(df_filtered, station)
    fig = px.histogram(
        df_filtered,
        x=station,
        nbins=int(1 / 0.05) - 1,
        title=f"Histogramme et densité de la station {station}",
        template="seaborn",
        histnorm='probability density',
        range_x=[0, 1],
        labels={"value": "Valeur"}
    )
    
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Densité', line=dict(color='firebrick', width=2)))
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