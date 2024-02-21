import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

from data.city.load_cities import City

def bike_distrubution(city: City, station: str):
    return px.line(
        data_frame=city.df_hours,
        x='date',
        y=station,
        title=f"Distribution des vélos dans la station {station}",
        template="seaborn"
    )

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

def bike_distrubution(station: str ="") -> px.line: 
    if station == "":
        return None
    fig = px.line(city.df_hours, x="id", y=station, title=f"Distribution des vélos dans la station {station}", template="seaborn")
    fig.update_layout(
        xaxis_title="Heure",
        yaxis_title="Ratio de vélos",
        font=dict(
            family="Arial",
            size=18,
            color="#7f7f7f"
        )
    )
    fig.update_traces(mode="lines")
    fig.update_layout(hovermode="x unified")
    return fig