from dash import html, register_page

register_page(__name__, path='/acp', name='ACP', title='TER', order=4,
              category='Statistique Descriptive', icon='codicon:graph-scatter')

def layout():
    return html.Div(
        [
            'cc'
        ],
    )