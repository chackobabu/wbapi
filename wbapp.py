from flask import Flask, render_template, session, redirect, url_for, request, send_file, flash, g
import wbapi
import json  
# from dash_app import dash

app = Flask(__name__)
app.config['SECRET_KEY'] = "wbgapp"
# socketio = SocketIO(app)

@app.before_request
def before_request():
    g.wb = wbapi.wbapi()
              
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        session['q'] = request.form['search_term']
        return redirect(url_for("select_db"))
    return render_template("search_db.html")

@app.route('/select_db', methods=['GET','POST'])
def select_db():
    topics_df = g.wb.search_topics(session['q'])
    session['q'] = g.wb.search_term_ret
    
    databases = g.wb.search_databases(session['q'])
    # print(databases)
    
    topics = [] 
    for i in topics_df.index:
        d = {}
        d['name'] = topics_df.loc[i,'value']
        d['id'] = topics_df.loc[i,'id']
        topics.append(d)
        
    dbs = []
    for i in databases.index:
        d = {}
        d['name'] = databases.loc[i,'name']
        d['id'] = databases.loc[i,'id']
        d['lastupdated'] = databases.loc[i,'lastupdated']
        d['dataavailability'] = databases.loc[i,'dataavailability']
        dbs.append(d)
        
    if request.method == "POST":
        if 'selection' in request.form.keys():
            
            type, selection = request.form['selection'].split("_")
            session['type'] = type

            session['selected_id'] = selection.split("|")[0]
            session['selected_name'] = selection.split("|")[1]
            
            if type == 't':
                topic = session['selected_id']
                session['source_note'] = topics_df.query(f'id == "{topic}"')['sourceNote'].iloc[0]
            else:
                session['source_note'] = ""
        
            return redirect(url_for("select_series"))
        
        else:
            session['type'] = 'all'
            return redirect(url_for("select_series"))
            # return render_template("select_db.html", error="Please select one",\
            #     passed={'length':topics_df.shape[0], 'data':topics},\
            #     passed_dbs={'length':databases.shape[0], 'data':dbs})
        
    return render_template("select_db.html",\
                passed={'length':topics_df.shape[0], 'data':topics})

@app.route('/select_series', methods=['GET','POST'])
def select_series():
    
    type = session['type']
     
    # print("\n\n",type,id)
    if type == "t":
        id = session['selected_id']
        series = g.wb.series(topic=id, db=None)
    elif type == "all":
        series = g.wb.series()
        
    print(series)
    
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
            return render_template("select_series.html", series_data={'source_note':session.get('source_note',''),'length':len(series_data),'data':series_data}, error="Please select one")
        
    return render_template("select_series.html", series_data={'source_note':session.get('source_note',''),'length':len(series_data),'data':series_data})

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

@app.route('/economies', methods=['GET','POST'])
def economies():
    
    names = []
    chosen_ids = []
    
    for each in session['selected_series']:
        names.append(each.split('@@@')[1])
        chosen_ids.append(each.split('@@@')[0])
    print(names, chosen_ids)
    
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
                                error=f"No economy selected. Timeseries {start} to {end} cannot be processed")
        elif len(chosen_economies) == 0:
            return render_template("economies.html",\
                    econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names},\
                    error="No economy selected")
        elif start>end:
            return render_template("economies.html",\
                econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names},\
                error=f"Timeseries {start} to {end} cannot be processed")
            
        else:
            session.clear()
            session['economies'] = chosen_economies
            session['series'] = chosen_ids
            session['time'] = [int(each) for each in [start,end,period]]
            return redirect(url_for("dashboard"))

    return render_template("economies.html",\
        econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names})

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    
    print(session['series'], session['economies'], session['time'])
    
    df = g.wb.get_dataframe(series =session['series'], economies=session['economies'], time=range(session['time'][0],session['time'][1],session['time'][2]))
    print(df)
    
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)