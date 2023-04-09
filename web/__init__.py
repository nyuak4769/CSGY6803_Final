import flask
from flask import Flask, session, g, render_template
from flask_restx import Api
from flask import Blueprint
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False
csrf = CSRFProtect()
csrf.init_app(app)

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint,
          title='Vault as a Service API',
          version='1.0',
          description='A proof of concept vault service',
          )

from .views import events
from .views import secrets

app.register_blueprint(blueprint)
api.add_namespace(events.api)
api.add_namespace(secrets.api)

@app.route('/')
def do_redirect():
    return flask.redirect('/api/v1')
