from dash import Dash, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    "Column 1": ["Row 1", "Row 2", "Row 3"],
    "Column 2": ["Data 1", "Data 2", "Data 3"]
})

# Create the Dash app and specify the Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create the DataTable
table = dash_table.DataTable(
    data=df.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df.columns],
    filter_action='native',
    style_table={'height': '200px', 'width': '400px'},
    style_data={
        'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    }
)

# Define the layout of the Dash app
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Dash App with Bootstrap"), width={'size': 6, 'offset': 3}),
        style={"marginTop": 50, "marginBottom": 50}
    ),
    dbc.Row(
        dbc.Col(table, width=12)
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)