from dash import Dash, html, page_container
from dash_bootstrap_components import themes, icons
import dash_mantine_components as dmc

from pages.menu.navbar import get_navbar

app = Dash(
    __name__,
    use_pages=True,
    prevent_initial_callbacks=True,
    external_stylesheets=[themes.PULSE, icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = 'TER'
app._favicon = './pictures/bike_icon_2.svg'

app.layout = html.Div(
    [
        get_navbar(),
        html.Div(page_container.children, id='page_content'),
    ],
    id='layout'
)

if __name__ == '__main__':
    app.run(debug=True)