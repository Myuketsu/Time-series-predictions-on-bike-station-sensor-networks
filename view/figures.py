import plotly.express as px
import plotly.graph_objects as go

from data.city.load_cities import CITIES

city = CITIES[1]

def bike_distrubution(station):
    fig = px.line(city.df_hours, x="id", y=station, title=f"Distribution des vélos dans la station {station}", template="seaborn")
    return fig