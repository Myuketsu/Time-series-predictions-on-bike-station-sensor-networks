from dash import html, dcc, Input, Output, State, callback
from dash import register_page
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from data.city.load_cities import CITY
import view.figures as figures
import view.map_factory as map_factory
from data import data

register_page(__name__, path='/acp', name='ACP', title='TER', order=4,
              category='Statistique Descriptive', icon='codicon:graph-scatter')

def layout():
    return html.Div(
        [
            create_switch(),  # Si switch on, index = 1, sinon index = 0
            html.Div(id='map_container'),
            create_tabs()
        ],
        id='acp_layout',
        style={'width': '100%'}
    )

def create_station_selector():
    station_options = [{'value': row['code_name'], 'label': row['code_name']} for index, row in CITY.df_coordinates.iterrows()]
    return dmc.Select(
        label="Select Station",
        data=station_options,
        value='00008-espace-saint-georges',  # Default value
        clearable=True,
        searchable=True,
        icon=DashIconify(icon='fluent:rename-16-regular'),
        id='station-selector'
    )

def create_component_selector():
    return dmc.NumberInput(
        id='component-num-selector',
        label="Select Number of Components",
        description="Number of components to show in the PCA plot",
        min=2,
        max=24,
        value=3,
        step=1
    )

def create_switch():
    return dmc.Switch(
        id='component-switch',
        offLabel=DashIconify(icon="charm:chart-line", width=20),
        onLabel=DashIconify(icon="charm:circle", width=20),
        checked=False,
        style={'position': 'absolute', 'top': 90, 'left': 10, 'zIndex': 1000},
        size='lg'
    )

def create_map(index: int):
    acp_map = map_factory.viewport_map(CITY, 'viewport_map_acp')

    ACP = data.get_acp(CITY)
    pca_values = ACP.pca.components_[index]

    map_factory.add_to_children(acp_map, [map_factory.get_colorbar((pca_values.min(), pca_values.max()))])
    map_factory.add_to_children(acp_map, map_factory.get_acp_markers(CITY, pca_values))
    return acp_map

def create_tabs():
    return dcc.Tabs(
        [
            dcc.Tab(label='Eigenvectors & Reconstructed Curve', children=[
                html.Div(
                    children=[
                        create_component_selector(),
                        create_station_selector(),
                        dcc.Graph(id='acp_plot'),
                        dcc.Graph(id='acp_reconstructed_curve')
                    ],
                    style={'textAlign': 'center'}
                )
            ]),
            dcc.Tab(label='Scree Plot', children=[
                html.Div(
                    children=[
                        dcc.Graph(id='acp_scree_plot')
                    ],
                    style={'textAlign': 'center'}
                )
            ]),
            dcc.Tab(label='Correlation Circle', children=[
                html.Div(
                    children=[
                        dcc.Graph(id='acp_correlation_circle')
                    ],
                    style={'textAlign': 'center'}
                )
            ])
        ],
        style={'width': '100%'}
    )

# --- CALLBACKS ---

@callback(
    Output('acp_scree_plot', 'figure'),
    Input('component-num-selector', 'value')
)
def update_scree_plot(num_components):
    ACP = data.get_acp(CITY, use_transposed=True)
    return figures.scree_plot(ACP)

@callback(
    Output('acp_plot', 'figure'),
    Input('component-num-selector', 'value')
)
def update_acp_plot(num_components):
    indices = list(range(num_components))
    return figures.acp_eigenvectors_plot(CITY, indices, use_transposed=True)

@callback(
    Output('acp_reconstructed_curve', 'figure'),
    Input('station-selector', 'value'),
    Input('component-num-selector', 'value')
)
def update_reconstructed_curve(station, comp_num):
    return figures.plot_reconstructed_curve(CITY, station, comp_num)

@callback(
    Output('map_container', 'children'),
    Input('component-switch', 'value')
)
def update_map(use_second_component):
    index = 1 if use_second_component else 0
    new_map = create_map(index)
    return html.Div(new_map)

@callback(
    Output('acp_correlation_circle', 'figure'),
    Input('component-num-selector', 'value')
)
def update_correlation_circle_plot(num_components):
    ACP = data.get_acp(CITY, use_transposed=True)
    return figures.correlation_circle_plot(ACP, ACP.feature_names)
