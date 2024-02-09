from dash import html, register_page

register_page(__name__, path='/correlation', name='Correlation', title='TER', order=3,
              category='Statistique Descriptive', icon='arcticons:cpustats')

def layout():
    return html.Div(
        [
            'cc'
        ],
    )