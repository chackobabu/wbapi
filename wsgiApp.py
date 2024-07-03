from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound

from wbApp import app as app1
from dashApp import dashapp

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app1, {"/dashboard":dashapp.server})

if __name__ == "__main__":
    app.run(debug=True)