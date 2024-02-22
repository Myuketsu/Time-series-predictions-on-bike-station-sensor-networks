import dash_leaflet as dl
from data.city.load_cities import City

def get_markers(city: City, highlight=None) -> list[dl.Marker]:
    highlighted_icon_url = "https://www.vanuatubeachbar.com/wp-content/uploads/leaflet-maps-marker-icons/bicycle_shop.png"
    return [
        dl.Marker(
            position=[row['latitude'], row['longitude']],
            icon={"iconUrl": highlighted_icon_url} if row['code_name'] == highlight else None,
            children=[dl.Tooltip(row['code_name'])],
            id={"type": "marker", "code_name": row['code_name']},
        ) for _, row in city.df_coordinates.iterrows()
    ]


def viewport_map(city: City, id: str, highlight=None):
    return dl.Map(
        [
            dl.TileLayer(),  # OpenStreetMap par défaut
        ] + get_markers(city, highlight=highlight),
        center=city.centroid,
        bounds=city.bounds,
        maxBounds=city.bounds,
        zoomControl=False,
        scrollWheelZoom=True,
        dragging=True,
        attributionControl=False,
        doubleClickZoom=False,
        zoomSnap=0.3,
        minZoom=16 if highlight else 12.4,
        id=id
    )