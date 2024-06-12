from dash import Dash, html, dash_table
import pandas as pd

import wbapi as wb
import random

class Dash():
    def _init__(self, server, name, url_base_path):
        self.dash_app = Dash(server=server, name=name, url_base_path=url_base_path)
        
    def show_df(self, data):
        self.dash_app.layout = [
                html.Div(children='My First App with Data'),
                dash_table.DataTable(data=data.to_dict('records'), page_size=10)
            ]
        return self.dash_app


# wbg = wb.wbapi("gender")

# topic = wbg.topics['id'].iloc[0]
# wbg.get_series(topic)
# wbg.get_economies()

# random_ind = random.sample(sorted(wbg.series['id']),k=5)
# random_econ = random.sample(sorted(wbg.economies.reset_index()['id']),k=5)

# wbg.get_dataframe(random_ind,random_econ)
# df = wbg.data

# # Initialize the app
# dash = Dash()

# # App layout
# dash.layout = [
#     html.Div(children='My First App with Data'),
#     dash_table.DataTable(data=df.to_dict('records'), page_size=10)
# ]
# # Run the app
# if __name__ == '__main__':
#     dash.run(debug=True, port=5000)