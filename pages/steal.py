from dash import html, register_page

register_page(__name__, path='/steal', name='Vélos Volés', title='TER', order=5,
              category='Prédictions', icon='mdi:location-off-outline')

def layout():
    return html.Div(
        [
            'cc'
        ],
    )