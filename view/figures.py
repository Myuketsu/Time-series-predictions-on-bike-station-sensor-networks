import plotly.express as px
import plotly.graph_objects as go

from data.city.load_cities import CITIES

city = CITIES[1]

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