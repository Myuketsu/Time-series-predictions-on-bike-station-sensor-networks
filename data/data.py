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

def calculate_correlations(city: City, selected_station: str):
    correlations = {}
    selected_station_data = city.df_hours[selected_station]
    
    for station in city.df_hours.columns:
        if station == selected_station:
            correlations[station] = 1
        correlation = selected_station_data.corr(city.df_hours[station])
        correlations[station] = correlation
    return correlations

def get_data_between_dates(city: City, date_range: list[str]):
    return city.df_hours[(city.df_hours['date'] >= pd.to_datetime(date_range[0])) & (city.df_hours['date'] < pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))]

def get_data_month(city: City):
    df=city.df_hours
    df.set_index('date', inplace=True)
    df_mean_by_month = df.groupby(df.index.month).mean()
    df_mean_by_month= df_mean_by_month.astype(str)
    return df_mean_by_month

def get_data_month_all(city: City):
    df = city.df_hours
    df.set_index('date', inplace=True)
    df_mean_by_month = df.groupby(df.index.month).mean()
    df_mean_by_month['mean_by_row'] = df_mean_by_month.mean(axis=1)
    df_mean_by_month = df_mean_by_month.astype(str)
    return df_mean_by_month['mean_by_row']

def get_data_mean_hour(city: City):
    df = city.df_hours
    df.set_index('date', inplace=True)
    df_mean_by_hour = df.groupby(df.index.hour).mean()
    df_mean_by_hour['total_mean'] = df_mean_by_hour.mean(axis=1)
    return df_mean_by_hour

def check_if_station_in_polygon(city: City, geojson) -> list:
    polygon: shapely.Polygon = shapely.from_geojson(dumps(geojson)).geoms[-1]
    get_station_inside = city.df_coordinates.apply(lambda row: shapely.Point(row['longitude'], row['latitude']).within(polygon), axis=1)
    return city.df_coordinates[get_station_inside]['code_name'].to_list()

def get_acp(city: City) -> tuple:
    df = city.df_hours
    df.set_index('date', inplace=True)
    df = df.groupby(df.index.hour).mean()
    X_selected = df.copy().loc[:, ~df.columns.isin(['id', 'date'])]

    scaler = StandardScaler()
    X = scaler.fit_transform(X_selected)

    pca = PCA()
    X_pca = pca.fit_transform(X)
    
    feature_names = X_selected.columns.values

    return X_pca, pca, feature_names

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


def get_data_between_dates(city: City, date_range: list[str]) -> pd.DataFrame:
    return city.df_hours[
        (city.df_hours['date'] >= pd.to_datetime(date_range[0])) & (city.df_hours['date'] < pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))
    ]

def get_tsne_dataframe(df: pd.DataFrame) -> None:
    '''t-SNE (t-Distributed Stochastic Neighbor Embedding)'''
    X = df.copy().loc[:, ~df.columns.isin(['id', 'date'])]

    from sklearn.manifold import TSNE

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # --- TSNE 2D ---
    tsne = TSNE(n_components=2, init='pca', perplexity=15, random_state=0, n_jobs=-1)
    X_tsne = tsne.fit_transform(X)

    X_tsne = pd.DataFrame(X_tsne, index=df.index, columns=[f'Dim{i + 1}' for i in range(X_tsne.shape[1])])
    X_tsne['hue'] = df['date'].dt.month_name(locale='French')
    print(X_tsne.head())

    import matplotlib.pyplot as plt
    import seaborn as sns

    unique = X_tsne['hue'].unique()
    palette = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
    sns.scatterplot(X_tsne, x='Dim1', y='Dim2', hue='hue', palette=palette)
    plt.show()

    print(tsne.kl_divergence_)

    # --- TSNE 3D ---
    # tsne = TSNE(n_components=3, init='pca', perplexity=15, random_state=0, n_jobs=-1)
    # X_tsne = tsne.fit_transform(X)

    # X_tsne = pd.DataFrame(X_tsne, columns=[f'Dim{i + 1}' for i in range(X_tsne.shape[1])])
    # print(X_tsne.head())

    # import matplotlib.pyplot as plt

    # plt.figure(figsize=(10, 8))
    # ax = plt.axes(projection="3d")
    # ax.scatter3D(X_tsne.iloc[:, 0], X_tsne.iloc[:, 1], X_tsne.iloc[:, 2])
    # ax.set_xlabel(X_tsne.columns[0])
    # ax.set_ylabel(X_tsne.columns[1])
    # ax.set_zlabel(X_tsne.columns[2])
    # plt.show()

    # print(tsne.kl_divergence_)

    return

def compute_kde(df, station):
    x = np.linspace(0, 1, 200)
    kde = gaussian_kde(df[station])
    y = kde(x)
    return x , y