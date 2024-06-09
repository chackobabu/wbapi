from flask import Flask, render_template, session, redirect, url_for, request, send_file, flash
import wbapi

app = Flask(__name__)
app.config['SECRET_KEY'] = "wbgapp"
# socketio = SocketIO(app)
              
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        session['q'] = request.form['search_term']
        return redirect(url_for("select_db"))
    
    return render_template("search_db.html")

@app.route('/select_db', methods=['GET','POST'])
def select_db():

    wb = wbapi.wbapi(session['q'])
    session['q'] = wb.search_term_ret
    
    topics = wb.topics
    
    data = []
        
    for i in topics.index:
        d = {}
        d['name'] = topics.loc[i,'value']
        d['id'] = topics.loc[i,'id']
        data.append(d)
        
    if request.method == "POST":
        if 'selected_db' in request.form.keys():
            session['selected_db'] = request.form['selected_db'].split("|")[0]
            session['selected_db_name'] = request.form['selected_db'].split("|")[1]
            return redirect(url_for("select_series"))
        else:
            return render_template("select_db.html", error="Please select one", passed={'length':topics.shape[0], 'data':data})
        
    return render_template("select_db.html", passed={'length':topics.shape[0], 'data':data})

@app.route('/select_series', methods=['GET','POST'])
def select_series():

    wb = wbapi.wbapi(session['q'])
    topics = wb.topics
    
    topic = session['selected_db']
    print(topic)
    
    source_note = topics.query(f'id == "{topic}"')['sourceNote'].iloc[0]

    wb.get_series(sel_db=session['selected_db'])
    series = wb.series
    
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
            return render_template("select_series.html", series_data={'source_note':source_note,'length':len(series_data),'data':series_data}, error="Please select one")
        
    return render_template("select_series.html", series_data={'source_note':source_note,'length':len(series_data),'data':series_data})

@app.route('/meta_data', methods=['GET','POST'])
def meta_data():
    wb = wbapi.wbapi()
    series_id = request.args.get('id')
    id, name = series_id.split('@@@')
    try:
        if request.args.get('type') == 'series':
            wb.get_metaData_series(param=id)
            metadata = wb.meta_data_series.metadata
        elif request.args.get('type') == 'economy':
            wb.get_metaData_economy(param=id)
            metadata = wb.meta_data_economy.metadata
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
    for each in session['selected_series']:
        names.append(each.split('@@@')[1])
    print(names)
    
    wb = wbapi.wbapi()
    wb.get_economies()
    economies = wb.economies.reset_index()
    
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
        if len(chosen_economies) == 0:
            return render_template("economies.html",\
                                econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names},\
                                error="Please select one")
        else:
            pass
            
    return render_template("economies.html",\
        econ_data = {'econ_data':econ_data,'length':len(economies),'regions': regions,'income_levels': inc_levels, 'series':names})

if __name__ == "__main__":
    app.run(debug=True)