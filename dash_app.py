from dash import Dash, dash_table
import pandas as pd

df = pd.read_csv('extract.csv')

dash_app = Dash(__name__)

dash_app.layout = dash_table.DataTable(df.to_dict('records'),\
                                columns=[{"name": i, "id": i} for i in df.columns])

if __name__ == '__main__':
    dash_app.run(debug=True)