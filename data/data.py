import pandas as pd
import numpy as np
import shapely

from scipy.cluster import hierarchy
from scipy.spatial import distance

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from json import dumps

from data.city.load_cities import City

def get_correlation_on_selected_stations(city: City, columns: list[str], ordered: bool=False):
    df_corr = city.df_hours[sorted(columns)].corr().round(3)

    if ordered:
        distance_matrix = distance.squareform(1 - df_corr.abs().values)
        linkage_matrix = hierarchy.linkage(distance_matrix, method='average')
        order = hierarchy.leaves_list(linkage_matrix)
        df_corr = df_corr.iloc[order, order]

    # Mask to matrix
    mask = np.zeros_like(df_corr, dtype=bool)
    mask[np.triu_indices_from(mask)] = True

    return df_corr.mask(mask)

def get_data_between_dates(city: City, date_range: list[str]):
    return city.df_hours[(city.df_hours['date'] >= pd.to_datetime(date_range[0])) & (city.df_hours['date'] < pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))]

def check_if_station_in_polygon(city: City, geojson) -> list:
    polygon: shapely.Polygon = shapely.from_geojson(dumps(geojson)).geoms[-1]
    get_station_inside = city.df_coordinates.apply(lambda row: shapely.Point(row['longitude'], row['latitude']).within(polygon), axis=1)
    return city.df_coordinates[get_station_inside]['code_name'].to_list()

def get_acp_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    X = df.copy().loc[:, df.columns != 'id']

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    pca = PCA(n_components=80)
    X_pca = pca.fit_transform(X)

    # --- VARIANCE EXPLIQUEE ---
    import matplotlib.pyplot as plt
    barPlotdf = pd.DataFrame({'composantes': ['comp' + str(i) for i in range(len(pca.explained_variance_ratio_))], 'ratio': pca.explained_variance_ratio_})
    ax = barPlotdf.plot.bar(x='composantes', y='ratio')

    for i in range(len(barPlotdf) - 1):
        ax.plot([barPlotdf.index[i], barPlotdf.index[i + 1]], [barPlotdf.ratio[i], barPlotdf.ratio[i + 1]], color='red', linewidth=1, marker='.')

    plt.title('Variance expliquée des composantes')
    plt.show()
    
    feature_names = df.columns.values
    
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

    return df_acp
def get_data_between_dates(city: City, date_range: list[str]):
    return city.df_hours[(city.df_hours['date'] >= pd.to_datetime(date_range[0])) & (city.df_hours['date'] < pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))]
