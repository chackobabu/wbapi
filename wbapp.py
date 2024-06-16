from flask import Flask, render_template, session, redirect, url_for, request, send_file, flash, g
import wbapi
import json  
import pandas as pd
import os
from flask_caching import Cache

import plotly
import regex as re

from dash import Dash, dash_table, html, dcc
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
# from plotly.subplots import make_subplots

app = Flask(__name__)
app.config['SECRET_KEY'] = "wbgapp"

app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = os.getenv('REDIS_HOST', 'localhost')
app.config['CACHE_REDIS_PORT'] = int(os.getenv('REDIS_PORT', 6379))
app.config['CACHE_REDIS_DB'] = int(os.getenv('REDIS_DB', 0))
app.config['CACHE_REDIS_PASSWORD'] = os.getenv('REDIS_PASSWORD', "c@che")
app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
# socketio = SocketIO(app)

cache = Cache(app)

@app.before_request
def before_request():
    g.wb = wbapi.wbapi()

@cache.cached()            
@app.route('/', methods=['GET','POST'])
def index():
    session.clear()
    topics_df = g.wb.search_topics()

    topics = [] 
    for i in topics_df.index:
        d = {}
        d['name'] = topics_df.loc[i,'value']
        d['id'] = topics_df.loc[i,'id']
        d['sourceNote'] = json.dumps(topics_df.loc[i,'sourceNote'])
        # print(d['sourceNote'])
        topics.append(d)
        
    if request.method == "POST":
        if 'selection' in request.form.keys():
            session['selected_id'] = request.form.getlist('selection')
            return redirect(url_for("select_series"))
        
    return render_template("select_db.html",\
                passed={'length':topics_df.shape[0], 'data':topics})

@cache.cached() 
@app.route('/select_series', methods=['GET','POST'])
def select_series():
    
    if len(session['selected_id']) > 0:
        series = []
        for id in session['selected_id']:
            series.append(g.wb.series(topic=id, db=None))
        series = pd.concat(series)
    else:
        series = g.wb.series()
    
    series.reset_index(inplace=True, drop=True)
    # print(series)
    
    series_data = []
    for i in series.index:  
        d = {}
        d['name'] = series.loc[i,'value']
        d['id'] = series.loc[i,'id']
        series_data.append(d)
        
    if request.method == "POST":
        if 'selected_series' in request.form.keys() and 'submit' in request.form.keys():
            session['selected_series'] = request.form.getlist('selected_series')
            return redirect(url_for("economies"))
        else:
            return render_template("select_series.html", series_data={'length':len(series_data),'data':series_data}, error="Please select one")
        
    return render_template("select_series.html", series_data={'length':len(series_data),'data':series_data})

@cache.cached() 
@app.route('/meta_data', methods=['GET','POST'])
def meta_data():

    series_id = request.args.get('id')
    id, name = series_id.split('@@@')
    try:
        if request.args.get('type') == 'series':
            metadata = g.wb.metaData_series(param=id).metadata
        elif request.args.get('type') == 'economy':
            metadata = g.wb.metaData_economy(param=id).metadata
    except:
        return render_template("meta_data.html", error=name)

    passed = []
    
    for key, value in zip(metadata.keys(), metadata.values()):
        data = {}
        data['keys'] = key
        data['value'] = value
        
        passed.append(data)
        
    return render_template("meta_data.html", passed=passed)

@cache.cached() 
@app.route('/economies', methods=['GET','POST'])
def economies():
    
    names = []
    chosen_ids = []
    
    for each in session['selected_series']:
        names.append(each.split('@@@')[1])
        chosen_ids.append(each.split('@@@')[0])
        
    print(names, chosen_ids)
    
    if len(names) == 1:
        session['series_name'] = names[0]
        
    economies = g.wb.economies().reset_index()
    
    econ_data = []
    
    for i in economies.index:
        d = {}
        d['name'] = economies.loc[i,'name']
        d['id'] = economies.loc[i,'id']
        d['region'] = economies.loc[i,'region']
        d['incLevel'] = economies.loc[i,'incomeLevel']       
        econ_data.append(d)
    
    regions = sorted(economies['region'].dropna().unique())
    inc_levels = ['Low income', 'Lower middle income','Upper middle income','High income','Not classified']

    if request.method == "POST":
        chosen_economies = request.form.getlist('selected_economies')
        start,end,period = request.form.get('start_year'),request.form.get('end_year'),request.form.get('period')
        
        if len(chosen_economies) == 0 and start>end:
            return render_template("economies.html",\
                                econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names},\
                                error=f"No economy selected. Timeseries {start} to {end} cannot be processed",\
                                selected_economies=chosen_economies)
        elif len(chosen_economies) == 0:
            return render_template("economies.html",\
                    econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names},\
                    error="No economy selected",\
                    selected_economies=chosen_economies)
        elif start>end:
            return render_template("economies.html",\
                econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names},\
                error=f"Timeseries {start} to {end} cannot be processed",\
                selected_economies=chosen_economies)
            
        else:
            session['economies'] = chosen_economies
            session['series'] = chosen_ids
            session['time'] = [int(each) for each in [start,end,period]]
            return redirect(url_for("dashboard"))

    return render_template("economies.html",\
        econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names})

dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/',external_stylesheets=[dbc.themes.BOOTSTRAP])
dash_app.layout = []

@cache.cached() 
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    
    # print(session['series'], session['economies'], session['time'])
    df = g.wb.get_dataframe(series =session['series'], economies=session['economies'], time=range(session['time'][0],session['time'][1]+1,session['time'][2]))
    # df.to_csv("extract.csv")
    df = df.round(2)

    
    pattern = re.compile(r'\d{4}')
    years_int = {each:int(pattern.findall(each)[0]) for each in df.filter(regex="\d{4}").columns}
    df.rename(years_int, axis=1, inplace=True)
    # print(list(years_int.values()))
    
    if session.get('series_name'):
        df['Series'] = session['series_name']
        # df = df[['Country','Series'] + list(years_int.values())].copy()
        
    with open('static/json/economies_dict.json','r') as file:
        economies_dict = json.loads(file.read())
    
    df['Region'] = df['Country'].apply(lambda name:economies_dict[name]['region'])
    df['Income Level'] = df['Country'].apply(lambda name:economies_dict[name]['incomeLevel'])
    
    df.reset_index(inplace=True)
    df = df[['Country','Series','Region','Income Level'] + list(years_int.values())].copy()
    print(df.head())
    df.to_csv("extract.csv")
    
    table = dash_table.DataTable(df.to_dict('records'),\
                                columns=[{"name": i, "id": i} for i in df.columns],\
                                        style_table={'height': 600,'overflowX':'auto', 'overflowY':'auto'},
                                        style_data={
                                            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
                                            'overflow': 'hidden',
                                            'textOverflow': 'ellipsis',
                                        },\
                                        style_as_list_view=True)

    dash_app.layout = []
    dash_app.layout.append(table)
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)