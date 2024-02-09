from dash import html, register_page

register_page(__name__, path='/', name='Menu', title='TER', order=1,
              category=None, icon=None)

def layout():
    return html.Div(
        [
            'Page d\'accueil :)'
        ],
    )