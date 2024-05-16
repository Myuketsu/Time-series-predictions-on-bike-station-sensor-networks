from dash import html, dcc, Input, Output, State
from dash import register_page, callback, no_update

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc

import data.data as data
import view.figures as figures
import data.prediction.methods as prediction_method
from data.prediction.prediction_setup import PredictSetup
from data.city.load_cities import CITY
