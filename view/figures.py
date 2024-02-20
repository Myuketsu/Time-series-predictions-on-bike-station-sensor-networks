import plotly.express as px
import plotly.graph_objects as go

from data.city.load_cities import City

def bike_distrubution(city: City, station: str):
    return px.line(
        data_frame=city.df_hours,
        x='date',
        y=station,
        title=f"Distribution des vélos dans la station {station}",
        template="seaborn"
    )