import dash
from dash import dcc, html
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import redis
import json

import pandas as pd

dash.register_page(__name__, name='SCATTER PLOT', path='/scatter')

r = redis.Redis(host='localhost', port=6379, db=0)

def get_data():
    data = r.get('data')
    return json.loads(data) if data else {}

instructions = [html.H5("You are viewing the data as a scatter-plot. Please choose between options available in top-right corner, and use the filters on the data.", style={"color":"darkblue"}),
                html.P("Click the camera icon on the plot to save it in .png format. Click on the globe on top if you wish to extract another file.")]

layout = dbc.Container(
        [   dcc.Store(id='trigger', data=True),
            dcc.Store(id='trans_data'),
            html.Div(children=instructions),
            dbc.Row(id="input_container", className="row d-flex align-items-center justify-content-center"),
            dbc.Col(html.H4(id="title"), width=12,style={'color':'darkblue','textAlign':'center', 'padding-top':'15px'}),
            dbc.Col(dcc.Graph(id="scatter_plot"), width=12),
            dbc.Row(id="legend_container", justify='end'),
            dbc.Col(dcc.Graph(id="time_series")),
            html.P(),
            html.Div([
            html.P("*As per the latest classification. The classifications are updated each year on July 1, based on the GNI per capita of the previous calendar year."),
            html.A(children=" read more", href="https://blogs.worldbank.org/en/opendata/world-bank-country-classifications-by-income-level-for-2024-2025#:~:text=The%20World%20Bank%20Group%20assigns,of%20the%20previous%20calendar%20year.")
            ], style={"display":"flex"})
        ])

@dash.callback(
    [Output("input_container","children"),
    Output("legend_container","children"),
    Output("trans_data", 'data')],
    Input('trigger', 'data'),
    State('datastore', 'data')
)
def update_inputs(triggered, data):
    if triggered:  # if not the first loading, data is present in 'datastore', use that 
        df = pd.DataFrame(data)
        
    df = df.melt(id_vars=['Country', 'Region', 'Income Level','Series']).copy()
    df.rename({"variable":"Year"}, axis=1, inplace=True)
    years = list(df['Year'].unique())

    df = df.pivot(index=['Country','Region','Income Level','Year'], columns=['Series']).droplevel(0, axis=1).copy()
    df.rename_axis("", axis=1, inplace=True)
    df.reset_index(inplace=True)
    
    start, end, diff = int(years[0]), int(years[-1]), int(years[1])-int(years[0])

    slider = dcc.Slider(start,end,diff,
                marks={i: str(i) for i in range(start,end,5)},
                value=end-diff,
                id='year_slider_sc',
                updatemode='drag', included=False, persistence=True, persistence_type='session')
    
    ddOpts = list(df.set_index(['Country','Region','Income Level','Year']).columns)

    dropdown1 = dcc.Dropdown(ddOpts, ddOpts[0], id='x_axis', persistence=True, persistence_type='session')
    try:
        dropdown2 = dcc.Dropdown(ddOpts, ddOpts[1], id='y_axis', persistence=True, persistence_type='session')
    except IndexError:
        dropdown2 = dcc.Dropdown(ddOpts, ddOpts[0], id='y_axis', persistence=True, persistence_type='session')
        
    log_x_axis = dcc.Checklist(options=[{'label':'log', 'value':1}], id='log_x', persistence=True, persistence_type="session")
    log_y_axis = dcc.Checklist(options=[{'label':'log', 'value':1}], id='log_y',persistence=True, persistence_type='session')
    
    legend = dcc.RadioItems(options=[{'label':'Region', 'value':'Region'},\
                                    {'label':'Income Level', 'value':'Income Level'}],\
                                    value="Region",
                                    style={'display': 'flex','gap': '8px'}, id='legend', inline=True)
    
    legend_contianer = [dbc.Col(html.Label(html.H6("Choose Category to Compare:")), style={'color':'darkblue'}, width=2),
                    dbc.Col(legend, width=2)]
    
    inputs = [
            dbc.Col(html.Label(html.H6("Select Y:")), style={'color':'darkblue'}, width=1),
            dbc.Col(dropdown2, width=4),
            dbc.Col(log_y_axis, width=1),
            dbc.Col(html.Label(html.H6("Select X:")), style={'color':'darkblue'}, width=1),
            dbc.Col(dropdown1, width=4),
            dbc.Col(log_x_axis, width=1),
            html.P(),
            dbc.Col(html.Label(html.H6("Select Year:")), style={'color':'darkblue'}, width=1),
            dbc.Col(slider, width=11)
    
            ]
    return inputs, legend_contianer, df.to_dict('records')

@dash.callback(
    Output('title','children'),
    [Input('x_axis','value'),\
    Input('y_axis','value'),   
    Input('year_slider_sc', 'value')])
def update_title(x_axis, y_axis, year_slider_sc):
    return f"{y_axis} vs {x_axis} at year {year_slider_sc}"

@dash.callback(
            Output('scatter_plot', 'figure'),
            [Input('year_slider_sc', 'value'),\
            Input('x_axis','value'),\
            Input('y_axis','value'),\
            Input('log_x','value'),
            Input('log_y','value'),
            Input('legend','value')],
            State('trans_data', 'data'))
def update_scatter(year, x_axis,y_axis, log_x, log_y, legend, data):
    df = pd.DataFrame(data)
    
    df = df[df['Year'] == str(year)].copy()
    figure = px.scatter(
        df, x=x_axis, y=y_axis, 
        color=legend,
        hover_name='Country')
    if log_x and log_x[0] == 1:
        figure.update_xaxes(title = f"{x_axis} (log)", type='log')
        
    if log_y and log_y[0] == 1:
        figure.update_yaxes(title = f"{y_axis} (log)", type='log')

    figure.update_traces(marker_size=15, opacity=0.7)
    figure.update_layout(hovermode='closest')
    return figure

@dash.callback([Output('time_series', 'figure'),\
                Output('time_series', 'style')],
                [Input('x_axis','value'),
                Input('y_axis','value'),
                Input('scatter_plot','clickData'),
                Input('log_x','value'),
                Input('log_y','value')],
                State('trans_data', 'data'))
def get_hoverdata(x_axis,y_axis,clickData, log_x, log_y, data):
    df = pd.DataFrame(data)
    if clickData:
        country = clickData['points'][0]['hovertext']
    else:
        country = df['Country'].unique()[0]
        
    df = df.query(f'Country == "{country}"').copy()
            
    figure = make_subplots(rows=1, cols=2)

    figure.add_trace(
        go.Scatter(x=df['Year'], y=df[x_axis], mode='lines+markers', name="", hovertemplate='Year: %{x}<br>Value: %{y}'),
        row=1, col=1
    )

    figure.add_trace(
        go.Scatter(x=df['Year'], y=df[y_axis], mode='lines+markers', name="",hovertemplate='Year: %{x}<br>Value: %{y}'),
        row=1, col=2
    )
    years = df['Year'].unique()
    years = [int(y) for y in years]
    print(range(years[0],years[-1]))
    figure.update_layout(showlegend=False, title = {'text': f"Historic Trends in Chosen Variables in {country}"})
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(title_text=x_axis, row=1, col=1)
    figure.update_yaxes(title_text=y_axis, row=1, col=2)
    
    if log_x and log_x[0] == 1:
        figure.update_yaxes(title = f"{x_axis} (log)", type='log',row=1, col=1)
        
    if log_y and log_y[0] == 1:
        figure.update_yaxes(title = f"{y_axis} (log)", type='log',row=1, col=2)
    
    return figure, {"display":"block"}        
