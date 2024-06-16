from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np

#  reading data - not required in the app
df = pd.read_csv('extract.csv')
df.drop('Unnamed: 0', axis=1, inplace=True)

df_wide = df.copy()
df = df.melt(id_vars=['Country', 'Region', 'Income Level','Series']).copy()
df.rename({"variable":"Year"}, axis=1, inplace=True)
df = df.pivot(index=['Country','Region','Income Level','Year'], columns=['Series']).droplevel(0, axis=1).copy()
df.rename_axis("", axis=1, inplace=True)
df.reset_index(inplace=True)
df_long = df.copy()
del df

dash_app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

years = df_wide.filter(regex=r'\d{4}').columns
print(years)

start, end, diff = int(years[0]), int(years[-1])+1, int(years[1])-int(years[0])

ddOpts = df_wide['Series'].unique()

slider = dcc.Slider(start,end,diff,
               marks={i: str(i) for i in range(start,end,5)},
               value=2020,
               id='year_slider',
               updatemode='drag')

dropdown1 = dcc.Dropdown(ddOpts, ddOpts[0], id='x_axis')
dropdown2 = dcc.Dropdown(ddOpts, ddOpts[1], id='y_axis')

log_x_axis = dcc.Checklist(options=[{'label':'log', 'value':1}], id='log_x')
log_y_axis = dcc.Checklist(options=[{'label':'log', 'value':1}], id='log_y')
legend = dcc.RadioItems(options=[{'label':'Region', 'value':'Region'},\
                                {'label':'Income Level', 'value':'Income Level'}],\
                                value="Region",
                                style={'display': 'flex','gap': '8px'}, id='legend', inline=True)

dash_app.layout = dbc.Container(
        [ 
            dbc.Row([
            dbc.Col(html.Label(html.H6("Select Y:")), style={'color':'darkblue'}, width=1),
            dbc.Col(dropdown2, width=4),
            dbc.Col(log_y_axis, width=1),
            dbc.Col(html.Label(html.H6("Select X:")), style={'color':'darkblue'}, width=1),
            dbc.Col(dropdown1, width=4),
            dbc.Col(log_x_axis, width=1),
            html.P(),
            html.P(),
            dbc.Col(html.Label(html.H6("Select Year:")), style={'color':'darkblue'}, width=1),
            dbc.Col(slider, width=10),
            dbc.Col(id="year_selected", width=1)
            ],className="row d-flex align-items-center justify-content-center"),
            dbc.Col(dcc.Graph(id="scatter_plot"), width=12),
            dbc.Row([
            dbc.Col(html.Label(html.H6("Choose Category to Compare:")), style={'color':'darkblue'}, width=2),
            dbc.Col(legend, width=2)])
        ]
)
@dash_app.callback(Output('year_selected','children'),
            [Input('year_slider', 'value')])
def update_output_div(year_slider):
    return f"Selection: {year_slider}"

@dash_app.callback(
            Output('scatter_plot', 'figure'),
            [Input('year_slider', 'value'),\
            Input('x_axis','value'),\
            Input('y_axis','value'),\
            Input('log_x','value'),
            Input('log_y','value'),
            Input('legend','value')])
def update_graph(year, x_axis,y_axis, log_x, log_y, legend):
    df = df_long.query(f'Year == "{year}"').copy()
    
    if log_x and log_x[0] == 1:
        df[x_axis] = np.log(df[x_axis])
        df.rename({x_axis:f"Log {x_axis}"},axis=1, inplace=True)
        x_axis = f"Log {x_axis}"
        
    if log_y and log_y[0] == 1:
        df[y_axis] = np.log(df[y_axis])
        df.rename({y_axis:f"Log {y_axis}"},axis=1, inplace=True)
        y_axis = f"Log {y_axis}"
            
    figure = px.scatter(
        df, x=x_axis, y=y_axis, 
        color=legend,
        hover_data=['Country'],\
            )
    figure.update_traces(marker_size=15, opacity=0.7)
    
    # traces = []
    # for each in df[legend].unique():
    #     _df = df.query(f'{legend} == "{each}"').copy()
    #     x = _df.query(f'series == "{x_axis}"')['value'].to_list()
    #     y = _df.query(f'series == "{y_axis}"')['value'].to_list()
    #     trace = go.Scatter(x=x, y=y, mode='markers',\
    #         opacity=0.7, marker={'size':15})
    #     traces.append(trace)

    # log_x, log_y = ('log' if log_x else None), ('log' if log_y else None)
        
    # layout = go.Layout(title=f'{y_axis} vs {x_axis}',\
    #     xaxis={'title':x_axis, 'type': log_x },\
    #     yaxis={'title':y_axis, 'type': log_y })
    
    # fig = {'data':traces,'layout':layout}
    return figure

# year_opts = [{'label':str(year), 'value':year for year in df_long['year'].unique}]
# print(year_opts)

if __name__ == '__main__':
    dash_app.run(debug=True, port=8686)