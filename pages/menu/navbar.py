from dash import html, page_registry
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

CATEGORIES = {
    'Statistique Descriptive': 'material-symbols-light:query-stats'
}

def get_nav_link(name: str, path: str, icon: str):
    return dbc.DropdownMenuItem(
        children=html.Div(
            [
                dmc.ThemeIcon(
                    variant="light",
                    children=DashIconify(icon=icon)
                ),
                html.Div(name)
            ],
            className='navbar_link'
        ),
        href=path
    )

def get_navbar():
    category: dict[str, list] = {}
    for page in page_registry.values():
        if page.get('category') is None:
            continue
        
        if page.get('category') not in category.keys():
            category[page.get('category')] = []

        category[page.get('category')].append(
            get_nav_link(page.get('name'), page.get('path'), page.get('icon'))
        )
    
    nav = [
        dbc.DropdownMenu(
            children=child,
            nav=True,
            in_navbar=True,
            label=label,
            class_name='main_dropdown_navbar')
        for label, child in category.items()
    ]

    return dbc.NavbarSimple(
        children=nav,
        brand=html.Div(
            [
                dmc.ThemeIcon(
                    children=DashIconify(icon='material-symbols-light:pedal-bike-outline')
                ),
                html.Div('Stations de vélos')
            ],
            id='navbar_title'
        ),
        brand_href='/',
        color='primary',
        dark=True,
    )