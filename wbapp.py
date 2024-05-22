from flask import Flask, render_template, session, redirect, url_for, request, send_file
from flask_socketio import SocketIO
import wbgcalls as api

import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = "wbgapp"
socketio = SocketIO(app)


@app.route('/index', methods=['GET','POST'])
def index():
    if request.method == "POST":
         search_term = request.form.search_term
         print(search_term)
    
    # wb = api.WbCall("gender")
    # data['']
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app=app, debug=True)


