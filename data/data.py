import pandas as pd
import numpy as np
import shapely

from scipy.cluster import hierarchy
from scipy.spatial import distance
from scipy.stats import gaussian_kde

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from json import dumps

from data.city.load_cities import City


class PCAResults:
    def __init__(self, pca, feature_names, components):
        self.pca = pca
        self.feature_names = feature_names
        self.components = components


def get_correlation_on_selected_stations(city: City, columns: list[str], ordered: bool=False):
    """
    Compute the Pearson correlation coefficients between the data of selected stations in a City's DataFrame.

    Parameters
    ----------
    city : City
        An instance of the City class containing hourly data in 'df_hours'.
    columns : list[str]
        A list of station names whose data will be used for correlation calculation.
    ordered : bool, optional
        If True, the correlation matrix is ordered using hierarchical clustering (default is False).

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the Pearson correlation coefficients between the selected stations' data.
    """
    df_corr = city.df_hours[sorted(columns)].corr().round(3)

    if ordered:
        distance_matrix = distance.squareform(1 - df_corr.abs().values)
        linkage_matrix = hierarchy.linkage(distance_matrix, method='average')
        order = hierarchy.leaves_list(linkage_matrix)
        df_corr = df_corr.iloc[order, order]

    mask = np.zeros_like(df_corr, dtype=bool)
    mask[np.triu_indices_from(mask)] = True

    return df_corr.mask(mask)

def calculate_correlations(city: City, selected_station: str) -> dict[str, float]:
    """
    Calculate the Pearson correlation coefficients between the data of a selected station
    and all other stations in the city's DataFrame.

    Parameters
    ----------
    city : City
        An instance of the City class containing hourly data in 'df_hours'.
    selected_station : str
        The station name whose data will be used as the reference for correlation calculation.

    Returns
    -------
    dict[str, float]
        A dictionary where the keys are station names and the values are the correlation coefficients
        between the selected station's data and each respective station's data.
    """
    df = city.df_hours.drop(columns=['date'])
    return df.corrwith(df[selected_station]).to_dict()

def compute_kde(df : pd.DataFrame, station : str) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes the Kernel Density Estimation (KDE) of a station's data in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the data to compute the KDE from.

    station : str
        The name of the station to compute the KDE for.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        A tuple containing the x and y values of the KDE.
    """
    x = np.linspace(0, 1, 200)
    kde = gaussian_kde(df[station])
    y = kde(x)
    return x , y

def get_data_between_dates(city: City, date_range: list[str]) -> pd.DataFrame:
    """
    Extracts the hourly data from a City's DataFrame between two dates.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.

    date_range : list[str]
        A list containing two strings representing the start and end dates in the format 'MM-DD-YYYY'.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the hourly data between the two dates.
    """
    return city.df_hours[(city.df_hours['date'] >= pd.to_datetime(date_range[0])) & (city.df_hours['date'] < pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))]

def get_data_month(city: City) -> pd.DataFrame:
    """
    Computes the monthly average of hourly data for each station and an additional 
    average across all stations for each month in the City's dataset.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.

    Returns
    -------
    pd.DataFrame
        A DataFrame with each column representing the monthly average values for each station,
        and an additional column 'mean_by_row' representing the average across all stations 
        for each month. The DataFrame's rows are indexed by month (1 through 12).
    """
    df=city.df_hours
    df.set_index('date', inplace=True)
    df_mean_by_month = df.groupby(df.index.month).mean()
    df_mean_by_month['mean_by_row'] = df_mean_by_month.mean(axis=1)
    return df_mean_by_month.astype(str)

def get_data_mean_hour(city: City) -> pd.DataFrame: 
    """
    Computes the hourly average of data for each station and an additional average
    across all stations for each hour in the City's dataset.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.

    Returns
    -------
    pd.DataFrame
        A DataFrame with each column representing the hourly average values for each station,
        and an additional column 'total_mean' representing the average across all stations
        for each hour. The DataFrame's rows are indexed by hour (0 through 23).
    """
    df = city.df_hours
    df.set_index('date', inplace=True)
    df_mean_by_hour = df.groupby(df.index.hour).mean()
    df_mean_by_hour['total_mean'] = df_mean_by_hour.mean(axis=1)
    return df_mean_by_hour

def check_if_station_in_polygon(city: City, geojson) -> list:
    """
    Checks if stations are inside a given polygon defined by a GeoJSON object.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_coordinates' with station coordinates.

    geojson : dict
        A GeoJSON object representing a polygon.

    Returns
    -------
    list
        A list of station names that are inside the polygon.
    """
    polygon: shapely.Polygon = shapely.from_geojson(dumps(geojson)).geoms[-1]
    get_station_inside = city.df_coordinates.apply(lambda row: shapely.Point(row['longitude'], row['latitude']).within(polygon), axis=1)
    return city.df_coordinates[get_station_inside]['code_name'].to_list()

def get_acp(city: City, use_transposed: bool = False) -> PCAResults:
    """
    Performs Principal Component Analysis (PCA) on the hourly data of a city, either using the original
    data or the transposed data matrix.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.
    use_transposed : bool, optional
        If True, PCA is performed on the transposed data matrix (default is False). (Use transposed data to get the PCA of the hours instead of the stations)

    Returns
    -------
    PCAResults
        An object containing the PCA model, feature names, and the PCA components.
    """
    df = city.df_hours
    df.set_index('date', inplace=True)
    df_mean = df.groupby(df.index.hour).mean()

    if use_transposed:
        df_mean = df_mean.T

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_mean)

    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    return PCAResults(pca, df_mean.columns.values, X_pca)


def reconstruct_curve_from_pca(city: City, station: str, comp_num: int = 3) -> np.ndarray:
    """
    Reconstructs the original mean curve of a station from its PCA components.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.
    station : str
        The name of the station to reconstruct the curve for.

    Returns
    -------
    np.ndarray
        An array containing the reconstructed curve of the station.
    """
    ACP_station = get_acp(city, use_transposed=False)
    ACP_hours = get_acp(city, use_transposed=True)

    df = city.df_hours.set_index('date', inplace=False)
    df_mean = df.groupby(df.index.hour).mean()

    station_index = np.where(ACP_station.feature_names == station)[0][0]

    wi = ACP_hours.pca.components_[0:comp_num]

    ci = ACP_hours.pca.transform(df_mean.T)[station_index][0:comp_num]
    reconstructed_curve = ci @ wi 

    return reconstructed_curve

def get_shifted_date(date: str, hours: int) -> pd.Timestamp:
    return pd.to_datetime(date) + pd.DateOffset(hours=hours)

def get_interpolated_indices(serie: pd.Series, tolerance: float=1e-3, output_type: str='mask'):
    mask, current_mask = [], []
    for index in range(len(serie)):
        # Si < 2 éléments d'affilé de suite
        if len(current_mask) < 2:
            current_mask.append(serie.index.values[index])
            continue
        
        # On check si la différence est la même entre trois éléments d'affilé de suite
        if np.abs((serie.values[index - 2] - serie.values[index - 1]) - (serie.values[index - 1] - serie.values[index])) < tolerance:
            current_mask.append(serie.index.values[index])
            continue
        
        # Si la différence est constante et la longueur de l'interpolation < 24 heures
        if len(current_mask) < 24 and np.abs(serie.values[index - 2] - serie.values[index - 1]) < tolerance:
            current_mask = []

        if len(current_mask) > 2:
            mask.append(current_mask[1:-1])
        current_mask = [serie.index.values[index - 1], serie.index.values[index]]

    if output_type == 'mask':
        return serie[[index_mask for row in mask for index_mask in row]].index

    if output_type == 'list':
        return mask
    
    raise ValueError('The "output_type" value must be one of the following : "mask", "list".')


def compute_global_mse(city: City, prediction, true_value) -> float:
    """
    Compute the Mean of the Mean Squared Error (MSE) between the prediction and the true value for all stations.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.
    prediction : np.ndarray
        An array containing the predicted values.
    true_value : np.ndarray
        An array containing the true values.

    Returns
    -------
    float
        The Mean Squared Error between the prediction and the true value.
    """
    return ((prediction - true_value) ** 2).mean(axis=1).mean()

def compute_station_mse(city: City, prediction, true_value):
    """
    Compute the Mean Squared Error (MSE) between the prediction and the true value for each station.

    Parameters
    ----------
    city : City
        An instance of the City class containing the DataFrame 'df_hours' with hourly data.
    prediction : np.ndarray
        An array containing the predicted values.
    true_value : np.ndarray
        An array containing the true values.

    Returns
    -------
    pd.dataframe
        A DataFrame containing the Mean Squared Error between the prediction and the true value for each station.
    """
    return pd.DataFrame(((prediction - true_value) ** 2).mean(axis=1), index=city.df_hours.columns, columns=['MSE'])

def get_acp_dataframe(df: pd.DataFrame) -> None:
    X_selected = df.copy().loc[:, ~df.columns.isin(['id', 'date'])]

    scaler = StandardScaler()
    X = scaler.fit_transform(X_selected)

    pca = PCA()
    X_pca = pca.fit_transform(X)

    # --- VARIANCE EXPLIQUEE ---
    import matplotlib.pyplot as plt
    barPlotdf = pd.DataFrame({'composantes': ['comp' + str(i) for i in range(len(pca.explained_variance_ratio_))], 'ratio': pca.explained_variance_ratio_})
    ax = barPlotdf.plot.bar(x='composantes', y='ratio')

    for i in range(len(barPlotdf) - 1):
        ax.plot([barPlotdf.index[i], barPlotdf.index[i + 1]], [barPlotdf.ratio[i], barPlotdf.ratio[i + 1]], color='red', linewidth=1, marker='.')

    plt.title('Variance expliquée des composantes')
    plt.show()
    
    feature_names = X_selected.columns.values
    
    # --- CERCLE DE CORRELATION ---
    # Calcul des coordonnées des variables dans l'espace réduit
    components = pca.components_

    # Création du cercle de corrélation
    fig, ax = plt.subplots()
    circle = plt.Circle((0, 0), 1, fill=False, color='black')
    ax.add_artist(circle)
    ax.scatter(components[0, :], components[1, :], s=150, color='steelblue')

    # Ajout des noms des variables
    for i, feature in enumerate(feature_names):
        ax.annotate(feature, (components[0, i], components[1, i]), fontsize=12)

    # Ajout des lignes reliant les points aux axes
    arrow_length = 0.05
    for i in range(len(feature_names)):
        plt.arrow(0, 0, components[0, i] - arrow_length * components[1, i],
                components[1, i] + arrow_length * components[0, i],
                head_width=0.03, head_length=0.03, fc='steelblue', ec='steelblue')

    # Configuration du graphique
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.title('Cercle de corrélation sur l\'ensemble des stations')
    plt.show()

    # --- ACP 3D ---

    df_acp = pd.DataFrame(
        X_pca[:, :3],
        columns=[
            f'PC1 ({pca.explained_variance_ratio_[0] * 100:.2f}%)',
            f'PC2 ({pca.explained_variance_ratio_[1] * 100:.2f}%)',
            f'PC3 ({pca.explained_variance_ratio_[2] * 100:.2f}%)',
        ]
    )

    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection="3d")
    ax.scatter3D(df_acp.iloc[:, 0].to_list(), df_acp.iloc[:, 1].to_list(), df_acp.iloc[:, 2].to_list())
    ax.set_title('ACP sur les données')
    ax.set_xlabel(df_acp.columns[0])
    ax.set_ylabel(df_acp.columns[1])
    ax.set_zlabel(df_acp.columns[2])
    plt.show()
    
    # --- PLOT DES CONTRIBUTIONS DE W1 ET W2 ---
    plt.figure(figsize=(14, 7))

    # Plot pour w1
    plt.subplot(1, 2, 1)
    plt.plot(pca.components_[0], marker='o', linestyle='-', color='r')
    plt.xticks(ticks=range(len(feature_names)), labels=feature_names, rotation=90)
    plt.title('Contribution des caractéristiques à w1 (PC1)')
    plt.grid(True)

    # Plot pour w2
    plt.subplot(1, 2, 2)
    plt.plot(pca.components_[1], marker='o', linestyle='-', color='g')
    plt.xticks(ticks=range(len(feature_names)), labels=feature_names, rotation=90)
    plt.title('Contribution des caractéristiques à w2 (PC2)')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    return


