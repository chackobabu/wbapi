import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import os

dashapp = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True, requests_pathname_prefix='/dashboard/')

navbar = dbc.NavbarSimple(
    [dbc.NavLink([html.Div(html.H6(page["name"]), className="ms-2")], href="/dashboard"+page["path"], active="exact") for page in dash.page_registry.values()],
    brand=html.Div([
        html.A(html.Img(src="static\img\image.png", style={"max-height": "40px", "max-width": "80px", "padding-right":"10px"}), href="/"),
        html.H2("World Bank Data Visualizer", style={"color":"black"}),
        ], style={"display": "flex", "alignItems": "center"}),
    brand_style={"fontSize":"2em"})


style_links = {"text-decoration": "none","font-weight": "500","color": "black", "padding-left": "0.1cm","padding-right": "0.1cm"}        

cpr = ["Made with ❤️ by ", html.A("Chacko Babu", style=style_links, href="https://chackobabu.github.io/")," using ",
        html.A("Flask",style=style_links, href="https://flask.palletsprojects.com/en/3.0.x/", target="_blank")," and ",
        html.A("Plotly-Dash",style=style_links, href="https://dash.plotly.com/", target="_blank")]

dashapp.layout = dbc.Container(
    [dcc.Store(id="datastore", storage_type="session"),
    dbc.Col(navbar, className="custom-background"),
    html.P(),
    dash.page_container,
    html.Div(children=cpr, style={'display': 'flex', 'justify-content': 'center', 'padding-top': '0.5cm'})], fluid=True)

if __name__ == '__main__':
    dashapp.run(debug=True)