import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import re

from data.city.load_cities import City
from data.data import get_data_between_dates, compute_kde, get_data_month, get_data_mean_hour, get_acp, reconstruct_curve_from_pca

def create_empty_graph(title: str='') -> go.Figure:
    return px.line(None, title=title)

def radar_chart_distribution(city: City, station: str) -> go.Figure:
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

    data_all = get_data_month(city)['mean_by_row']
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


def bike_distrubution(city: City, station: str, date_range: list[str]) -> go.Figure:
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
    
def bike_distrution_mean_hour(city: City, station: str) -> go.Figure:
    data = get_data_mean_hour(city)
    fig = px.line(
        data_frame=data,
        x=data.index,
        y=station,
        title=f"Distribution des vélos dans la station : {station}",
        template="seaborn",
    )
    fig.add_scatter(
        x=data.index, 
        y=data['total_mean'],
        mode='lines',
        name='Moyenne des stations',
    )
    fig.update_layout(
        xaxis_title="Heure",
        yaxis_title="Proportion de vélos disponibles",
        yaxis=dict(range=[0, 1]),
    )
    return fig


def bike_boxplot(city: City, station: str, date_range: list[str]) -> go.Figure:

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

def correlation_plot(df: pd.DataFrame) -> go.Figure:
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


def acp_eigenvectors_plot(city: City, indices: list[int], use_transposed=False) -> go.Figure:
    """
    Generates a plot showing the contribution of features to selected principal components from PCA,
    with the option to use transposed data.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.
    indices : list[int]
        List of indices representing the principal components to be plotted.
    use_transposed : bool, optional
        If True, PCA is performed on the transposed data matrix (default is False), and y-axis scale is set to [-1, 1].

    Returns
    -------
    go.Figure
        A Plotly figure illustrating the eigenvectors' contributions to the selected principal components.
    """
    ACP = get_acp(city, use_transposed=use_transposed)
    fig = go.Figure()

    colors = px.colors.qualitative.Plotly
    for i, index in enumerate(indices):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=ACP.feature_names,
            y=ACP.pca.components_[index],
            mode='lines+markers',
            name=f'Component {index + 1}',
            line=dict(color=color)
        ))

    fig.update_layout(
        title='Contribution of Features to Selected Principal Components',
        xaxis=dict(tickangle=90, title='Features'),
        yaxis_title="Contribution",
        showlegend=True,
        yaxis=dict(range=[-1, 1] if use_transposed else None) 
    )

    return fig

    
def plot_reconstructed_curve(city: City, station: str, comp_num: int = 3):
    """
    Generate a plot showing the original and reconstructed curves for a given station.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.
    station : str
        The station code for which the curve is to be reconstructed.

    Returns
    -------
    go.Figure
        A Plotly figure illustrating the original and reconstructed curves for the given station.
    """
    df = city.df_hours.set_index('date', inplace=False)
    original_curve = df.groupby(df.index.hour)[station].mean()
    reconstructed_curve = reconstruct_curve_from_pca(city, station, comp_num=comp_num)
    hours = list(range(24))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=original_curve,
        mode='lines',
        name='Original Curve',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=hours,
        y=reconstructed_curve,
        mode='lines',
        name='Reconstructed Curve',
        line=dict(color='red')
    ))
    fig.update_layout(
        title=f'Original and Reconstructed Curves for Station {station}',
        xaxis_title='Hour of the Day',
        yaxis_title='Values', 
        legend_title="Curve Type"
    )

    return fig

# --- PREDICTIONS ---

def interpolation_plot_analyzer(city: City, station: str, interpolated_indices: list[list[int]]) -> go.Figure:
    df = city.df_hours[station].copy().to_frame(name='Données originales')

    df['Sans interpolation'] = city.df_hours[station].copy()
    indices = [index for interpolated_slice in interpolated_indices for index in interpolated_slice]
    df.loc[indices, 'Sans interpolation'] = pd.NA

    df = df.set_index(city.df_hours['date'])

    fig = px.line(df)
    fig.update_layout(
        title=f'Mise en avant des {len(interpolated_indices)} interpolations de la station {station}',
        xaxis_title='Date',
        yaxis_title='Taux d\'occupation de la station (%)',
        legend_title='Traitement'
    )

    return fig

def main_graph_prediction(station_name: str, methods: list[pd.Series], reality_data: pd.Series) -> go.Figure:
    df_predict: pd.DataFrame = reality_data.copy().rename('Données réelles').to_frame()
    for serie in methods:
        df_predict = df_predict.join(serie)

    fig = px.line(
        data_frame=df_predict
    )

    fig.update_layout(
        title=f"Prédiction du {methods[0].index[0].strftime('%d-%m-%Y')} au {methods[0].index[-1].strftime('%d-%m-%Y')} de la station {station_name}",
        xaxis_title='Date',
        yaxis_title='Taux d\'occupation de la station (%)',
        legend_title='Entraînement <b>avec</b> interpolation',
        hovermode='x'
    )

    return fig