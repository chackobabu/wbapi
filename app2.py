from flask import Flask, render_template, session, redirect, url_for, request, send_file, flash, g
import wbapi
import json  
import pandas as pd
import os
from flask_caching import Cache
import plotly
import regex as re

import plotly.graph_objects as go
# from plotly.subplots import make_subplots

app = Flask(__name__)
app.config['SECRET_KEY'] = "wbgapp"


@app.route('/', methods=['GET','POST'])
def dashboard():

    df = pd.read_csv("extract.csv")
    df = df.round(2)
    # df.fillna("-", inplace=True)
    
    pattern = re.compile(r'\d{4}')
    years_int = {each:int(pattern.findall(each)[0]) for each in df.filter(regex="\d{4}").columns}
    df.rename(years_int, axis=1, inplace=True)
    df.drop(['economy','series'], axis=1, inplace=True)
    df.set_index(['Country','Series'], inplace=True)
    
    df_html = df.to_html()
    df_html = re.sub('<th>', '<th class="sticky">', df_html)
    with open('file.html','w') as file:
        file.write(df_html)
    # print(df_html)
    return render_template("index.html", table=df_html)

if __name__ == "__main__":
    app.run(port=5001, debug=True)