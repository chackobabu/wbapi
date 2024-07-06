import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import redis
import json

dash.register_page(__name__, name='DATA TABLE', path="/")
r = redis.Redis(host='localhost', port=6379, db=0)

def get_data():
    data = r.get('data')
    return json.loads(data) if data else {}

instructions = [html.H5("You are viewing the data as a table. Please choose between options available in top-right corner, and use the filters on the data.", style={"color":"darkblue"}),
                html.P("Click download to save the data-table in your system in .xlsx format. Click on the globe on top if you wish to extract another file.")]

layout = dbc.Container(
        [dcc.Store(id='trigger', data=True),
        html.Div(children=instructions),
        html.Div(id="rendered_layout_main"),
        html.P(),
        dbc.Row(dbc.Col(id="df_container", width=12, style={"overflow":"auto"})),
        html.P(),
        dcc.Store(id="dataview"),
        html.Div([dcc.Download(id="download_data_full"),
        dbc.Col(dbc.Button("Download", id="btn_full", class_name='btn-success'), width=1)]),
        html.P(),
        html.Div([
        html.P("*Income levels are as per the latest classification. The classifications are updated each year on July 1, based on the GNI per capita of the previous calendar year."),
        html.A(style={"padding-left":"5px"},children="read more",target="#", href="https://blogs.worldbank.org/en/opendata/world-bank-country-classifications-by-income-level-for-2024-2025#:~:text=The%20World%20Bank%20Group%20assigns,of%20the%20previous%20calendar%20year.")
        ], style={"display":"flex"})

        ])

@dash.callback(
    [Output('datastore', 'data'),
     Output("rendered_layout_main","children")],
    Input('trigger', 'data'),
    State('datastore', 'data')
)
def update_layout(triggered, data):
    if triggered and data is not None:  # if not the first loading, data is present in 'datastore', use that 
        df = pd.DataFrame(data)
    elif triggered:                     # if first loading, get data from redis and use that
        json_data = get_data()
        df = pd.DataFrame(json_data)
    
    # updating the dropdown filters with fields present in the data. persistence = True ensures they remain throughout the session. 
    country_dd = dcc.Dropdown(list(df['Country'].unique()), value= [], id="sel_countries", multi=True, placeholder="select countries...", persistence=True, persistence_type='session')
    series_dd = dcc.Dropdown(list(df['Series'].unique()), value=[], id="sel_series", multi=True, placeholder="select series...", persistence=True, persistence_type='session')
    region_dd = dcc.Dropdown(list(df['Region'].unique()), value=[], id="sel_region", multi=True, placeholder="select regions...", persistence=True, persistence_type='session')
    income_level_dd = dcc.Dropdown(list(df['Income Level'].unique()), value=[], id="sel_income_level", multi=True, placeholder="select income levels...", persistence=True, persistence_type='session')
    
    # updating the years slider with years present in the data
    years = [int(each) for each in list(df.filter(regex=r'\d{4}').columns)]
    
    # if there are multiple years, make a range slider, if not a simple slider. 
    if len(years) > 1:
        start, end, diff = years[0], years[-1], years[1]-years[0]

        if end - start < 5:
            marks = {i: str(i) for i in range(start,end+1, 1)}
        elif end - start > 5 and diff == 1:
            marks = {i: str(i) for i in range(start,end+1,5)}
        elif end - start > 5 and diff != 1:
            marks = {i: str(i) for i in range(start,end+1,diff)}
    
        slider = dcc.RangeSlider(start,end,diff,
                    marks= marks,
                    value=[start, end],
                    id='year_slider_dt',
                    updatemode='drag', persistence=True, persistence_type='session')
    else:
        slider = dcc.Slider(1960,2020,1,
                            marks={i: str(i) for i in range(1960,2020,5)},
                            value=years[0],
                            id='year_slider_dt',
                            updatemode='drag', disabled=True
                            )
        
    rendered_layout_main = [
        dbc.Row(
            [dbc.Label("Filter countries:", width=2),
            dbc.Label("Filter indicators:", width=6),
            dbc.Label("Filter regions:", width=2),
            dbc.Label("Filter income levels*:", width=2)]
            ),
        dbc.Row(
            [dbc.Col(country_dd, width=2),
            dbc.Col(series_dd, width=6),
            dbc.Col(region_dd, width=2),
            dbc.Col(income_level_dd, width=2)]
            ),
        dbc.Row(
            [dbc.Col(html.Label(html.H6("Select Year:")), width=2),\
            dbc.Col(slider, width=10)],
            style={"padding-top":"20px"})]
    
    return get_data(), rendered_layout_main
    
@dash.callback(
    [Output("df_container","children"),
     Output("dataview","data")],
    [Input('datastore', 'data'),
     Input("sel_countries","value"),
     Input("sel_series","value"),
     Input("sel_region","value"),
     Input("sel_income_level","value"),
     Input("year_slider_dt","value")])
def update_table(data, countries, series, region, inc_level, years):
    
    df = pd.DataFrame(data)
    
    years_df = list(df.filter(regex=r"\d{4}").columns)
    print(years)
    years = [str(y) for y in range(years[0], years[1]+1)]
    years = [y for y in years if y in years_df]
    
    countries = list(df['Country'].unique()) if countries == [] else countries
    series = list(df['Series'].unique()) if series == [] else series
    region = list(df['Region'].unique()) if region == [] else region
    inc_level = list(df['Income Level'].unique()) if inc_level == [] else inc_level
    
    _df = df.query(f'Country in {countries} and Series in {series} and Region in {region} and `Income Level` in {inc_level}').copy()
    _df = _df[['Country','Series','Region','Income Level'] + years].copy()
    
    view = _df.to_dict('records')
    _columns = [{"name": i, "id": i} for i in _df.columns]
    
    data_table =  dash_table.DataTable(
            id='datatable',
            data=_df.to_dict('records'),
            columns=_columns,
            sort_action="native",
            sort_mode="multi",
            selected_columns=[],
            page_current= 0,
            page_size= 15,
        )
    
    return data_table, view

@dash.callback(
    Output("download_data_full", "data"),
    Input("btn_full", "n_clicks"),
    State('dataview', 'data'),
    prevent_initial_call=True,
)
def func(n_clicks, data):
    df = pd.DataFrame(data)
    years = list(df.filter(regex=r"\d{4}").columns)
    df = df[['Country','Series','Region','Income Level'] + years].copy()
    return dcc.send_data_frame(df.to_excel, "wb_extract.xlsx", index=False)