from dash import html, register_page

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions import Lottie

register_page(__name__, path='/', name='Menu', title='TER', order=1,
              category=None, icon=None)

def layout():
    return html.Div(
        [
            get_title(),
            get_authors(),
            dmc.Divider(
                size='md',
                id='home_divider'
            ),
            get_subject_title(),
            get_lottie()
        ],
        id='home_layout'
    )

def get_title():
    return html.Div(
        [
            'Projet d\'expertise en Statistique et Probabilités'
        ],
        id='home_title'
    )

def get_authors():
    return html.Div(
        [
            'Théo Lavandier, Alexandre Leys, Mathilde Tissandier'
        ],
        id='home_authors'
    )

def get_subject_title():
    return dmc.Paper(
        [
            dmc.Blockquote(
                'Apprentissage statistique dans un réseau de capteurs et application à la reconstruction de la dynamique temporelle de stations de vélos en libre service',
                cite='Contact : Jérémie Bigot - Université de Bordeaux',
                icon=DashIconify(icon='grommet-icons:bike', width=30),
                color='blue',
            )
        ],
        shadow='sm',
        p='lg',
        radius='lg',
        id='home_suject'
    )

def get_lottie():
    return Lottie(
        options=dict(
            loop=True,
            autoplay=True,
            rendererSettings=dict(
                preserveAspectRatio='xMidYMid slice')
        ),
        width='30%',
        url='./assets/lotties/cycle_route.json',
        isClickToPauseDisabled=True
    )