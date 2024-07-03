import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import os

dashapp = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True, requests_pathname_prefix='/dashboard/')

navbar =dbc.NavbarSimple(
    [dbc.NavLink([html.Div(html.H6(page["name"]), className="ms-2")], href="/dashboard"+page["path"], active="exact") for page in dash.page_registry.values()],
    brand=html.Div([
        html.A(html.Img(src="static\img\image.png", style={"max-height": "40px", "max-width": "80px", "padding-right":"10px"}), href="/"),
        html.H2("World Bank Data Visualizer", style={"color":"black"}),
        ], style={"display": "flex", "alignItems": "center"}),
    brand_style={"fontSize":"2em"})

dashapp.layout = dbc.Container(
    [dcc.Store(id="datastore", storage_type="session"),
    dbc.Col(navbar),
    html.P(),
    dash.page_container], fluid=True)

if __name__ == '__main__':
    dashapp.run(debug=True)